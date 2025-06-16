"""add fuel_type to fuelentry"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "fuelentry",
        sa.Column("fuel_type", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("fuelentry", "fuel_type")
