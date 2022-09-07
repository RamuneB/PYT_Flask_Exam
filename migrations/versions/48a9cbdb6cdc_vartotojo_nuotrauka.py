"""Vartotojo nuotrauka

Revision ID: 48a9cbdb6cdc
Revises: 0853f6045e94
Create Date: 2022-08-31 18:40:15.366175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48a9cbdb6cdc'
down_revision = '0853f6045e94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vartotojas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nuotrauka', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vartotojas', schema=None) as batch_op:
        batch_op.drop_column('nuotrauka')

    # ### end Alembic commands ###
