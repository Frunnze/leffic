from sqlalchemy.orm import Session

from shared.content_access import owned_content
from shared.models import File

_MISSING_FILE = "File does not exist!"


def owned_file(db: Session, user_id: str, file_id: str) -> File:
    return owned_content(db, user_id, File, file_id, _MISSING_FILE)
