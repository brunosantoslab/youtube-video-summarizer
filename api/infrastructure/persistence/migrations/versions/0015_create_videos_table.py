"""Create videos table

Revision ID: 0015_videos
Revises: 001_oauth_tokens
Create Date: 2025-04-26 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0015_videos'
down_revision = '001_oauth_tokens'  # Previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('youtube_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('channel_title', sa.String(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Interval(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('youtube_id', name='uq_videos_youtube_id')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_videos_youtube_id', 'videos', ['youtube_id'])
    op.create_index('ix_videos_channel_id', 'videos', ['channel_id'])
    op.create_index('ix_videos_status', 'videos', ['status'])


def downgrade() -> None:
    op.drop_index('ix_videos_status')
    op.drop_index('ix_videos_channel_id')
    op.drop_index('ix_videos_youtube_id')
    op.drop_table('videos')
