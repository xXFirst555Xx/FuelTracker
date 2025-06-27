"""add fuel prices table"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fuelprice",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("station", sa.String, nullable=False),
        sa.Column("fuel_type", sa.String, nullable=False),
        sa.Column("name_th", sa.String, nullable=False),
        sa.Column("price", sa.Numeric, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("fuelprice")
