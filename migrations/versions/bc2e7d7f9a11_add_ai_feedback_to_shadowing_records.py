"""add ai feedback to shadowing records

Revision ID: bc2e7d7f9a11
Revises: 440daf34526f
Create Date: 2026-04-01 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc2e7d7f9a11'
down_revision = '440daf34526f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_shadowing_records', sa.Column('ai_feedback', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('user_shadowing_records', 'ai_feedback')