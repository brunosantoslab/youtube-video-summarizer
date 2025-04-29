"""Create summaries table

Revision ID: 004_summaries
Revises: 003_tasks
Create Date: 2025-04-26 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_summaries'
down_revision = '003_tasks'  # Após a tabela de tasks
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('processing_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_summaries_video_id', 'summaries', ['video_id'])
    op.create_index('ix_summaries_model_provider', 'summaries', ['model_provider'])
    
    # Create saved_summaries junction table for users to save summaries
    op.create_table(
        'saved_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('summaries.id'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['summary_id'], ['summaries.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'summary_id', name='uq_saved_summary_user_summary')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_saved_summaries_user_id', 'saved_summaries', ['user_id'])
    op.create_index('ix_saved_summaries_summary_id', 'saved_summaries', ['summary_id'])


def downgrade() -> None:
    op.drop_index('ix_saved_summaries_summary_id')
    op.drop_index('ix_saved_summaries_user_id')
    op.drop_table('saved_summaries')
    
    op.drop_index('ix_summaries_model_provider')
    op.drop_index('ix_summaries_video_id')
    op.drop_table('summaries')
