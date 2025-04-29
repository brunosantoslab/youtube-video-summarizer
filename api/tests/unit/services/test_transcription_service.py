"""
Unit tests for the Transcription Service
Author: Bruno Santos
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.models.video import Video, VideoStatus
from domain.models.transcript import (
    Transcript, TranscriptSourceType, ProcessingStatus, 
    TranscriptSegment
)
from application.services.transcription_service import TranscriptionService


@pytest.fixture
def mock_video_repository():
    repo = MagicMock()
    video = Video(
        id=uuid.uuid4(),
        youtube_id="test_video_id",
        title="Test Video",
        description="Test description",
        channel_id="test_channel_id",
        channel_title="Test Channel",
        status=VideoStatus.NEW
    )
    repo.get_by_id.return_value = video
    return repo, video


@pytest.fixture
def mock_transcript_repository():
    repo = MagicMock()
    # Initially no transcript exists
    repo.get_by_video_id.return_value = None
    
    # Mock create method
    def mock_create(transcript):
        transcript.id = uuid.uuid4()
        return transcript
    
    repo.create.side_effect = mock_create
    
    # Mock update method
    def mock_update(transcript):
        return transcript
    
    repo.update.side_effect = mock_update
    
    return repo


@pytest.fixture
def mock_youtube_client():
    client = AsyncMock()
    # By default, no captions available
    client.get_video_captions.return_value = None
    return client


@pytest.fixture
def mock_audio_downloader():
    downloader = MagicMock()
    downloader.download_audio.return_value = (b"test_audio_data", "mp3")
    return downloader


@pytest.fixture
def mock_whisper_client():
    client = AsyncMock()
    
    # Mock transcription response
    whisper_result = {
        "text": "This is a test transcript.",
        "segments": [
            {
                "start": 0.0,
                "end": 2.5,
                "text": "This is a"
            },
            {
                "start": 2.5,
                "end": 5.0,
                "text": "test transcript."
            }
        ],
        "_metadata": {
            "processing_time": 3.5
        }
    }
    client.transcribe_audio.return_value = whisper_result
    
    # Mock segment parsing
    def mock_parse_segments(result):
        return [
            TranscriptSegment(start_time=0.0, end_time=2.5, text="This is a"),
            TranscriptSegment(start_time=2.5, end_time=5.0, text="test transcript.")
        ]
    
    client.parse_segments.side_effect = mock_parse_segments
    
    return client


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock()
    return publisher


@pytest.mark.asyncio
async def test_extract_transcript_youtube_captions(
    mock_video_repository, mock_transcript_repository, 
    mock_youtube_client, mock_audio_downloader, 
    mock_whisper_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    
    # Set up YouTube captions to be available
    mock_youtube_client.get_video_captions.return_value = """
1
00:00:00,000 --> 00:00:02,500
This is a

