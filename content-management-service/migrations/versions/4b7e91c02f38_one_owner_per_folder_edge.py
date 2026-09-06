from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from shared.models.columns import FlexibleUuid

revision: str = "4b7e91c02f38"
down_revision: str | Sequence[str] | None = "8f2a41c9de17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OWNER_UNIQUENESS = "one_owner_per_folder"
_COMPOSITE_PARENT_KEY = "subfolder_shares_the_owner"
_OWNER_COLUMNS = ["id", "user_id"]
_PARENT_COLUMNS = ["parent_id", "user_id"]
_FOLDERS_TABLE = "folders"
_PARENT_INDEX = "ix_folders_parent_id"
_QUARANTINE_FOREIGN_PARENTS = sa.text("""
    UPDATE folders SET parent_id = NULL
    WHERE parent_id IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM folders AS parent
          WHERE parent.id = folders.parent_id
            AND parent.user_id = folders.user_id
      )
""")


def _folders_as_declared(*constraints: sa.Constraint) -> sa.Table:
    return sa.Table(
        _FOLDERS_TABLE,
        sa.MetaData(),
        sa.Column("parent_id", FlexibleUuid(), nullable=True),
        sa.Column("user_id", FlexibleUuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("public", sa.Boolean(), nullable=False),
        sa.Column("id", FlexibleUuid(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index(_PARENT_INDEX, "parent_id"),
        *constraints,
    )


def upgrade() -> None:
    op.execute(_QUARANTINE_FOREIGN_PARENTS)

    with op.batch_alter_table(
        _FOLDERS_TABLE, copy_from=_folders_as_declared()
    ) as batch:
        batch.create_unique_constraint(_OWNER_UNIQUENESS, _OWNER_COLUMNS)
        batch.create_foreign_key(
            _COMPOSITE_PARENT_KEY,
            _FOLDERS_TABLE,
            _PARENT_COLUMNS,
            _OWNER_COLUMNS,
        )


def downgrade() -> None:
    constrained = _folders_as_declared(
        sa.UniqueConstraint(*_OWNER_COLUMNS, name=_OWNER_UNIQUENESS),
        sa.ForeignKeyConstraint(
            _PARENT_COLUMNS,
            ["folders.id", "folders.user_id"],
            name=_COMPOSITE_PARENT_KEY,
        ),
    )

    with op.batch_alter_table(
        _FOLDERS_TABLE, copy_from=constrained
    ) as batch:
        batch.drop_constraint(_COMPOSITE_PARENT_KEY, type_="foreignkey")
        batch.drop_constraint(_OWNER_UNIQUENESS, type_="unique")
