# api/infrastructure/youtube/youtube_api_service.py
"""
Comprehensive service for YouTube API operations
Author: Bruno Santos
"""
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import uuid
from datetime import datetime, timedelta

from domain.models.auth import OAuthToken
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService
from infrastructure.youtube.youtube_api_client import RateLimitExceeded, AuthenticationError, APIRequestError
from infrastructure.youtube.youtube_channels_client import YouTubeChannelsClient
from infrastructure.youtube.youtube_videos_client import YouTubeVideosClient
from infrastructure.youtube.youtube_captions_client import YouTubeCaptionsClient


logger = logging.getLogger(__name__)


class YouTubeAPIService:
    """Comprehensive service for YouTube API operations"""
    
    def __init__(self, youtube_oauth_service: YouTubeOAuthService, api_key: Optional[str] = None):
        self.youtube_oauth_service = youtube_oauth_service
        self.api_key = api_key
        
        # Initialize specialized clients
        self.channels_client = YouTubeChannelsClient(youtube_oauth_service, api_key)
        self.videos_client = YouTubeVideosClient(youtube_oauth_service, api_key)
        self.captions_client = YouTubeCaptionsClient(youtube_oauth_service, api_key)
    
    # Subscription and Channel Methods
    
    async def get_user_subscriptions(
        self, 
        user_id: uuid.UUID, 
        all_pages: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all subscriptions for a user
        
        Args:
            user_id: User ID
            all_pages: Whether to fetch all pages
            
        Returns:
            List of subscription data
        """
        try:
            result = await self.channels_client.get_subscriptions(
                user_id=user_id,
                max_results=50,
                all_pages=all_pages
            )
            
            return result.get("items", [])
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting user subscriptions: {str(e)}")
            return []
    
    async def get_channel_details(
        self,
        channel_id: str,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get details for a channel
        
        Args:
            channel_id: Channel ID
            auth_user_id: Optional user ID for authentication
            
        Returns:
            Channel details or None if not found
        """
        try:
            result = await self.channels_client.get_channel_details(
                channel_id=channel_id,
                auth_user_id=auth_user_id
            )
            
            items = result.get("items", [])
            return items[0] if items else None
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting channel details: {str(e)}")
            return None
    
    # Video Methods
    
    async def get_video_details(
        self,
        video_id: Union[str, List[str]],
        auth_user_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get details for one or more videos
        
        Args:
            video_id: Video ID or list of video IDs
            auth_user_id: Optional user ID for authentication
            
        Returns:
            List of video details
        """
        try:
            result = await self.videos_client.get_video_details(
                video_id=video_id,
                auth_user_id=auth_user_id
            )
            
            return result.get("items", [])
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting video details: {str(e)}")
            return []
    
    async def get_recent_videos_from_channel(
        self,
        channel_id: str,
        max_days: int = 7,
        max_results: int = 50,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent videos from a channel
        
        Args:
            channel_id: Channel ID
            max_days: Maximum age of videos in days
            max_results: Maximum results to return
            auth_user_id: Optional user ID for authentication
            
        Returns:
            List of recent videos
        """
        try:
            result = await self.videos_client.get_recent_videos_from_channel(
                channel_id=channel_id,
                max_days=max_days,
                max_results=max_results,
                auth_user_id=auth_user_id
            )
            
            return result.get("items", [])
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting recent videos: {str(e)}")
            return []
    
    # Transcript Methods
    
    async def get_video_transcript(
        self,
        video_id: str,
        language_code: str = "en",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Optional[str]:
        """
        Get transcript for a video
        
        Args:
            video_id: Video ID
            language_code: Language code (ISO 639-1)
            auth_user_id: User ID for authentication (required for captions)
            
        Returns:
            Transcript text or None if not available
        """
        if not auth_user_id:
            logger.warning("Cannot get transcript without authenticated user")
            return None
        
        try:
            return await self.captions_client.get_transcript(
                video_id=video_id,
                language_code=language_code,
                auth_user_id=auth_user_id
            )
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting video transcript: {str(e)}")
            return None
    
    # Combined Operations
    
    async def get_recent_videos_from_subscriptions(
        self,
        user_id: uuid.UUID,
        max_days: int = 7,
        max_results_per_channel: int = 5,
        max_total_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent videos from all subscribed channels
        
        Args:
            user_id: User ID
            max_days: Maximum age of videos in days
            max_results_per_channel: Maximum results per channel
            max_total_results: Maximum total results
            
        Returns:
            List of recent videos from subscriptions
        """
        try:
            # Get user's subscriptions
            subscriptions = await self.channels_client.get_subscriptions(
                user_id=user_id,
                all_pages=True
            )
            
            subscriptions_items = subscriptions.get("items", [])
            if not subscriptions_items:
                return []
            
            # Extract channel IDs
            channel_ids = [
                sub["snippet"]["resourceId"]["channelId"]
                for sub in subscriptions_items
                if "resourceId" in sub.get("snippet", {})
            ]
            
            # Get recent videos for each channel
            all_videos = []
            for channel_id in channel_ids:
                channel_videos = await self.get_recent_videos_from_channel(
                    channel_id=channel_id,
                    max_days=max_days,
                    max_results=max_results_per_channel,
                    auth_user_id=user_id
                )
                
                all_videos.extend(channel_videos)
                
                # Stop if we've reached the maximum total results
                if len(all_videos) >= max_total_results:
                    break
            
            # Sort by published date (newest first)
            all_videos.sort(
                key=lambda v: v.get("snippet", {}).get("publishedAt", ""),
                reverse=True
            )
            
            # Limit to max_total_results
            return all_videos[:max_total_results]
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting videos from subscriptions: {str(e)}")
            return []
    
    async def get_video_with_transcript(
        self,
        video_id: str,
        language_code: str = "en",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get both video details and transcript
        
        Args:
            video_id: Video ID
            language_code: Language code for transcript
            auth_user_id: User ID for authentication
            
        Returns:
            Tuple of (video_details, transcript)
        """
        try:
            # Get video details
            video_details_list = await self.get_video_details(video_id, auth_user_id)
            
            # Get transcript
            transcript = await self.get_video_transcript(video_id, language_code, auth_user_id)
            
            # Extract first video if available
            video_details = video_details_list[0] if video_details_list else None
            
            return video_details, transcript
        except Exception as e:
            logger.error(f"Error getting video with transcript: {str(e)}")
            return None, None
