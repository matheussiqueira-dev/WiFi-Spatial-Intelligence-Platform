"""Bounded operational log of alert webhook deliveries (no bodies, no secrets)."""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "webhook_deliveries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("event", sa.String(32), nullable=False),
        sa.Column("alert_code", sa.String(32), nullable=True),
        sa.Column("location", sa.String(48), nullable=True),
        sa.Column("delivered", sa.Boolean(), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("error", sa.String(32), nullable=True),
    )
    op.create_index("ix_webhook_deliveries_created_at", "webhook_deliveries", ["created_at"])


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
