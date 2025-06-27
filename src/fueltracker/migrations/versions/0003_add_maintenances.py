"""add maintenances table"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "maintenance",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("due_odo", sa.Integer, nullable=True),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("note", sa.String, nullable=True),
        sa.Column("is_done", sa.Boolean, nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_table("maintenance")
