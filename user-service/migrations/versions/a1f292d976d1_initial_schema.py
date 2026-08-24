from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1f292d976d1"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("users",
    sa.Column("username", sa.String(length=50), nullable=False),
    sa.Column("email", sa.String(length=100), nullable=False),
    sa.Column("hashed_password", sa.String(length=200), nullable=False),
    sa.Column("theme", sa.String(length=10), nullable=False),
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table("provider_keys",
    sa.Column("user_id", sa.Uuid(), nullable=False),
    sa.Column("provider", sa.String(length=30), nullable=False),
    sa.Column("sealed_key", sa.String(length=500), nullable=False),
    sa.Column("salt", sa.String(length=50), nullable=False),
    sa.Column("hint", sa.String(length=8), nullable=False),
    sa.Column("monthly_limit_cents", sa.Integer(), nullable=True),
    sa.Column("spent_cents", sa.Integer(), nullable=False),
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("user_id", "provider", name="one_key_per_provider")
    )
    op.create_index(op.f("ix_provider_keys_user_id"), "provider_keys", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_provider_keys_user_id"), table_name="provider_keys")
    op.drop_table("provider_keys")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
