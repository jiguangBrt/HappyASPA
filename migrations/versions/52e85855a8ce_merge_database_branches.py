"""Merge database branches

Revision ID: 52e85855a8ce
Revises: 9f2a6e3c1b7d, e8fa8a97fa62
Create Date: 2026-03-29 23:25:49.487058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52e85855a8ce'
down_revision = ('9f2a6e3c1b7d', 'e8fa8a97fa62')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
