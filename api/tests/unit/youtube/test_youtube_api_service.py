# api/tests/unit/youtube/test_youtube_api_service.py
"""
Unit tests for YouTube API Service
Author: Bruno Santos
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
from datetime import datetime, timedelta

from infrastructure.youtube.youtube_api_service import YouTubeAPIService
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService


class TestYouTubeAPIService:
    """Test YouTube API Service"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.youtube_oauth_service = MagicMock(spec=YouTubeOAuthService)
        self.api_service = YouTubeAPIService(
            youtube_oauth_service=self.youtube_oauth_service,
            api_key="test_api_key"
        )
        
        # Mock the specialized clients
        self.api_service.channels_client = MagicMock()
        self.api_service.videos_client = MagicMock()
        self.api_service.captions_client = MagicMock()
        
        # Setup async mocks
        self.api_service.channels_client.get_subscriptions = AsyncMock()
        self.api_service.channels_client.get_channel_details = AsyncMock()
        self.api_service.videos_client.get_video_details = AsyncMock()
        self.api_service.videos_client.get_recent_videos_from_channel = AsyncMock()
        self.api_service.captions_client.get_transcript = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self):
        """Test getting user subscriptions"""
        # Setup
        user_id = uuid.uuid4()
        mock_subscriptions = {
            "items": [
                {"id": "sub1", "snippet": {"title": "Channel 1", "resourceId": {"channelId": "channel1"}}},
                {"id": "sub2", "snippet": {"title": "Channel 2", "resourceId": {"channelId": "channel2"}}}
            ]
        }
        self.api_service.channels_client.get_subscriptions.return_value = mock_subscriptions
        
        # Execute
        result = await self.api_service.get_user_subscriptions(user_id, all_pages=True)
        
        # Assert
        assert result == mock_subscriptions["items"]
        self.api_service.channels_client.get_subscriptions.assert_called_once_with(
            user_id=user_id,
            max_results=50,
            all_pages=True
        )
    
    @pytest.mark.asyncio
    async def test_get_channel_details(self):
        """Test getting channel details"""
        # Setup
        channel_id = "test_channel_id"
        user_id = uuid.uuid4()
        mock_channel = {
            "items": [
                {"id": channel_id, "snippet": {"title": "Test Channel"}}
            ]
        }
        self.api_service.channels_client.get_channel_details.return_value = mock_channel
        
        # Execute
        result = await self.api_service.get_channel_details(channel_id, auth_user_id=user_id)
        
        # Assert
        assert result == mock_channel["items"][0]
        self.api_service.channels_client.get_channel_details.assert_called_once_with(
            channel_id=channel_id,
            auth_user_id=user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_details(self):
        """Test getting video details"""
        # Setup
        video_id = "test_video_id"
        user_id = uuid.uuid4()
        mock_video = {
            "items": [
                {"id": video_id, "snippet": {"title": "Test Video"}}
            ]
        }
        self.api_service.videos_client.get_video_details.return_value = mock_video
        
        # Execute
        result = await self.api_service.get_video_details(video_id, auth_user_id=user_id)
        
        # Assert
        assert result == mock_video["items"]
        self.api_service.videos_client.get_video_details.assert_called_once_with(
            video_id=video_id,
            auth_user_id=user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_recent_videos_from_channel(self):
        """Test getting recent videos from a channel"""
        # Setup
        channel_id = "test_channel_id"
        user_id = uuid.uuid4()
        mock_videos = {
            "items": [
                {"id": {"videoId": "video1"}, "snippet": {"title": "Video 1"}},
                {"id": {"videoId": "video2"}, "snippet": {"title": "Video 2"}}
            ]
        }
        self.api_service.videos_client.get_recent_videos_from_channel.return_value = mock_videos
        
        # Execute
        result = await self.api_service.get_recent_videos_from_channel(
            channel_id=channel_id,
            max_days=5,
            max_results=10,
            auth_user_id=user_id
        )
        
        # Assert
        assert result == mock_videos["items"]
        self.api_service.videos_client.get_recent_videos_from_channel.assert_called_once_with(
            channel_id=channel_id,
            max_days=5,
            max_results=10,
            auth_user_id=user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_transcript(self):
        """Test getting video transcript"""
        # Setup
        video_id = "test_video_id"
        user_id = uuid.uuid4()
        mock_transcript = "This is a test transcript."
        self.api_service.captions_client.get_transcript.return_value = mock_transcript
        
        # Execute
        result = await self.api_service.get_video_transcript(
            video_id=video_id,
            language_code="en",
            auth_user_id=user_id
        )
        
        # Assert
        assert result == mock_transcript
        self.api_service.captions_client.get_transcript.assert_called_once_with(
            video_id=video_id,
            language_code="en",
            auth_user_id=user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_recent_videos_from_subscriptions(self):
        """Test getting recent videos from subscriptions"""
        # Setup
        user_id = uuid.uuid4()
        mock_subscriptions = {
            "items": [
                {"snippet": {"resourceId": {"channelId": "channel1"}}},
                {"snippet": {"resourceId": {"channelId": "channel2"}}}
            ]
        }
        
        mock_channel1_videos = [
            {"id": {"videoId": "video1"}, "snippet": {"publishedAt": "2023-01-02T00:00:00Z", "title": "Video 1"}},
            {"id": {"videoId": "video2"}, "snippet": {"publishedAt": "2023-01-01T00:00:00Z", "title": "Video 2"}}
        ]
        
        mock_channel2_videos = [
            {"id": {"videoId": "video3"}, "snippet": {"publishedAt": "2023-01-03T00:00:00Z", "title": "Video 3"}},
            {"id": {"videoId": "video4"}, "snippet": {"publishedAt": "2023-01-01T00:00:00Z", "title": "Video 4"}}
        ]
        
        # Mock the method calls
        self.api_service.channels_client.get_subscriptions.return_value = mock_subscriptions
        
        self.api_service.get_recent_videos_from_channel = AsyncMock(side_effect=[
            mock_channel1_videos,
            mock_channel2_videos
        ])
        
        # Execute
        result = await self.api_service.get_recent_videos_from_subscriptions(
            user_id=user_id,
            max_days=7,
            max_results_per_channel=2,
            max_total_results=5
        )
        
        # Assert
        # Should have all videos sorted by date (newest first)
        expected_order = [
            mock_channel2_videos[0],  # video3 (newest)
            mock_channel1_videos[0],  # video1
            mock_channel1_videos[1],  # video2
            mock_channel2_videos[1],  # video4
        ]
        
        assert len(result) == 4
        assert result == expected_order
        
        # Verify channels_client.get_subscriptions was called correctly
        self.api_service.channels_client.get_subscriptions.assert_called_once_with(
            user_id=user_id,
            all_pages=True
        )
        
        # Verify get_recent_videos_from_channel was called for each channel
        assert self.api_service.get_recent_videos_from_channel.call_count == 2
        
        # First call for channel1
        self.api_service.get_recent_videos_from_channel.assert_any_call(
            channel_id="channel1",
            max_days=7,
            max_results=2,
            auth_user_id=user_id
        )
        
        # Second call for channel2
        self.api_service.get_recent_videos_from_channel.assert_any_call(
            channel_id="channel2",
            max_days=7,
            max_results=2,
            auth_user_id=user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_with_transcript(self):
        """Test getting video with transcript"""
        # Setup
        video_id = "test_video_id"
        user_id = uuid.uuid4()
        language_code = "en"
        
        mock_video_list = [
            {"id": video_id, "snippet": {"title": "Test Video"}}
        ]
        mock_transcript = "This is a test transcript."
        
        # Create a separate method for testing to avoid mocking issues
        async def mock_get_video_details(video_id, auth_user_id):
            return mock_video_list
            
        async def mock_get_transcript(video_id, language_code, auth_user_id):
            return mock_transcript
            
        # Replace the methods with our mock implementations
        self.api_service.get_video_details = mock_get_video_details
        self.api_service.get_video_transcript = mock_get_transcript
        
        # Execute
        video_details, transcript = await self.api_service.get_video_with_transcript(
            video_id=video_id,
            language_code=language_code,
            auth_user_id=user_id
        )
        
        # Assert
        assert video_details == mock_video_list[0]
        assert transcript == mock_transcript
    
    @pytest.mark.asyncio
    async def test_get_video_with_transcript_no_video(self):
        """Test getting video with transcript when video not found"""
        # Setup
        video_id = "test_video_id"
        user_id = uuid.uuid4()
        language_code = "en"
        
        # Create a separate method for testing to avoid mocking issues
        async def mock_get_video_details(video_id, auth_user_id):
            return []
            
        async def mock_get_transcript(video_id, language_code, auth_user_id):
            return "This is a test transcript."
            
        # Replace the methods with our mock implementations
        self.api_service.get_video_details = mock_get_video_details
        self.api_service.get_video_transcript = mock_get_transcript
        
        # Execute
        video_details, transcript = await self.api_service.get_video_with_transcript(
            video_id=video_id,
            language_code=language_code,
            auth_user_id=user_id
        )
        
        # Assert
        assert video_details is None
        assert transcript == "This is a test transcript."
