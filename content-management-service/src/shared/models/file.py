
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base
from shared.models.mixins import FolderContent


class File(FolderContent, Base):
    __tablename__: str = "files"

    extension: Mapped[str] = mapped_column(String, nullable=False)
    bookmarked_page: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