2
00:00:02,500 --> 00:00:05,000
test transcript.
"""
    
    service = TranscriptionService(
        video_repository=video_repo,
        transcript_repository=mock_transcript_repository,
        youtube_client=mock_youtube_client,
        audio_downloader=mock_audio_downloader,
        whisper_client=mock_whisper_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    transcript = await service.extract_transcript(video.id)
    
    # Assert
    assert transcript is not None
    assert transcript.content == "This is a test transcript."
    assert transcript.source_type == TranscriptSourceType.YOUTUBE
    assert transcript.processing_status == ProcessingStatus.COMPLETED
    assert len(transcript.segments) == 2
    
    # Verify YouTube API was called
    mock_youtube_client.get_video_captions.assert_called_once_with(video.youtube_id)
    
    # Verify Whisper API was NOT called (since YouTube captions were available)
    mock_whisper_client.transcribe_audio.assert_not_called()
    
    # Verify event was published
    mock_event_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_extract_transcript_whisper_fallback(
    mock_video_repository, mock_transcript_repository, 
    mock_youtube_client, mock_audio_downloader, 
    mock_whisper_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    
    # Set up YouTube captions to NOT be available
    mock_youtube_client.get_video_captions.return_value = None
    
    # Set up whisper transcription result
    whisper_result = {
        "text": "This is a test transcript.",
        "segments": [
            {
                "start": 0.0,
                "end": 2.5,
                "text": "This is a"
            },
            {
                "start": 2.5,
                "end": 5.0,
                "text": "test transcript."
            }
        ],
        "_metadata": {
            "processing_time": 3.5
        }
    }
    mock_whisper_client.transcribe_audio.return_value = whisper_result
    
    # Mock for segments parsing
    segments = [
        TranscriptSegment(start_time=0.0, end_time=2.5, text="This is a"),
        TranscriptSegment(start_time=2.5, end_time=5.0, text="test transcript.")
    ]
    
    # Important: If parse_segments is an async method in your implementation, use this:
    # mock_whisper_client.parse_segments.return_value = segments
    # Otherwise, if it's a regular method:
    mock_whisper_client.parse_segments = MagicMock(return_value=segments)
    
    service = TranscriptionService(
        video_repository=video_repo,
        transcript_repository=mock_transcript_repository,
        youtube_client=mock_youtube_client,
        audio_downloader=mock_audio_downloader,
        whisper_client=mock_whisper_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    transcript = await service.extract_transcript(video.id)
    
    # Assert
    assert transcript is not None
    assert transcript.content == "This is a test transcript."
    assert transcript.source_type == TranscriptSourceType.WHISPER
    assert transcript.processing_status == ProcessingStatus.COMPLETED
    assert len(transcript.segments) == 2
    
    # Verify YouTube API was called but failed
    mock_youtube_client.get_video_captions.assert_called_once_with(video.youtube_id)
    
    # Verify audio was downloaded
    mock_audio_downloader.download_audio.assert_called_once_with(video.youtube_id)
    
    # Verify Whisper API was called as fallback
    mock_whisper_client.transcribe_audio.assert_called_once()
    
    # Verify event was published
    mock_event_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_extract_transcript_existing_transcript(
    mock_video_repository, mock_transcript_repository, 
    mock_youtube_client, mock_audio_downloader, 
    mock_whisper_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    
    # Set up an existing transcript
    existing_transcript = Transcript(
        id=uuid.uuid4(),
        video_id=video.id,
        content="Existing transcript content",
        processing_status=ProcessingStatus.COMPLETED
    )
    mock_transcript_repository.get_by_video_id.return_value = existing_transcript
    
    service = TranscriptionService(
        video_repository=video_repo,
        transcript_repository=mock_transcript_repository,
        youtube_client=mock_youtube_client,
        audio_downloader=mock_audio_downloader,
        whisper_client=mock_whisper_client,
        event_publisher=mock_event_publisher
    )
    
    # Act
    transcript = await service.extract_transcript(video.id)
    
    # Assert
    assert transcript is not None
    assert transcript.id == existing_transcript.id
    assert transcript.content == "Existing transcript content"
    
    # Verify no API calls were made
    mock_youtube_client.get_video_captions.assert_not_called()
    mock_audio_downloader.download_audio.assert_not_called()
    mock_whisper_client.transcribe_audio.assert_not_called()
    
    # Verify no event was published
    mock_event_publisher.publish.assert_not_called()


@pytest.mark.asyncio
async def test_extract_transcript_both_methods_fail(
    mock_video_repository, mock_transcript_repository, 
    mock_youtube_client, mock_audio_downloader, 
    mock_whisper_client, mock_event_publisher
):
    # Arrange
    video_repo, video = mock_video_repository
    
    # Set up YouTube captions to NOT be available
    mock_youtube_client.get_video_captions.return_value = None
    
    # Set up Whisper to fail
    mock_whisper_client.transcribe_audio.side_effect = Exception("Whisper API error")
    
    service = TranscriptionService(
        video_repository=video_repo,
        transcript_repository=mock_transcript_repository,
        youtube_client=mock_youtube_client,
        audio_downloader=mock_audio_downloader,
        whisper_client=mock_whisper_client,
        event_publisher=mock_event_publisher
    )
    
    # Act/Assert
    with pytest.raises(Exception):
        await service.extract_transcript(video.id)
    
    # Verify transcript was saved with failed status
    mock_transcript_repository.create.assert_called_once()
    created_transcript = mock_transcript_repository.create.call_args[0][0]
    assert created_transcript.processing_status == ProcessingStatus.FAILED
    assert "Whisper API error" in created_transcript.metadata.error_message
