"""user_lands: crop care counters for orchard harvest rarity

Revision ID: f4e8a1b9c0d2
Revises: 0a60f6b09075
Create Date: 2026-04-05

If `flask db upgrade` fails on down_revision, run `flask db heads` and set
`down_revision` below to your current head (or create a merge revision).
"""
from alembic import op
import sqlalchemy as sa


revision = 'f4e8a1b9c0d2'
down_revision = '0a60f6b09075'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user_lands', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('crop_water_count', sa.Integer(), nullable=False, server_default='0')
        )
        batch_op.add_column(
            sa.Column('crop_fertilizer_quality', sa.Float(), nullable=False, server_default='0.0')
        )


def downgrade():
    with op.batch_alter_table('user_lands', schema=None) as batch_op:
        batch_op.drop_column('crop_fertilizer_quality')
        batch_op.drop_column('crop_water_count')
