from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

from app.extensions import db
from app.models.links import Link

MAX_BYTES = 1_000_000
SKIP_TAGS = {"script", "style", "noscript"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        text = " ".join(data.split())
        if text:
            self.parts.append(text)


def readable_text(html):
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return "\n".join(parser.parts).strip()


def fetch_link_text(url):
    parsed = urlparse(url or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None, "Only http and https links can be read."

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "SourceDesk"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return None, f"Could not fetch this link: {error}"

    if len(response.content) > MAX_BYTES:
        return None, "This page is too large to read."

    content_type = response.headers.get("Content-Type", "").lower()
    if content_type and "html" not in content_type and not content_type.startswith("text/"):
        return None, "This page is not readable text."

    body = response.text.strip()
    if "html" in content_type or body.lower().startswith("<!doctype html") or "<html" in body[:500].lower():
        try:
            body = readable_text(body)
        except Exception as error:
            return None, f"Could not read this page: {error}"

    if not body:
        return None, "This page has no readable text."
    return body, None


def create_link(user_id, url, title, notes):
    content_text, content_error = fetch_link_text(url)
    new_link = Link(
        user_id=user_id,
        url=url,
        title=title,
        notes=notes,
        content_text=content_text,
        content_error=content_error,
    )
    db.session.add(new_link)
    db.session.commit()
    return new_link.to_dict()

def delete_link(user_id, link_id):
    link = Link.query.filter_by(user_id=user_id, id=link_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        return True
    return False

def list_links(user_id):
    links = Link.query.filter_by(user_id=user_id).all()
    return [link.to_dict() for link in links]


def get_link(user_id, link_id):
    link = Link.query.filter_by(user_id=user_id, id=link_id).first()
    if link is None:
        return None
    return link.to_dict()
