import io
import uuid
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.files import File

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage"
TEXT_SUFFIXES = {".txt", ".md", ".markdown"}
UNREADABLE_YET = "This file type cannot be read yet."


def save_file(user_id, upload):
    original_name = secure_filename(upload.filename or "") or "upload"
    suffix = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    folder = STORAGE_ROOT / str(user_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / stored_name
    upload.save(path)

    content_text, content_error = read_saved_file(path, suffix)

    record = File(
        user_id=user_id,
        file_name=original_name,
        file_path=str(path.relative_to(STORAGE_ROOT.parent)),
        file_type=upload.mimetype or "application/octet-stream",
        file_size=path.stat().st_size,
        content_text=content_text,
        content_error=content_error,
    )
    db.session.add(record)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        path.unlink(missing_ok=True)
        raise
    return record.to_dict()

def delete_file(user_id, file_id):
    file = File.query.filter_by(user_id=user_id, id=file_id).first()
    if file:
        db.session.delete(file)
        db.session.commit()
        path = STORAGE_ROOT.parent / file.file_path
        path.unlink(missing_ok=True)
        return True

    return False

def read_pdf(path):
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            return None, "This PDF is encrypted and cannot be read."
        parts = []
        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if text:
                parts.append(text)
    except (PdfReadError, OSError, ValueError) as error:
        return None, f"Could not read this PDF: {error}"
    if not parts:
        return None, "This PDF has no readable text."
    return "\n\n".join(parts), None

def _stored_pdf(user_id, file_id):
    record = File.query.filter_by(user_id=user_id, id=file_id).first()
    if record is None or not record.file_name.lower().endswith(".pdf"):
        return None
    path = STORAGE_ROOT.parent / record.file_path
    if not path.is_file():
        return None
    return path


def pdf_page_count(user_id, file_id):
    path = _stored_pdf(user_id, file_id)
    if path is None:
        return None
    pdf = pdfium.PdfDocument(str(path))
    try:
        return len(pdf)
    finally:
        pdf.close()


def render_pdf_page(user_id, file_id, page_index):
    path = _stored_pdf(user_id, file_id)
    if path is None:
        return None
    pdf = pdfium.PdfDocument(str(path))
    page = None
    bitmap = None
    try:
        if page_index < 0 or page_index >= len(pdf):
            return None
        page = pdf[page_index]
        bitmap = page.render(scale=1.5)
        image = bitmap.to_pil()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()
    finally:
        if bitmap is not None:
            bitmap.close()
        if page is not None:
            page.close()
        pdf.close()

def read_saved_file(path, suffix):
    suffix = suffix.lower()
    if suffix in TEXT_SUFFIXES:
        try:
            return path.read_text(encoding="utf-8"), None
        except UnicodeDecodeError:
            return None, "Could not read this file as UTF-8 text."
        except OSError as error:
            return None, f"Could not read this file: {error}"
    if suffix == ".pdf":
        return read_pdf(path)
    return None, UNREADABLE_YET


def refresh_unread_pdf(record):
    if record.content_text or record.content_error != UNREADABLE_YET:
        return
    if not record.file_name.lower().endswith(".pdf"):
        return
    path = STORAGE_ROOT.parent / record.file_path
    if not path.is_file():
        return
    record.content_text, record.content_error = read_pdf(path)
    db.session.commit()


def list_files(user_id):
    files = File.query.filter_by(user_id=user_id).all()
    for record in files:
        refresh_unread_pdf(record)
    return [record.to_dict() for record in files]


def get_file(user_id, file_id):
    file = File.query.filter_by(user_id=user_id, id=file_id).first()
    if file is None:
        return None
    refresh_unread_pdf(file)
    return file.to_dict()
