"""add vendor fields to metadata

Revision ID: 7c4f2a9b1d6e
Revises: 6853757bdbf5
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c4f2a9b1d6e"
down_revision = "6853757bdbf5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "metadata",
        sa.Column(
            "vendor",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "metadata",
        sa.Column(
            "vendor_gstin",
            sa.String(length=20),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column(
        "metadata",
        "vendor_gstin",
    )

    op.drop_column(
        "metadata",
        "vendor",
    )
