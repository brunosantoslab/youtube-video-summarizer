# api/application/services/feed_monitoring_service.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from domain.models.video import Video, VideoStatus
from domain.models.user import User
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from application.events.event_publisher import IEventPublisher

logger = logging.getLogger(__name__)


class VideoDiscoveredEvent:
    """Event raised when a new video is discovered"""
    
    def __init__(self, video_id: uuid.UUID):
        self.event_type = "video.discovered"
        self.payload = {"video_id": str(video_id)}


class FeedMonitoringService:
    """Service for monitoring YouTube feeds for new videos"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        video_repository: IVideoRepository,
        youtube_client,  # YouTubeApiClient
        event_publisher: IEventPublisher
    ):
        self.user_repository = user_repository
        self.video_repository = video_repository
        self.youtube_client = youtube_client
        self.event_publisher = event_publisher
    
    async def check_for_new_videos(self, user_id: uuid.UUID) -> List[Video]:
        """Check for new videos in user's subscriptions"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get user access token (this would normally come from a token service)
        access_token = self._get_user_access_token(user)
        
        # Get subscriptions
        subscriptions = await self._get_user_subscriptions(access_token)
        
        # Check each subscription for new videos
        new_videos = []
        for channel_id in subscriptions:
            channel_videos = await self._get_new_videos_for_channel(channel_id)
            for video in channel_videos:
                # Check if video already exists in our database
                existing_video = self.video_repository.get_by_youtube_id(video.youtube_id)
                if not existing_video:
                    # Save new video
                    saved_video = self.video_repository.create(video)
                    new_videos.append(saved_video)
                    
                    # Publish event for new video
                    await self.event_publisher.publish(
                        VideoDiscoveredEvent(video_id=saved_video.id)
                    )
        
        return new_videos
    
    def _get_user_access_token(self, user: User) -> str:
        """Get the user's access token for YouTube API
        
        In a real implementation, this would get the token from a token service
        or auth provider. For testing purposes, we return a placeholder.
        """
        # This is a placeholder implementation
        return "mock_access_token"
    
    async def _get_user_subscriptions(self, access_token: str) -> List[str]:
        """Get list of channel IDs that the user is subscribed to"""
        channel_ids = []
        page_token = None
        
        while True:
            response = await self.youtube_client.get_subscriptions(
                access_token=access_token,
                page_token=page_token
            )
            
            # Extract channel IDs
            for item in response.get("items", []):
                channel_id = item["snippet"]["resourceId"]["channelId"]
                channel_ids.append(channel_id)
            
            # Check if there are more pages
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        
        return channel_ids
    
    async def _get_new_videos_for_channel(
        self, channel_id: str, days_back: int = 1
    ) -> List[Video]:
        """Get new videos from a channel published within specified days"""
        published_after = datetime.now() - timedelta(days=days_back)
        videos = []
        page_token = None
        
        while True:
            response = await self.youtube_client.get_videos_for_channel(
                channel_id=channel_id,
                published_after=published_after,
                page_token=page_token
            )
            
            # Process videos
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                
                # Get full video details
                video_details = await self.youtube_client.get_video_details(video_id)
                if not video_details.get("items"):
                    continue
                
                video_info = video_details["items"][0]
                
                # Create video object
                video = Video(
                    youtube_id=video_id,
                    title=video_info["snippet"]["title"],
                    description=video_info["snippet"]["description"],
                    channel_id=video_info["snippet"]["channelId"],
                    channel_title=video_info["snippet"]["channelTitle"],
                    published_at=datetime.fromisoformat(
                        video_info["snippet"]["publishedAt"].replace("Z", "+00:00")
                    ),
                    duration=self._parse_duration(video_info["contentDetails"]["duration"]),
                    thumbnail_url=video_info["snippet"]["thumbnails"]["high"]["url"],
                    status=VideoStatus.NEW
                )
                
                videos.append(video)
            
            # Check if there are more pages
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        
        return videos
    
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse ISO 8601 duration format to timedelta
        
        Args:
            duration_str: ISO 8601 duration format (e.g., 'PT1H30M15S')
            
        Returns:
            Equivalent timedelta object
        """
        import re
        
        hours = 0
        minutes = 0
        seconds = 0
        
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)