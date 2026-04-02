"""Merge database branches

Revision ID: d82ad0d879b0
Revises: 074f10ff2d88, 8530d4d43976
Create Date: 2026-04-02 23:52:48.066323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd82ad0d879b0'
down_revision = ('074f10ff2d88', '8530d4d43976')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
