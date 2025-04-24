# api/tests/unit/services/test_topic_extraction_service.py
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.models.video import Video
from domain.models.summary import Summary
from domain.models.transcript import Transcript, TranscriptSegment
from domain.models.topic import Topic
from application.services.topic_extraction_service import TopicExtractionService


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
def mock_summary_repository():
    repo = MagicMock()
    summary = Summary(
        id=uuid.uuid4(),
        video_id=uuid.uuid4(),
        content="This is a test summary about artificial intelligence, machine learning, and neural networks.",
        model_provider="openai",
        model_version="gpt-4"
    )
    repo.get_by_id.return_value = summary
    return repo, summary


@pytest.fixture
def mock_transcript_repository():
    repo = MagicMock()
    transcript = Transcript(
        id=uuid.uuid4(),
        video_id=uuid.uuid4(),
        content="This is a test transcript that talks about artificial intelligence in the beginning, then discusses machine learning techniques, and finally introduces neural networks.",
        segments=[
            TranscriptSegment(start_time=0.0, end_time=10.0, text="This is a test transcript that talks about artificial intelligence"),
            TranscriptSegment(start_time=10.0, end_time=20.0, text="in the beginning, then discusses machine learning techniques"),
            TranscriptSegment(start_time=20.0, end_time=30.0, text="and finally introduces neural networks.")
        ]
    )
    repo.get_by_video_id.return_value = transcript
    return repo, transcript


@pytest.fixture
def mock_topic_repository():
    repo = MagicMock()
    
    # Mock create_many method
    def mock_create_many(topics):
        for topic in topics:
            topic.id = uuid.uuid4()
        return topics
    
    repo.create_many.side_effect = mock_create_many
    repo.get_by_video_id.return_value = []
    
    return repo


@pytest.fixture
def mock_langchain_client():
    client = AsyncMock()
    
    # Mock topics extraction
    topic_results = [
        {
            "name": "Artificial Intelligence",
            "description": "General overview of AI concepts and applications.",
            "relevance": 0.9
        },
        {
            "name": "Machine Learning",
            "description": "Discussion of machine learning techniques and methodologies.",
# api/tests/unit/services/test_topic_extraction_service.py (continued)
            "relevance": 0.8
        },
        {
            "name": "Neural Networks",
            "description": "Explanation of neural network architecture and functionality.",
            "relevance": 0.7
        }
    ]
    client.extract_topics.return_value = topic_results
    
    # Mock timestamp detection
    timestamp_results = {
        "Artificial Intelligence": {"start": 0.0, "end": 10.0},
        "Machine Learning": {"start": 10.0, "end": 20.0},
        "Neural Networks": {"start": 20.0, "end": 30.0}
    }
    client.detect_topic_timestamps.return_value = timestamp_results
    
    return client


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock()
    return publisher


