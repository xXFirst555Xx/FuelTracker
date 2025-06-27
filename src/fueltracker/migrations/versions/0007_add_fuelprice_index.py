"""add index on fuelprice(date, station, fuel_type)"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_fuelprice_date_station_fuel_type",
        "fuelprice",
        ["date", "station", "fuel_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fuelprice_date_station_fuel_type",
        table_name="fuelprice",
    )
