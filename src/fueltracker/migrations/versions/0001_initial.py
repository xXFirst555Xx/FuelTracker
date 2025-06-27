"""initial schema"""

from alembic import op
import sqlalchemy as sa


def _table_absent(table: str) -> bool:
    """Return True if the given table is not present in the database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table not in inspector.get_table_names()


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    if _table_absent("vehicle"):
        op.create_table(
            "vehicle",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String, nullable=False),
            sa.Column("vehicle_type", sa.String, nullable=False),
            sa.Column("license_plate", sa.String, nullable=False),
            sa.Column("tank_capacity_liters", sa.Float, nullable=False),
        )
    if _table_absent("fuelentry"):
        op.create_table(
            "fuelentry",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("entry_date", sa.Date, nullable=False),
            sa.Column("vehicle_id", sa.Integer, nullable=False),
            sa.Column("odo_before", sa.Float, nullable=False),
            sa.Column("odo_after", sa.Float, nullable=True),
            sa.Column("amount_spent", sa.Float, nullable=True),
            sa.Column("liters", sa.Float, nullable=True),
        )


def downgrade() -> None:
    if not _table_absent("fuelentry"):
        op.drop_table("fuelentry")
    if not _table_absent("vehicle"):
        op.drop_table("vehicle")
