"""Straipsnio tekstas

Revision ID: 0853f6045e94
Revises: 9d3cac76d536
Create Date: 2022-08-31 14:32:32.980044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0853f6045e94'
down_revision = '9d3cac76d536'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('straipsniai', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Tekstas', sa.Text(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('straipsniai', schema=None) as batch_op:
        batch_op.drop_column('Tekstas')

    # ### end Alembic commands ###