@pytest.mark.asyncio
async def test_extract_topics(
    mock_video_repository, mock_summary_repository, 
    mock_transcript_repository, mock_topic_repository,
    mock_langchain_client, mock_event_publisher
):
    # Arrange
    _, video = mock_video_repository
    summary_repo, summary = mock_summary_repository
    transcript_repo, transcript = mock_transcript_repository
    
    # Update IDs to link entities
    summary.video_id = video.id
    transcript.video_id = video.id
    
    service = TopicExtractionService(
        video_repository=mock_video_repository[0],
        summary_repository=summary_repo,
        transcript_repository=transcript_repo,
        topic_repository=mock_topic_repository,
        langchain_client=mock_langchain_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    topics = await service.extract_topics(summary.id)
    
    # Assert
    assert topics is not None
    assert len(topics) == 3
    
    # Verify topics were created with correct properties
    assert topics[0].name == "Artificial Intelligence"
    assert topics[0].relevance == 0.9
    assert topics[0].video_id == video.id
    assert topics[0].summary_id == summary.id
    
    # Verify timestamps were added
    assert topics[0].start_time == timedelta(seconds=0.0)
    assert topics[0].end_time == timedelta(seconds=10.0)
    
    # Verify LangChain client was called
    mock_langchain_client.extract_topics.assert_called_once()
    
    # Verify timestamp detection was called
    mock_langchain_client.detect_topic_timestamps.assert_called_once()
    
    # Verify topics were saved
    mock_topic_repository.create_many.assert_called_once()
    
    # Verify event was published
    mock_event_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_extract_topics_no_transcript(
    mock_video_repository, mock_summary_repository, 
    mock_transcript_repository, mock_topic_repository,
    mock_langchain_client, mock_event_publisher
):
    # Arrange
    _, video = mock_video_repository
    summary_repo, summary = mock_summary_repository
    transcript_repo, _ = mock_transcript_repository
    
    # Set up missing transcript
    transcript_repo.get_by_video_id.return_value = None
    
    # Update IDs to link entities
    summary.video_id = video.id
    
    service = TopicExtractionService(
        video_repository=mock_video_repository[0],
        summary_repository=summary_repo,
        transcript_repository=transcript_repo,
        topic_repository=mock_topic_repository,
        langchain_client=mock_langchain_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    topics = await service.extract_topics(summary.id)
    
    # Assert
    assert topics is not None
    assert len(topics) == 3
    
    # Verify topics were created, but without timestamps
    assert topics[0].start_time is None
    assert topics[0].end_time is None
    
    # Verify timestamp detection was not called
    mock_langchain_client.detect_topic_timestamps.assert_not_called()


@pytest.mark.asyncio
async def test_extract_topics_langchain_failure(
    mock_video_repository, mock_summary_repository, 
    mock_transcript_repository, mock_topic_repository,
    mock_langchain_client, mock_event_publisher
):
    # Arrange
    _, video = mock_video_repository
    summary_repo, summary = mock_summary_repository
    
    # Set up LangChain to fail
    mock_langchain_client.extract_topics.side_effect = Exception("LangChain error")
    
    # Update IDs to link entities
    summary.video_id = video.id
    
    service = TopicExtractionService(
        video_repository=mock_video_repository[0],
        summary_repository=summary_repo,
        transcript_repository=mock_transcript_repository[0],
        topic_repository=mock_topic_repository,
        langchain_client=mock_langchain_client,
        event_publisher=mock_event_publisher
    )
    
    # Act & Assert
    with pytest.raises(Exception, match="LangChain error"):
        await service.extract_topics(summary.id)
    
    # Verify failure event was published
    mock_event_publisher.publish.assert_called_once()
    call_args = mock_event_publisher.publish.call_args[0][0]
    assert call_args.event_type == "topics.extraction.failed"
    assert call_args.payload["summary_id"] == str(summary.id)


@pytest.mark.asyncio
async def test_rank_topics_by_relevance(
    mock_video_repository, mock_summary_repository, 
    mock_transcript_repository, mock_topic_repository,
    mock_langchain_client, mock_event_publisher
):
    # Arrange
    _, video = mock_video_repository
    
    # Set up topics with different relevance scores
    topics = [
        Topic(id=uuid.uuid4(), video_id=video.id, name="Low Relevance", relevance=0.3),
        Topic(id=uuid.uuid4(), video_id=video.id, name="High Relevance", relevance=0.9),
        Topic(id=uuid.uuid4(), video_id=video.id, name="Medium Relevance", relevance=0.6)
    ]
    mock_topic_repository.get_by_video_id.return_value = topics
    
    service = TopicExtractionService(
        video_repository=mock_video_repository[0],
        summary_repository=mock_summary_repository[0],
        transcript_repository=mock_transcript_repository[0],
        topic_repository=mock_topic_repository,
        langchain_client=mock_langchain_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    ranked_topics = await service.rank_topics_by_relevance(video.id)
    
    # Assert
    assert ranked_topics is not None
    assert len(ranked_topics) == 3
    assert ranked_topics[0].name == "High Relevance"
    assert ranked_topics[1].name == "Medium Relevance"
    assert ranked_topics[2].name == "Low Relevance"