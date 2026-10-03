from app.extensions import db
from app.models.links import Link


def create_link(user_id, url, title, notes):
    new_link = Link(user_id=user_id, url=url, title=title, notes=notes)
    db.session.add(new_link)
    db.session.commit()
    return new_link.to_dict()


def list_links(user_id):
    links = Link.query.filter_by(user_id=user_id).all()
    return [link.to_dict() for link in links]
