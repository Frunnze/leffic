from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from shared.models.columns import FlexibleUuid

revision: str = "8f2a41c9de17"
down_revision: str | Sequence[str] | None = "c750ff70652b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CLEAR_REVIEWS = sa.text("DELETE FROM test_item_reviews")
_CLEAR_SESSIONS = sa.text("DELETE FROM test_sessions")


def upgrade() -> None:
    op.execute(_CLEAR_REVIEWS)
    op.execute(_CLEAR_SESSIONS)

    with op.batch_alter_table("test_sessions") as batch:
        batch.add_column(
            sa.Column("user_id", FlexibleUuid(), nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("test_sessions") as batch:
        batch.drop_column("user_id")
