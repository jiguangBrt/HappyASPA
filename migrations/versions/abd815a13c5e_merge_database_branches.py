"""Merge database branches

Revision ID: abd815a13c5e
Revises: 52e85855a8ce, 751bfdb757ef
Create Date: 2026-03-30 00:54:47.591295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abd815a13c5e'
down_revision = ('52e85855a8ce', '751bfdb757ef')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
