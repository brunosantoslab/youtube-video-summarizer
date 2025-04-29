"""Create processing tasks table

Revision ID: 003_tasks
Revises: 202504260001
Create Date: 2025-04-26 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_tasks'
down_revision = '202504260001'  # Após a renomeação do metadata
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'processing_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.Column('date_completed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_processing_tasks_video_id', 'processing_tasks', ['video_id'])
    op.create_index('ix_processing_tasks_task_type', 'processing_tasks', ['task_type'])
    op.create_index('ix_processing_tasks_status', 'processing_tasks', ['status'])
    op.create_index('ix_processing_tasks_next_retry_at', 'processing_tasks', ['next_retry_at'])


def downgrade() -> None:
    op.drop_index('ix_processing_tasks_next_retry_at')
    op.drop_index('ix_processing_tasks_status')
    op.drop_index('ix_processing_tasks_task_type')
    op.drop_index('ix_processing_tasks_video_id')
    op.drop_table('processing_tasks')
