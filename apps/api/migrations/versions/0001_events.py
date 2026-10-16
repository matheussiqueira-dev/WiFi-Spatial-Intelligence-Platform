"""Create synthetic event and audit storage; do not fabricate future module tables."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "sensing_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("event_id", sa.String(36), nullable=False, unique=True),
        sa.Column("timestamp", sa.String(40), nullable=False),
        sa.Column("evidence_level", sa.String(32), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
    )
    op.create_index("ix_sensing_events_timestamp", "sensing_events", ["timestamp"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("timestamp", sa.String(40), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
    )


def downgrade():
    op.drop_table("audit_events")
    op.drop_index("ix_sensing_events_timestamp", "sensing_events")
    op.drop_table("sensing_events")
