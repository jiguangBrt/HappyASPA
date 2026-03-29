"""merge heads of branch

Revision ID: 20611f1e3851
Revises: 7ca8407d06b2, c43e16d45f52
Create Date: 2026-03-27 09:07:31.378726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20611f1e3851'
down_revision = ('7ca8407d06b2', 'c43e16d45f52')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
