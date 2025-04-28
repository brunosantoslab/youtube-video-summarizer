"""
Unit tests for the Summary Generation Service
Author: Bruno Santos
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.models.video import Video
from domain.models.transcript import Transcript, TranscriptSegment
from domain.models.summary import Summary
from application.services.summary_generation_service import SummaryGenerationService


@pytest.fixture
def mock_video_repository():
    repo = MagicMock()
    video = Video(
        id=uuid.uuid4(),
        youtube_id="test_video_id",
        title="Test Video",
        description="Test description"
    )
    repo.get_by_id.return_value = video
    return repo, video


@pytest.fixture
def mock_transcript_repository():
    repo = MagicMock()
    transcript = Transcript(
        id=uuid.uuid4(),
        video_id=uuid.uuid4(),
        content="This is a test transcript with some content for summarization.",
        segments=[
            TranscriptSegment(start_time=0.0, end_time=2.5, text="This is a test"),
            TranscriptSegment(start_time=2.5, end_time=5.0, text="transcript with some content"),
            TranscriptSegment(start_time=5.0, end_time=7.5, text="for summarization.")
        ]
    )
    repo.get_by_video_id.return_value = transcript
    return repo, transcript


@pytest.fixture
def mock_summary_repository():
    repo = MagicMock()
    
    # Mock create method
    def mock_create(summary):
        summary.id = uuid.uuid4()
        return summary
    
    repo.create.side_effect = mock_create
    repo.get_latest_by_video_id.return_value = None
    
    return repo


@pytest.fixture
def mock_ai_provider_client():
    client = AsyncMock()
    
    # Mock response from the AI provider
    ai_result = {
        "text": "This is a test summary of the video content.",
        "model": "gpt-4",
        "metadata": {
            "processing_time": 2.5,
            "token_count": 150,
            "prompt_version": "1.0",
            "model_parameters": {
                "temperature": 0.5,
                "max_tokens": 500
            }
        }
    }
    client.generate_summary.return_value = ai_result
    
    return client


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock()
    return publisher


@pytest.mark.asyncio
async def test_generate_summary(
    mock_video_repository, mock_transcript_repository, 
    mock_summary_repository, mock_ai_provider_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    transcript_repo, transcript = mock_transcript_repository
    
    # Update transcript to match the video id
    transcript.video_id = video.id
    
    service = SummaryGenerationService(
        video_repository=video_repo,
        transcript_repository=transcript_repo,
        summary_repository=mock_summary_repository,
        ai_provider_client=mock_ai_provider_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    summary = await service.generate_summary(video.id)
    
    # Assert
    assert summary is not None
    assert summary.video_id == video.id
    assert summary.content == "This is a test summary of the video content."
    assert summary.model_provider == "gpt"  # Extracted from "gpt-4"
    assert summary.model_version == "gpt-4"
    
    # Verify transcript was retrieved
    transcript_repo.get_by_video_id.assert_called_once_with(video.id)
    
    # Verify AI provider was called with optimized transcript
    mock_ai_provider_client.generate_summary.assert_called_once()
    # Check the transcript text was passed correctly
    call_args = mock_ai_provider_client.generate_summary.call_args[1]
    assert "transcript_text" in call_args
    assert "This is a test transcript with some content" in call_args["transcript_text"]
    
    # Verify summary was created in repository
    mock_summary_repository.create.assert_called_once()
    
    # Verify event was published
    mock_event_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_with_existing_summary(
    mock_video_repository, mock_transcript_repository, 
    mock_summary_repository, mock_ai_provider_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    transcript_repo, transcript = mock_transcript_repository
    
    # Create an existing summary
    existing_summary = Summary(
        id=uuid.uuid4(),
        video_id=video.id,
        content="Existing summary content",
        model_provider="openai",
        model_version="gpt-4"
    )
    mock_summary_repository.get_latest_by_video_id.return_value = existing_summary
    
    service = SummaryGenerationService(
        video_repository=video_repo,
        transcript_repository=transcript_repo,
        summary_repository=mock_summary_repository,
        ai_provider_client=mock_ai_provider_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    summary = await service.get_or_generate_summary(video.id)
    
    # Assert
    assert summary is not None
    assert summary.id == existing_summary.id
    assert summary.content == "Existing summary content"
    
    # Verify AI provider was NOT called (since summary already exists)
    mock_ai_provider_client.generate_summary.assert_not_called()
    
    # Verify repository create was NOT called (since summary already exists)
    mock_summary_repository.create.assert_not_called()
    
    # Verify event was NOT published (since summary already exists)
    mock_event_publisher.publish.assert_not_called()


@pytest.mark.asyncio
async def test_generate_summary_missing_transcript(
    mock_video_repository, mock_transcript_repository, 
    mock_summary_repository, mock_ai_provider_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    
    # Set up missing transcript
    transcript_repo, _ = mock_transcript_repository
    transcript_repo.get_by_video_id.return_value = None
    
    service = SummaryGenerationService(
        video_repository=video_repo,
        transcript_repository=transcript_repo,
        summary_repository=mock_summary_repository,
        ai_provider_client=mock_ai_provider_client,
        event_publisher=mock_event_publisher
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="No transcript found"):
        await service.generate_summary(video.id)
    
    # Verify AI provider was NOT called (due to missing transcript)
    mock_ai_provider_client.generate_summary.assert_not_called()


@pytest.mark.asyncio
async def test_generate_summary_ai_failure(
    mock_video_repository, mock_transcript_repository, 
    mock_summary_repository, mock_ai_provider_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    transcript_repo, transcript = mock_transcript_repository
    
    # Update transcript to match the video id
    transcript.video_id = video.id
    
    # Set up AI provider to fail
    mock_ai_provider_client.generate_summary.side_effect = Exception("AI provider error")
    
    service = SummaryGenerationService(
        video_repository=video_repo,
        transcript_repository=transcript_repo,
        summary_repository=mock_summary_repository,
        ai_provider_client=mock_ai_provider_client,
        event_publisher=mock_event_publisher
    )
    
    # Act & Assert
    with pytest.raises(Exception, match="AI provider error"):
        await service.generate_summary(video.id)
    
    # Verify failure event was published
    mock_event_publisher.publish.assert_called_once()
    call_args = mock_event_publisher.publish.call_args[0][0]
    assert call_args.event_type == "summary.failed"
    assert call_args.payload["video_id"] == str(video.id)
    assert "AI provider error" in call_args.payload["error"]
