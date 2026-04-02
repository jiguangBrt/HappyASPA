"""merge conflicting heads

Revision ID: 18b75ff8509d
Revises: 27816c03fd13, bc2e7d7f9a11
Create Date: 2026-04-01 20:06:36.574653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18b75ff8509d'
down_revision = ('27816c03fd13', 'bc2e7d7f9a11')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
