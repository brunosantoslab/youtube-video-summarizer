"""Rename metadata field to avoid SQLAlchemy reserved keyword

Revision ID: 202504260001
Revises: 20250425_create_oauth_tokens_table
Create Date: 2025-04-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '202504260001'
down_revision: Union[str, None] = '002_transcripts'  # Previous migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata column to transcript_metadata to avoid SQLAlchemy reserved keyword
    op.alter_column('transcripts', 'metadata', new_column_name='transcript_metadata')


def downgrade() -> None:
    # Rename back to metadata if needed
    op.alter_column('transcripts', 'transcript_metadata', new_column_name='metadata')
