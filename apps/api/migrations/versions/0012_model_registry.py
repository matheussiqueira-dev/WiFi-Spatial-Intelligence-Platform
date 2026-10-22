"""Third-party model cards (metadata only; files are never uploaded or loaded)."""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "model_registry",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("payload", sa.Text(), nullable=False),
    )


def downgrade():
    raise RuntimeError("destructive downgrade is not supported")
