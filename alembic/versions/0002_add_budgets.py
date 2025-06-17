"""add budgets table"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


# FIX: skip creation when table already exists
def upgrade() -> None:
    conn = op.get_bind()
    if "budget" not in sa.inspect(conn).get_table_names():
        op.create_table(
            "budget",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("vehicle_id", sa.Integer, nullable=False),
            sa.Column("amount", sa.Float, nullable=False),
        )


def downgrade() -> None:
    op.drop_table("budget")
