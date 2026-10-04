import uuid
from pathlib import Path

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.files import File

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage"


def save_file(user_id, upload):
    original_name = secure_filename(upload.filename or "") or "upload"
    suffix = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    folder = STORAGE_ROOT / str(user_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / stored_name
    upload.save(path)

    record = File(
        user_id=user_id,
        file_name=original_name,
        file_path=str(path.relative_to(STORAGE_ROOT.parent)),
        file_type=upload.mimetype or "application/octet-stream",
        file_size=path.stat().st_size,
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
