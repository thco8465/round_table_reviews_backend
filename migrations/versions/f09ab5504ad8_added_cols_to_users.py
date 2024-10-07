"""added cols to users

Revision ID: f09ab5504ad8
Revises: 69012a429d56
Create Date: 2024-10-01 10:40:00.153528

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f09ab5504ad8'
down_revision = '69012a429d56'  # Replace with the last revision ID
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to the Users table
    op.add_column('Users', sa.Column('createdAt', sa.TIMESTAMP(timezone=True), server_default=sa.func.current_timestamp(), nullable=True))
    op.add_column('Users', sa.Column('updatedAt', sa.TIMESTAMP(timezone=True), server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=True))
    op.add_column('Users', sa.Column('reviewCount', sa.Integer(), default=0, nullable=True))
    op.add_column('Users', sa.Column('exp', sa.Integer(), default=0, nullable=True))
    op.add_column('Users', sa.Column('level', sa.String(), nullable=True))

def downgrade():
    # Remove the added columns in case of a downgrade
    op.drop_column('Users', 'createdAt')
    op.drop_column('Users', 'updatedAt')
    op.drop_column('Users', 'reviewCount')
    op.drop_column('Users', 'exp')
    op.drop_column('Users', 'level')
