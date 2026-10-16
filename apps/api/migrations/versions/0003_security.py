"""Bounded aggregated denial counters; existing audit history is untouched."""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "security_denials",
        sa.Column("action", sa.String(64), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("first_seen", sa.String(40), nullable=False),
        sa.Column("last_seen", sa.String(40), nullable=False),
        sa.Column("correlation_id", sa.String(36), nullable=False),
    )


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
