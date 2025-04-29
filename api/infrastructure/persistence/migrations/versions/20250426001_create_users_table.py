"""Create users table

Revision ID: 20250426001_create_users_table
Revises: 
Create Date: 2025-04-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250426001'
down_revision = None  # Initial migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('youtube_user_id', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('youtube_user_id', name='uq_users_youtube_user_id')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_youtube_user_id', 'users', ['youtube_user_id'])


def downgrade() -> None:
    op.drop_index('ix_users_youtube_user_id')
    op.drop_index('ix_users_email')
    op.drop_table('users')
