"""fix nullable and default for total_* and permanent fields

Revision ID: 751bfdb757ef
Revises: 6830c5823ebd
Create Date: 2026-03-27 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '751bfdb757ef'
down_revision = '6830c5823ebd'
branch_labels = None
depends_on = None

def upgrade():
    # 1. 修复现有数据：将所有 NULL 值改为 0
    op.execute("UPDATE users SET total_correct_questions = 0 WHERE total_correct_questions IS NULL")
    op.execute("UPDATE users SET total_listening_duration = 0 WHERE total_listening_duration IS NULL")

    # 2. 可选：添加 NOT NULL 约束（SQLite 下会重建表，可能影响性能，但数据已无 NULL，理论上可以成功）
    #    如果你不想添加 NOT NULL，可以注释掉以下 with 块，依靠应用层空值保护即可。
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.alter_column('total_correct_questions',
    #            existing_type=sa.INTEGER(),
    #            nullable=False,
    #            existing_server_default=sa.text('0'))
    #     batch_op.alter_column('total_listening_duration',
    #            existing_type=sa.INTEGER(),
    #            nullable=False,
    #            existing_server_default=sa.text('0'))

def downgrade():
    # 回退操作：将非空列恢复为允许 NULL（但数据已变，不建议完全回滚）
    # 这里留空或根据实际需要编写
    pass