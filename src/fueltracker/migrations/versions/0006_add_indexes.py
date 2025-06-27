"""add indexes to improve lookup speed"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_fuelentry_vehicle_id", "fuelentry", ["vehicle_id"])
    op.create_index("ix_fuelentry_entry_date", "fuelentry", ["entry_date"])
    op.create_index("ix_maintenance_vehicle_id", "maintenance", ["vehicle_id"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_vehicle_id", table_name="maintenance")
    op.drop_index("ix_fuelentry_entry_date", table_name="fuelentry")
    op.drop_index("ix_fuelentry_vehicle_id", table_name="fuelentry")
