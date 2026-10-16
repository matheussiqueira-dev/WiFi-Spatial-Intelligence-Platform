"""Aggregated passive channel surveys (no SSID/BSSID), isolated from spatial data."""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "channel_surveys",
        sa.Column("survey_id", sa.String(36), primary_key=True),
        sa.Column("timestamp", sa.String(40), nullable=False),
        sa.Column("location", sa.String(48), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index("ix_channel_surveys_timestamp", "channel_surveys", ["timestamp"])
    op.create_index("ix_channel_surveys_location", "channel_surveys", ["location"])


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
