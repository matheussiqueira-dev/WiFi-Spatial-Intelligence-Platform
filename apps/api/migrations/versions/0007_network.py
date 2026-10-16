"""Measured host network telemetry, isolated from spatial simulation."""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "network_samples",
        sa.Column("sample_id", sa.String(36), primary_key=True),
        sa.Column("timestamp", sa.String(40), nullable=False),
        sa.Column("location", sa.String(48), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
    )
    op.create_index("ix_network_samples_timestamp", "network_samples", ["timestamp"])
    op.create_index("ix_network_samples_location", "network_samples", ["location"])
    op.create_table(
        "network_configuration",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location", sa.String(48), nullable=False),
    )


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
