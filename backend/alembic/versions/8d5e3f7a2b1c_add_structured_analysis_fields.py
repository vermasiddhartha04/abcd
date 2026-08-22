"""add structured analysis fields

Revision ID: 8d5e3f7a2b1c
Revises: 7c4f2a9b1d6e
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d5e3f7a2b1c"
down_revision = "7c4f2a9b1d6e"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "analysis",
        sa.Column(
            "demands",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "analysis",
        sa.Column(
            "penalty_proposals",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "analysis",
        sa.Column(
            "allegations",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade():

    op.drop_column(
        "analysis",
        "allegations",
    )

    op.drop_column(
        "analysis",
        "penalty_proposals",
    )

    op.drop_column(
        "analysis",
        "demands",
    )
