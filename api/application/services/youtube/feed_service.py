# api/application/services/youtube/feed_service.py
"""
Service for monitoring and managing YouTube video feeds
Author: Bruno Santos
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from domain.models.user import User
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from infrastructure.youtube.youtube_api_service import YouTubeAPIService


logger = logging.getLogger(__name__)


class YouTubeFeedService:
    """Service for handling YouTube feed operations"""
    
    def __init__(
        self,
        youtube_api_service: YouTubeAPIService,
        user_repository: IUserRepository,
        video_repository: IVideoRepository
    ):
        self.youtube_api_service = youtube_api_service
        self.user_repository = user_repository
        self.video_repository = video_repository
    
    async def get_user_subscriptions(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Get all subscriptions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of subscription data
        """
        return await self.youtube_api_service.get_user_subscriptions(user_id, all_pages=True)
    
    async def get_recent_videos_from_subscriptions(
        self,
        user_id: uuid.UUID,
        max_days: int = 7,
        max_videos: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent videos from all subscribed channels
        
        Args:
            user_id: User ID
            max_days: Maximum age of videos in days
            max_videos: Maximum number of videos to return
            
        Returns:
            List of recent videos from subscriptions
        """
        return await self.youtube_api_service.get_recent_videos_from_subscriptions(
            user_id=user_id,
            max_days=max_days,
            max_results_per_channel=5,
            max_total_results=max_videos
        )
    
    async def get_channel_details(
        self,
        channel_id: str,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get details for a channel
        
        Args:
            channel_id: Channel ID
            user_id: Optional user ID for authentication
            
        Returns:
            Channel details or None if not found
        """
        return await self.youtube_api_service.get_channel_details(
            channel_id=channel_id,
            auth_user_id=user_id
        )
    
    async def get_video_details(
        self,
        video_id: str,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get details for a video
        
        Args:
            video_id: Video ID
            user_id: Optional user ID for authentication
            
        Returns:
            Video details or None if not found
        """
        result = await self.youtube_api_service.get_video_details(
            video_id=video_id,
            auth_user_id=user_id
        )
        
        return result[0] if result else None
    
    async def get_video_transcript(
        self,
        video_id: str,
        language_code: str = "en",
        user_id: uuid.UUID = None
    ) -> Optional[str]:
        """
        Get transcript for a video
        
        Args:
            video_id: Video ID
            language_code: Language code (ISO 639-1)
            user_id: User ID for authentication (required for captions)
            
        Returns:
            Transcript text or None if not available
        """
        if not user_id:
            logger.warning("Cannot get transcript without authenticated user")
            return None
        
        return await self.youtube_api_service.get_video_transcript(
            video_id=video_id,
            language_code=language_code,
            auth_user_id=user_id
        )
    
    async def get_video_with_transcript(
        self,
        video_id: str,
        language_code: str = "en",
        user_id: uuid.UUID = None
    ) -> Dict[str, Any]:
        """
        Get both video details and transcript
        
        Args:
            video_id: Video ID
            language_code: Language code for transcript
            user_id: User ID for authentication
            
        Returns:
            Dictionary with video_details and transcript
        """
        video_details, transcript = await self.youtube_api_service.get_video_with_transcript(
            video_id=video_id,
            language_code=language_code,
            auth_user_id=user_id
        )
        
        return {
            "video_details": video_details,
            "transcript": transcript
        }
    
    async def check_for_new_videos(self, user_id: uuid.UUID, days: int = 1) -> List[Dict[str, Any]]:
        """
        Check for new videos from subscriptions within the specified days
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of new videos
        """
        # Get recent videos
        recent_videos = await self.get_recent_videos_from_subscriptions(
            user_id=user_id,
            max_days=days,
            max_videos=50
        )
        
        # Extract video IDs
        video_ids = [
            video.get("id", {}).get("videoId") 
            for video in recent_videos 
            if "id" in video and "videoId" in video.get("id", {})
        ]
        
        # Filter out videos that we've already processed
        new_videos = []
        for video in recent_videos:
            video_id = video.get("id", {}).get("videoId")
            if video_id and not self.video_repository.exists_by_youtube_id(video_id):
                new_videos.append(video)
        
        return new_videos
    
    async def process_new_videos(self, user_id: uuid.UUID) -> int:
        """
        Process new videos for a user, adding them to processing queue
        
        Args:
            user_id: User ID
            
        Returns:
            Number of new videos found
        """
        # Check for new videos in last day
        new_videos = await self.check_for_new_videos(user_id, days=1)
        
        if not new_videos:
            return 0
        
        # Add each new video to processing queue
        # Note: This would typically dispatch to a task queue like Celery
        for video in new_videos:
            video_id = video.get("id", {}).get("videoId")
            if not video_id:
                continue
                
            # Get full video details
            video_details = await self.get_video_details(video_id, user_id)
            if not video_details:
                logger.warning(f"Could not get details for video {video_id}")
                continue
                
            # Queue video for processing
            # In a real implementation, this would dispatch to a background task
            logger.info(f"Queueing video {video_id} for processing")
            
            # For now, we'll just log it
            # self.queue_video_for_processing(user_id, video_details)
        
        return len(new_videos)
    
    async def monitor_user_feed(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Monitor a user's feed for new videos
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with monitoring results
        """
        try:
            # Get user from repository
            user = self.user_repository.get_by_id(user_id)
            
            # Handle case where user is not found
            if not user:
                error_message = f"User {user_id} not found"
                logger.error(error_message)
                return {
                    "success": False,
                    "error": error_message
                }
            
            # Check for new videos
            new_videos_count = await self.process_new_videos(user_id)
            
            # Return successful response
            return {
                "success": True,
                "user_id": str(user_id),
                "new_videos_count": new_videos_count,
                "monitored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Handle any exceptions
            error_message = str(e)
            logger.error(f"Error monitoring feed for user {user_id}: {error_message}")
            
            return {
                "success": False,
                "error": error_message
            }
