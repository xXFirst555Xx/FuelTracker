"""add budgets table"""

from alembic import op
import sqlalchemy as sa


def _table_absent(table: str) -> bool:
    """Return True if the given table is not present in the database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table not in inspector.get_table_names()


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if _table_absent("budget"):
        op.create_table(
            "budget",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("vehicle_id", sa.Integer, nullable=False),
            sa.Column("amount", sa.Float, nullable=False),
        )


def downgrade() -> None:
    if not _table_absent("budget"):
        op.drop_table("budget")
