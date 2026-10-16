"""Persist bounded synthetic experiment snapshots, separate from scene events."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "model_lab_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
    )


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
