from sqlalchemy import (
    Column, Integer, String, 
    ForeignKey, DateTime, Boolean, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid

from .database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    public = Column(Boolean, default=False, nullable=False)

    folder = relationship("Folder", remote_side=[id], back_populates="subfolders")
    subfolders = relationship("Folder", back_populates="folder", cascade="all, delete-orphan")

    files = relationship("File", backref="folder", cascade="all, delete-orphan")
    flashcard_decks = relationship("FlashcardDeck", backref="folder", cascade="all, delete-orphan")
    tests = relationship("Test", backref="folder", cascade="all, delete-orphan")
    notes = relationship("Note", backref="folder", cascade="all, delete-orphan")


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False)
    storage_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    public = Column(Boolean, default=False, nullable=False)


class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    public = Column(Boolean, default=False, nullable=False)

    flashcards = relationship("Flashcard", backref="deck", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, nullable=False)
    deck_id = Column(UUID(as_uuid=True), ForeignKey("flashcard_decks.id"), nullable=False)
    type = Column(String, nullable=False)
    next_review = Column(DateTime, nullable=True)
    content = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    fsrs_card = Column(JSONB, nullable=True)
    future_ratings_time = Column(JSONB, nullable=True)

    flashcard_reviews = relationship("FlashcardReview", backref="flashcard", cascade="all, delete-orphan")


class FlashcardReview(Base):
    __tablename__ = "flashcard_reviews"

    id = Column(Integer, primary_key=True, nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    fsrs_review = Column(JSONB, nullable=False)
    # reviewed_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    # score = Column(Integer, nullable=False)
    # duration = Column(Float, nullable=True)


class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    public = Column(Boolean, default=False, nullable=False)

    test_items = relationship("TestItem", backref="test", cascade="all, delete-orphan")


class TestItem(Base):
    __tablename__ = "test_items"

    id = Column(Integer, primary_key=True, nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id"), nullable=False)
    content = Column(JSONB, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    test_item_reviews = relationship("TestItemReview", backref="test_item", cascade="all, delete-orphan")


class TestItemReview(Base):
    __tablename__ = "test_item_reviews"

    id = Column(Integer, primary_key=True, nullable=False)
    test_item_id = Column(Integer, ForeignKey("test_items.id"), nullable=False)
    reviewed_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    accuracy = Column(Float, nullable=False)
    duration = Column(Float, nullable=True)


class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=False)
    name = Column(String, nullable=False)
    content = Column(JSONB, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    public = Column(Boolean, default=False, nullable=False)