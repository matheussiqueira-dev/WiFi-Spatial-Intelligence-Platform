"""Add replay segments and saved analytics without changing event payloads."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade():
    op.add_column("sensing_events", sa.Column("segment_id", sa.String(36), nullable=True))
    op.create_table(
        "analytics_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
    )
    op.create_index("ix_sensing_events_segment_id", "sensing_events", ["segment_id"])


def downgrade():
    op.drop_table("analytics_reports")
    op.drop_index("ix_sensing_events_segment_id", "sensing_events")
    op.drop_column("sensing_events", "segment_id")
