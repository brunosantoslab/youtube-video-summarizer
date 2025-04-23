# api/tests/unit/services/test_feed_monitoring_service.py
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.models.user import User
from domain.models.video import VideoStatus
from application.services.feed_monitoring_service import FeedMonitoringService


@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        youtube_user_id="user123",
        display_name="Test User"
    )
    repo.get_by_id.return_value = user
    return repo


@pytest.fixture
def mock_video_repository():
    repo = MagicMock()
    repo.get_by_youtube_id.return_value = None
    
    def mock_create(video):
        # Return the same video but with an ID
        return video
    
    repo.create.side_effect = mock_create
    return repo


@pytest.fixture
def mock_youtube_client():
    client = AsyncMock()
    
    # Mock subscriptions response
    subscriptions_response = {
        "items": [
            {"snippet": {"resourceId": {"channelId": "channel1"}}},
            {"snippet": {"resourceId": {"channelId": "channel2"}}}
        ]
    }
    client.get_subscriptions.return_value = subscriptions_response
    
    # Mock videos response
    videos_response = {
        "items": [
            {"id": {"videoId": "video1"}, "snippet": {"title": "Video 1"}}
        ]
    }
    client.get_videos_for_channel.return_value = videos_response
    
    # Mock video details response
    video_details_response = {
        "items": [
            {
                "id": "video1",
                "snippet": {
                    "title": "Video 1",
                    "description": "Description 1",
                    "channelId": "channel1",
                    "channelTitle": "Channel 1",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "thumbnails": {
                        "high": {
                            "url": "https://example.com/thumbnail.jpg"
                        }
                    }
                },
                "contentDetails": {
                    "duration": "PT10M30S"
                }
            }
        ]
    }
    client.get_video_details.return_value = video_details_response
    
    return client


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock()
    return publisher


@pytest.mark.asyncio
async def test_check_for_new_videos(
    mock_user_repository, mock_video_repository, mock_youtube_client, mock_event_publisher
):
    # Arrange
    service = FeedMonitoringService(
        user_repository=mock_user_repository,
        video_repository=mock_video_repository,
        youtube_client=mock_youtube_client,
        event_publisher=mock_event_publisher
    )
    
    user_id = uuid.uuid4()
    
    # Act
    new_videos = await service.check_for_new_videos(user_id)
    
    # Assert
    assert len(new_videos) == 2  # One video from each channel
    mock_user_repository.get_by_id.assert_called_once_with(user_id)
    assert mock_youtube_client.get_subscriptions.call_count == 1
    assert mock_youtube_client.get_videos_for_channel.call_count == 2
    assert mock_video_repository.get_by_youtube_id.call_count == 2
    assert mock_video_repository.create.call_count == 2
    assert mock_event_publisher.publish.call_count == 2
    
    # Check video properties
    video = new_videos[0]
    assert video.youtube_id == "video1"
    assert video.title == "Video 1"
    assert video.channel_id == "channel1"
    assert video.status == VideoStatus.NEW
    assert isinstance(video.duration, timedelta)
    assert video.duration.total_seconds() == 630  # 10 minutes 30 seconds