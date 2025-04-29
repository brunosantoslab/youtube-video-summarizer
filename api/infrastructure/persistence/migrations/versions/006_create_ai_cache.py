"""Create AI cache table

Revision ID: 006_ai_cache
Revises: 005_topics
Create Date: 2025-04-26 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_ai_cache'
down_revision = '005_topics'  # Após a tabela de topics
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cache_key', sa.String(), nullable=False),
        sa.Column('prompt_hash', sa.String(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ttl', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.Column('date_expires', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('cache_key', name='uq_ai_cache_cache_key')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_ai_cache_cache_key', 'ai_cache', ['cache_key'])
    op.create_index('ix_ai_cache_prompt_hash', 'ai_cache', ['prompt_hash'])
    op.create_index('ix_ai_cache_model_provider', 'ai_cache', ['model_provider'])
    op.create_index('ix_ai_cache_date_expires', 'ai_cache', ['date_expires'])

    # Create AI usage tracking table
    op.create_table(
        'ai_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('context', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('date', 'model_provider', 'model_version', 'user_id', 'context', name='uq_ai_usage_daily_per_model_user_context')
    )
    
    # Create indexes for faster lookups and reporting
    op.create_index('ix_ai_usage_date', 'ai_usage', ['date'])
    op.create_index('ix_ai_usage_user_id', 'ai_usage', ['user_id'])
    op.create_index('ix_ai_usage_model_provider', 'ai_usage', ['model_provider'])


def downgrade() -> None:
    op.drop_index('ix_ai_usage_model_provider')
    op.drop_index('ix_ai_usage_user_id')
    op.drop_index('ix_ai_usage_date')
    op.drop_table('ai_usage')
    
    op.drop_index('ix_ai_cache_date_expires')
    op.drop_index('ix_ai_cache_model_provider')
    op.drop_index('ix_ai_cache_prompt_hash')
    op.drop_index('ix_ai_cache_cache_key')
    op.drop_table('ai_cache')
