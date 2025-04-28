"""Create OAuth tokens table

Revision ID: 001_oauth_tokens
Revises: 
Create Date: 2025-04-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_oauth_tokens'
down_revision = '20250426001'  # Users table must exist first
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'oauth_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('token_type', sa.String(), nullable=False),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_oauth_token_user_provider')
    )
    
    # Create an index on user_id and provider for faster lookups
    op.create_index('ix_oauth_tokens_user_id_provider', 'oauth_tokens', ['user_id', 'provider'])
    
    # Create an index on provider for querying all tokens for a specific provider
    op.create_index('ix_oauth_tokens_provider', 'oauth_tokens', ['provider'])


def downgrade() -> None:
    op.drop_index('ix_oauth_tokens_provider')
    op.drop_index('ix_oauth_tokens_user_id_provider')
    op.drop_table('oauth_tokens')
