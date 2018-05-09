"""empty message

Revision ID: f59f060e0503
Revises: f91da78fdc3b
Create Date: 2018-05-08 18:27:37.395004

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = 'f59f060e0503'
down_revision = 'f91da78fdc3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('idrs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('polygons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='POLYGON'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('polygons')
    op.drop_table('idrs')
    op.drop_table('sessions')
    # ### end Alembic commands ###