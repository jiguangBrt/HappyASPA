"""merge different 4 heads

Revision ID: f788c507ed00
Revises: 2ef8029c5dc5, a872908ff3fe, d82ad0d879b0, ed819308236c
Create Date: 2026-04-03 10:52:45.190803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f788c507ed00'
down_revision = ('2ef8029c5dc5', 'a872908ff3fe', 'd82ad0d879b0', 'ed819308236c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
