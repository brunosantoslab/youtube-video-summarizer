"""Create transcripts table

Revision ID: 002_transcripts
Revises: 001_oauth_tokens
Create Date: 2025-04-26 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_transcripts'
down_revision = '0015_videos'  # Previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('segments', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('processing_status', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_transcripts_video_id', 'transcripts', ['video_id'])
    op.create_index('ix_transcripts_language_code', 'transcripts', ['language_code'])
    op.create_index('ix_transcripts_processing_status', 'transcripts', ['processing_status'])


def downgrade() -> None:
    op.drop_index('ix_transcripts_processing_status')
    op.drop_index('ix_transcripts_language_code')
    op.drop_index('ix_transcripts_video_id')
    op.drop_table('transcripts')
