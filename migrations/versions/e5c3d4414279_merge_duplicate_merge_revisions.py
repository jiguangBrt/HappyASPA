"""merge duplicate merge revisions

Revision ID: e5c3d4414279
Revises: 2ef8029c5dc5, d82ad0d879b0
Create Date: 2026-04-03 10:36:43.086563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5c3d4414279'
down_revision = ('2ef8029c5dc5', 'd82ad0d879b0')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
