"""Create topics table

Revision ID: 005_topics
Revises: 004_summaries
Create Date: 2025-04-26 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_topics'
down_revision = '004_summaries'  # Após a tabela de summaries
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('timestamp_start', sa.Float(), nullable=True),
        sa.Column('timestamp_end', sa.Float(), nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_modified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_topics_video_id', 'topics', ['video_id'])
    op.create_index('ix_topics_name', 'topics', ['name'])
    
    # Create full-text search index for topic name and description
    op.execute(
        """
        CREATE INDEX ix_topics_fts ON topics 
        USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX ix_topics_fts;")
    op.drop_index('ix_topics_name')
    op.drop_index('ix_topics_video_id')
    op.drop_table('topics')
