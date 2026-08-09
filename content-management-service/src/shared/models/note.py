
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base
from shared.models.mixins import FolderContent


class Note(FolderContent, Base):
    __tablename__: str = "notes"

    content: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
