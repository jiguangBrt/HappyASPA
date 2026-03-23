"""Merge database branches

Revision ID: 3bc29812953b
Revises: 67f8affd089d, d5224d0d8122
Create Date: 2026-03-22 18:47:43.238520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bc29812953b'
down_revision = ('67f8affd089d', 'd5224d0d8122')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
