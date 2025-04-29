"""
Integration tests for Summary Repository using TestContainers
Author: Bruno Santos
"""
import uuid
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from domain.models.summary import Summary, SummaryMetadata
from infrastructure.persistence.summary_entity import SummaryEntity
from infrastructure.persistence.video_entity import VideoEntity
from infrastructure.repositories.summary_repository import PostgresSummaryRepository


@pytest.mark.integration
class TestSummaryRepository:
    """Integration tests for SummaryRepository"""
    
    @pytest.fixture
    def summary_repository(self, db_session):
        """Create a summary repository with test database session"""
        return PostgresSummaryRepository(db_session)
    
    @pytest.fixture
    def test_video(self, db_session):
        """Create a test video in the database"""
        video_entity = VideoEntity(
            youtube_id = f"test_video_{uuid.uuid4().hex}",
            title="Test Video",
            description="Test description",
            channel_id="test_channel_id",
            channel_title="Test Channel",
            published_at=datetime.now() - timedelta(days=1),
            thumbnail_url="https://example.com/thumbnail.jpg",
            duration=timedelta(minutes=10)
        )
        db_session.add(video_entity)
        db_session.flush()
        return video_entity
    
    def test_create_summary(self, summary_repository, test_video, db_session):
        """Test creating a summary in the database"""

        # Create a summary metadata
        summaryMetadata = SummaryMetadata(
            processing_time=1.5,
            token_count=150,
            prompt_version="1.0",
            confidence_score=1,
            model_parameters=None
        )
        
        # Create a summary domain model
        summary = Summary(
            video_id=test_video.id,
            content="This is a test summary content",
            model_provider="openai",
            model_version="gpt-4",
            processing_metadata=summaryMetadata
        )
        
        # Save the summary
        created_summary = summary_repository.create(summary)
        
        # Force flush to the database
        db_session.flush()
        
        # Get the summary entity from the database
        stmt = select(SummaryEntity).where(SummaryEntity.video_id == test_video.id)
        result = db_session.execute(stmt).scalar_one()
        
        # Verify the summary was saved correctly
        assert result is not None
        assert result.video_id == test_video.id
        assert result.content == "This is a test summary content"
        assert result.model_provider == "openai"
        assert result.model_version == "gpt-4"
        assert result.processing_metadata["processing_time"] == 1.5
        assert result.processing_metadata["token_count"] == 150
        
        # Verify the domain object was updated with ID
        assert created_summary.id is not None
        assert isinstance(created_summary.id, uuid.UUID)
    
    def test_get_summary_by_id(self, summary_repository, test_video, db_session):
        """Test retrieving a summary by ID"""


        # Create a summary entity directly in the database
        summary_entity = SummaryEntity(
            video_id=test_video.id,
            content="This is another test summary",
            model_provider="google",
            model_version="gemini-pro",
            processing_metadata={
                "processing_time": 2.0,
                "token_count": 200,
                "prompt_version": "1.0",
                "confidence_score": 1,
                "model_parameters": None
            }
        )
        db_session.add(summary_entity)
        db_session.flush()
        
        # Get the summary by ID
        summary = summary_repository.get_by_id(summary_entity.id)
        
        # Verify the summary was retrieved correctly
        assert summary is not None
        assert summary.id == summary_entity.id
        assert summary.video_id == test_video.id
        assert summary.content == "This is another test summary"
        assert summary.model_provider == "google"
        assert summary.model_version == "gemini-pro"
        assert summary.processing_metadata.processing_time == 2.0
        assert summary.processing_metadata.token_count == 200
    
    def test_get_latest_by_video_id(self, summary_repository, test_video, db_session):
        """Test retrieving the latest summary for a video"""
 
        # Create multiple summary entities for the same video with different creation times
        old_summary = SummaryEntity(
            video_id=test_video.id,
            content="Old summary",
            model_provider="openai",
            model_version="gpt-3.5",
            date_created=datetime.now() - timedelta(hours=24),
            processing_metadata={
                "processing_time": 2.0,
                "token_count": 200,
                "prompt_version": "1.0",
                "confidence_score": 1,
                "model_parameters": None
            }
        )
        
        middle_summary = SummaryEntity(
            video_id=test_video.id,
            content="Middle summary",
            model_provider="openai",
            model_version="gpt-3.5",
            date_created=datetime.now() - timedelta(hours=12),
            processing_metadata={
                "processing_time": 2.0,
                "token_count": 200,
                "prompt_version": "1.0",
                "confidence_score": 1,
                "model_parameters": None
            }
        )
        
        latest_summary = SummaryEntity(
            video_id=test_video.id,
            content="Latest summary",
            model_provider="openai",
            model_version="gpt-4",
            date_created=datetime.now() - timedelta(hours=1),
            processing_metadata={
                "processing_time": 2.0,
                "token_count": 200,
                "prompt_version": "1.0",
                "confidence_score": 1,
                "model_parameters": None
            }
        )
        
        db_session.add_all([old_summary, middle_summary, latest_summary])
        db_session.flush()
        
        # Get the latest summary for the video
        summary = summary_repository.get_latest_by_video_id(test_video.id)
        
        # Verify the latest summary was retrieved
        assert summary is not None
        assert summary.id == latest_summary.id
        assert summary.content == "Latest summary"
        assert summary.model_version == "gpt-4"
        assert summary.processing_metadata.processing_time == 2.0
        assert summary.processing_metadata.token_count == 200
    
    def test_get_all_by_video_id(self, summary_repository, test_video, db_session):
        """Test retrieving all summaries for a video"""
        # Create multiple summary entities for the same video
        summaries = [
            SummaryEntity(
                video_id=test_video.id,
                content=f"Summary {i}",
                model_provider="openai",
                model_version=f"gpt-{3+i}",
                processing_metadata={
                    "processing_time": 2.0,
                    "token_count": 200,
                    "prompt_version": "1.0",
                    "confidence_score": 1,
                    "model_parameters": None
                }
            )
            for i in range(3)
        ]
        
        for summary in summaries:
            db_session.add(summary)
        db_session.flush()
        
        # Get all summaries for the video
        all_summaries = summary_repository.get_all_by_video_id(test_video.id)
        
        # Verify we have at least 3 summaries (there might be more from other tests)
        assert len(all_summaries) >= 3
        
        # Verify our newly created summaries are in the result
        summary_contents = [s.content for s in all_summaries]
        assert "Summary 0" in summary_contents
        assert "Summary 1" in summary_contents
        assert "Summary 2" in summary_contents
    
    def test_update_summary(self, summary_repository, test_video, db_session):
        """Test updating a summary"""
        # Create a summary entity directly in the database
        summary_entity = SummaryEntity(
            video_id=test_video.id,
            content="Original content",
            model_provider="openai",
            model_version="gpt-4",
            processing_metadata = SummaryMetadata(
                processing_time=1.0,
                token_count=300,
                prompt_version="1.0",
                confidence_score=1,
                model_parameters=None
            ).to_dict()
        )
        db_session.add(summary_entity)
        db_session.flush()
        
        # Get the summary and update it
        summary = summary_repository.get_by_id(summary_entity.id)
        summary.content = "Updated content"
        summary.processing_metadata = SummaryMetadata(
                processing_time=1.0,
                token_count=300,
                prompt_version="1.0",
                confidence_score=1,
                model_parameters=None
            )
        
        # Update the summary
        updated_summary = summary_repository.update(summary)
        db_session.flush()
        
        # Verify the summary was updated in the database
        stmt = select(SummaryEntity).where(SummaryEntity.id == summary_entity.id)
        result = db_session.execute(stmt).scalar_one()
        
        assert result.content == "Updated content"
        
        # Verify the returned object is correct
        assert updated_summary.content == "Updated content"
    
    def test_delete_summary(self, summary_repository, test_video, db_session):
        """Test deleting a summary"""
        # Create a summary entity directly in the database
        summary_entity = SummaryEntity(
            video_id=test_video.id,
            content="Summary to delete",
            model_provider="openai",
            model_version="gpt-4",
            processing_metadata = SummaryMetadata(
                processing_time=1.0,
                token_count=300,
                prompt_version="1.0",
                confidence_score=1,
                model_parameters=None
            ).to_dict()
        )
        db_session.add(summary_entity)
        db_session.flush()
        summary_id = summary_entity.id
        
        # Delete the summary
        result = summary_repository.delete(summary_id)
        db_session.flush()
        
        # Verify the summary was deleted
        assert result is True
        
        # Verify the summary is no longer in the database
        stmt = select(SummaryEntity).where(SummaryEntity.id == summary_id)
        result = db_session.execute(stmt).scalar_one_or_none()
        assert result is None
