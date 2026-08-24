from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from shared.models.columns import FlexibleUuid

revision: str = "c750ff70652b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("folders",
    sa.Column("parent_id", FlexibleUuid(), nullable=True),
    sa.Column("user_id", FlexibleUuid(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("public", sa.Boolean(), nullable=False),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.ForeignKeyConstraint(["parent_id"], ["folders.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_folders_parent_id"), "folders", ["parent_id"], unique=False)
    op.create_table("test_sessions",
    sa.Column("origin_id", FlexibleUuid(), nullable=False),
    sa.Column("status", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("files",
    sa.Column("extension", sa.String(), nullable=False),
    sa.Column("bookmarked_page", sa.Integer(), nullable=True),
    sa.Column("folder_id", FlexibleUuid(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("public", sa.Boolean(), nullable=False),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.ForeignKeyConstraint(["folder_id"], ["folders.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("flashcard_decks",
    sa.Column("source_kind", sa.String(), nullable=True),
    sa.Column("source_reference", sa.String(), nullable=True),
    sa.Column("folder_id", FlexibleUuid(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("public", sa.Boolean(), nullable=False),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.ForeignKeyConstraint(["folder_id"], ["folders.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("notes",
    sa.Column("content", sa.String(), nullable=False),
    sa.Column("type", sa.String(), nullable=False),
    sa.Column("read", sa.Boolean(), nullable=False),
    sa.Column("source_kind", sa.String(), nullable=True),
    sa.Column("source_reference", sa.String(), nullable=True),
    sa.Column("folder_id", FlexibleUuid(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("public", sa.Boolean(), nullable=False),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.ForeignKeyConstraint(["folder_id"], ["folders.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("tests",
    sa.Column("source_kind", sa.String(), nullable=True),
    sa.Column("source_reference", sa.String(), nullable=True),
    sa.Column("folder_id", FlexibleUuid(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("public", sa.Boolean(), nullable=False),
    sa.Column("id", FlexibleUuid(), nullable=False),
    sa.ForeignKeyConstraint(["folder_id"], ["folders.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("flashcards",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("deck_id", FlexibleUuid(), nullable=False),
    sa.Column("type", sa.String(), nullable=False),
    sa.Column("next_review", sa.DateTime(), nullable=True),
    sa.Column("content", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("fsrs_card", sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(["deck_id"], ["flashcard_decks.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_flashcards_deck_id"), "flashcards", ["deck_id"], unique=False)
    op.create_index(op.f("ix_flashcards_next_review"), "flashcards", ["next_review"], unique=False)
    op.create_table("test_items",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("test_id", FlexibleUuid(), nullable=False),
    sa.Column("content", sa.JSON(), nullable=False),
    sa.Column("type", sa.String(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["test_id"], ["tests.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("flashcard_reviews",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("flashcard_id", sa.Integer(), nullable=False),
    sa.Column("fsrs_review", sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(["flashcard_id"], ["flashcards.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_table("test_item_reviews",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("test_session", FlexibleUuid(), nullable=False),
    sa.Column("test_item_id", sa.Integer(), nullable=False),
    sa.Column("reviewed_at", sa.DateTime(), nullable=True),
    sa.Column("accuracy", sa.Float(), nullable=False),
    sa.Column("answers", sa.JSON(), nullable=False),
    sa.Column("duration", sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(["test_item_id"], ["test_items.id"], ),
    sa.ForeignKeyConstraint(["test_session"], ["test_sessions.id"], ),
    sa.PrimaryKeyConstraint("id")
    )


def downgrade() -> None:
    op.drop_table("test_item_reviews")
    op.drop_table("flashcard_reviews")
    op.drop_table("test_items")
    op.drop_index(op.f("ix_flashcards_next_review"), table_name="flashcards")
    op.drop_index(op.f("ix_flashcards_deck_id"), table_name="flashcards")
    op.drop_table("flashcards")
    op.drop_table("tests")
    op.drop_table("notes")
    op.drop_table("flashcard_decks")
    op.drop_table("files")
    op.drop_table("test_sessions")
    op.drop_index(op.f("ix_folders_parent_id"), table_name="folders")
    op.drop_table("folders")
