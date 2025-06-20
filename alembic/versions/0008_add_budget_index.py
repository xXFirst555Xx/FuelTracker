"""add index on budget.vehicle_id"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_budget_vehicle_id", "budget", ["vehicle_id"])


def downgrade() -> None:
    op.drop_index("ix_budget_vehicle_id", table_name="budget")
