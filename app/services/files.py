import uuid
from pathlib import Path

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.files import File

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage"
TEXT_SUFFIXES = {".txt", ".md", ".markdown"}


def save_file(user_id, upload):
    original_name = secure_filename(upload.filename or "") or "upload"
    suffix = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    folder = STORAGE_ROOT / str(user_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / stored_name
    upload.save(path)

    content_text = None
    if suffix.lower() in TEXT_SUFFIXES:
        try:
            content_text = path.read_text(encoding="utf-8")
            content_error = None
        except UnicodeDecodeError:
            content_error = "Could not read this file as UTF-8 text."
        except OSError as error:
            content_error = f"Could not read this file: {error}"
    else:
        content_error = "This file type cannot be read yet."

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


def list_files(user_id):
    files = File.query.filter_by(user_id=user_id).all()
    return [record.to_dict() for record in files]


def get_file(user_id, file_id):
    file = File.query.filter_by(user_id=user_id, id=file_id).first()
    if file is None:
        return None
    return file.to_dict()
