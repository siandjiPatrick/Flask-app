"""add column profil-categorie 

Revision ID: ae1ae5324663
Revises: 9119f9466e16
Create Date: 2024-06-23 16:44:44.025441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae1ae5324663'
down_revision = '9119f9466e16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budget_categorie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_categorie', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budget_categorie', schema=None) as batch_op:
        batch_op.drop_column('profile_categorie')

    # ### end Alembic commands ###