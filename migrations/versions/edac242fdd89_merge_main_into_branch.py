"""merge main into branch

Revision ID: edac242fdd89
Revises: cbbdcec7114c, fb9fb72fb1e1
Create Date: 2026-04-09 10:50:38.614281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edac242fdd89'
down_revision = ('cbbdcec7114c', 'fb9fb72fb1e1')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
