# api/tests/unit/youtube/services/test_feed_service.py
"""
Unit tests for YouTube Feed Service
Author: Bruno Santos
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
from datetime import datetime

from application.services.youtube.feed_service import YouTubeFeedService
from infrastructure.youtube.youtube_api_service import YouTubeAPIService
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from domain.models.user import User


class TestYouTubeFeedService:
    """Test YouTube Feed Service"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.youtube_api_service = MagicMock(spec=YouTubeAPIService)
        self.user_repository = MagicMock(spec=IUserRepository)
        self.video_repository = MagicMock(spec=IVideoRepository)
        
        self.feed_service = YouTubeFeedService(
            youtube_api_service=self.youtube_api_service,
            user_repository=self.user_repository,
            video_repository=self.video_repository
        )
        
        # Setup async mocks
        self.youtube_api_service.get_user_subscriptions = AsyncMock()
        self.youtube_api_service.get_recent_videos_from_subscriptions = AsyncMock()
        self.youtube_api_service.get_channel_details = AsyncMock()
        self.youtube_api_service.get_video_details = AsyncMock()
        self.youtube_api_service.get_video_transcript = AsyncMock()
        self.youtube_api_service.get_video_with_transcript = AsyncMock()
        
        # Mock the process_new_videos method - important to use patch here
        # to ensure the method is properly mocked while keeping the original function available
        self.patcher = patch.object(self.feed_service, 'process_new_videos', new_callable=AsyncMock)
        self.mock_process_new_videos = self.patcher.start()
        
        # Common test data
        self.user_id = uuid.uuid4()
        self.test_user = User(
            id=self.user_id,
            email="test@example.com",
            youtube_user_id="test_youtube_id",
            display_name="Test User"
        )
    
    def teardown_method(self):
        """Cleanup after tests"""
        # Stop the patch
        self.patcher.stop()
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self):
        """Test getting user subscriptions"""
        # Setup
        mock_subscriptions = [
            {"snippet": {"title": "Channel 1", "resourceId": {"channelId": "channel1"}}},
            {"snippet": {"title": "Channel 2", "resourceId": {"channelId": "channel2"}}}
        ]
        self.youtube_api_service.get_user_subscriptions.return_value = mock_subscriptions
        
        # Execute
        result = await self.feed_service.get_user_subscriptions(self.user_id)
        
        # Assert
        assert result == mock_subscriptions
        self.youtube_api_service.get_user_subscriptions.assert_called_once_with(
            self.user_id, all_pages=True
        )
    
    @pytest.mark.asyncio
    async def test_get_recent_videos_from_subscriptions(self):
        """Test getting recent videos from subscriptions"""
        # Setup
        mock_videos = [
            {"id": {"videoId": "video1"}, "snippet": {"title": "Video 1"}},
            {"id": {"videoId": "video2"}, "snippet": {"title": "Video 2"}}
        ]
        self.youtube_api_service.get_recent_videos_from_subscriptions.return_value = mock_videos
        
        # Execute
        result = await self.feed_service.get_recent_videos_from_subscriptions(
            user_id=self.user_id,
            max_days=5,
            max_videos=10
        )
        
        # Assert
        assert result == mock_videos
        self.youtube_api_service.get_recent_videos_from_subscriptions.assert_called_once_with(
            user_id=self.user_id,
            max_days=5,
            max_results_per_channel=5,
            max_total_results=10
        )
    
    @pytest.mark.asyncio
    async def test_get_channel_details(self):
        """Test getting channel details"""
        # Setup
        channel_id = "test_channel_id"
        mock_channel = {"id": channel_id, "snippet": {"title": "Test Channel"}}
        self.youtube_api_service.get_channel_details.return_value = mock_channel
        
        # Execute
        result = await self.feed_service.get_channel_details(
            channel_id=channel_id,
            user_id=self.user_id
        )
        
        # Assert
        assert result == mock_channel
        self.youtube_api_service.get_channel_details.assert_called_once_with(
            channel_id=channel_id,
            auth_user_id=self.user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_details(self):
        """Test getting video details"""
        # Setup
        video_id = "test_video_id"
        mock_video = {"id": video_id, "snippet": {"title": "Test Video"}}
        self.youtube_api_service.get_video_details.return_value = [mock_video]
        
        # Execute
        result = await self.feed_service.get_video_details(
            video_id=video_id,
            user_id=self.user_id
        )
        
        # Assert
        assert result == mock_video
        self.youtube_api_service.get_video_details.assert_called_once_with(
            video_id=video_id,
            auth_user_id=self.user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_details_not_found(self):
        """Test getting video details when not found"""
        # Setup
        video_id = "nonexistent_video_id"
        self.youtube_api_service.get_video_details.return_value = []
        
        # Execute
        result = await self.feed_service.get_video_details(
            video_id=video_id,
            user_id=self.user_id
        )
        
        # Assert
        assert result is None
        self.youtube_api_service.get_video_details.assert_called_once_with(
            video_id=video_id,
            auth_user_id=self.user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_transcript(self):
        """Test getting video transcript"""
        # Setup
        video_id = "test_video_id"
        mock_transcript = "This is a test transcript."
        self.youtube_api_service.get_video_transcript.return_value = mock_transcript
        
        # Execute
        result = await self.feed_service.get_video_transcript(
            video_id=video_id,
            language_code="en",
            user_id=self.user_id
        )
        
        # Assert
        assert result == mock_transcript
        self.youtube_api_service.get_video_transcript.assert_called_once_with(
            video_id=video_id,
            language_code="en",
            auth_user_id=self.user_id
        )
    
    @pytest.mark.asyncio
    async def test_get_video_transcript_no_user_id(self):
        """Test getting video transcript without user ID"""
        # Setup
        video_id = "test_video_id"
        
        # Execute
        result = await self.feed_service.get_video_transcript(
            video_id=video_id,
            language_code="en",
            user_id=None
        )
        
        # Assert
        assert result is None
        self.youtube_api_service.get_video_transcript.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_video_with_transcript(self):
        """Test getting video with transcript"""
        # Setup
        video_id = "test_video_id"
        mock_video = {"id": video_id, "snippet": {"title": "Test Video"}}
        mock_transcript = "This is a test transcript."
        self.youtube_api_service.get_video_with_transcript.return_value = (mock_video, mock_transcript)
        
        # Execute
        result = await self.feed_service.get_video_with_transcript(
            video_id=video_id,
            language_code="en",
            user_id=self.user_id
        )
        
        # Assert
        assert result == {
            "video_details": mock_video,
            "transcript": mock_transcript
        }
        self.youtube_api_service.get_video_with_transcript.assert_called_once_with(
            video_id=video_id,
            language_code="en",
            auth_user_id=self.user_id
        )
    
    @pytest.mark.asyncio
    async def test_check_for_new_videos(self):
        """Test checking for new videos"""
        # Setup
        mock_videos = [
            {"id": {"videoId": "video1"}, "snippet": {"title": "Video 1"}},
            {"id": {"videoId": "video2"}, "snippet": {"title": "Video 2"}},
            {"id": {"videoId": "video3"}, "snippet": {"title": "Video 3"}}
        ]
        self.youtube_api_service.get_recent_videos_from_subscriptions.return_value = mock_videos
        
        # Mock video repository to say only video3 exists
        self.video_repository.exists_by_youtube_id = MagicMock(
            side_effect=lambda vid: vid == "video3"
        )
        
        # Execute
        result = await self.feed_service.check_for_new_videos(self.user_id, days=1)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"]["videoId"] == "video1"
        assert result[1]["id"]["videoId"] == "video2"
        
        self.youtube_api_service.get_recent_videos_from_subscriptions.assert_called_once_with(
            user_id=self.user_id,
            max_days=1,
            max_results_per_channel=5,
            max_total_results=50
        )
        
        # Verify video repository was called for each video
        assert self.video_repository.exists_by_youtube_id.call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_new_videos(self):
        """Test processing new videos"""
        # Create a separate service instance just for this test
        # to avoid interference with other tests
        test_service = YouTubeFeedService(
            youtube_api_service=self.youtube_api_service,
            user_repository=self.user_repository,
            video_repository=self.video_repository
        )
        
        # Setup mocks on the test service
        # Mock check_for_new_videos
        mock_videos = [
            {"id": {"videoId": "video1"}, "snippet": {"title": "Video 1"}},
            {"id": {"videoId": "video2"}, "snippet": {"title": "Video 2"}}
        ]
        
        with patch.object(test_service, 'check_for_new_videos', new_callable=AsyncMock) as mock_check, \
             patch.object(test_service, 'get_video_details', new_callable=AsyncMock) as mock_get_details:
            # Configure mocks
            mock_check.return_value = mock_videos
            mock_get_details.return_value = {"id": "video1", "snippet": {"title": "Video 1 Details"}}
            
            # Execute
            result = await test_service.process_new_videos(self.user_id)
            
            # Assert
            assert result == 2  # Should return the number of videos
            mock_check.assert_called_once_with(self.user_id, days=1)
            assert mock_get_details.call_count == 2  # Called once for each video
    
    @pytest.mark.asyncio
    async def test_monitor_user_feed_success(self):
        """Test monitoring user feed successfully"""
        # Setup
        self.user_repository.get_by_id.return_value = self.test_user
        self.mock_process_new_videos.return_value = 5
        
        # Execute
        result = await self.feed_service.monitor_user_feed(self.user_id)
        
        # Assert
        assert result["success"] is True
        assert result["user_id"] == str(self.user_id)
        assert result["new_videos_count"] == 5
        assert "monitored_at" in result
        
        self.user_repository.get_by_id.assert_called_once_with(self.user_id)
        self.mock_process_new_videos.assert_called_once_with(self.user_id)
    
    @pytest.mark.asyncio
    async def test_monitor_user_feed_user_not_found(self):
        """Test monitoring user feed when user not found"""
        # Setup
        self.user_repository.get_by_id.return_value = None
        
        # Execute
        result = await self.feed_service.monitor_user_feed(self.user_id)
        
        # Assert
        assert result["success"] is False
        assert "error" in result
        assert f"User {self.user_id} not found" in result["error"]
        
        self.user_repository.get_by_id.assert_called_once_with(self.user_id)
        self.mock_process_new_videos.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_monitor_user_feed_exception(self):
        """Test monitoring user feed when an exception occurs"""
        # Setup - Configure repository to raise an exception
        error_message = "Test exception"
        exception = Exception(error_message)
        self.user_repository.get_by_id.side_effect = exception
        
        # Execute
        result = await self.feed_service.monitor_user_feed(self.user_id)
        
        # Assert
        assert result["success"] is False
        assert "error" in result
        assert error_message in result["error"]
        
        self.user_repository.get_by_id.assert_called_once_with(self.user_id)
        self.mock_process_new_videos.assert_not_called()
