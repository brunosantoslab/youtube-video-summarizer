# api/infrastructure/external/youtube/client.py
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import httpx
from httpx import Response

from config import get_settings
from infrastructure.caching.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class YouTubeApiClient:
    """Client for YouTube Data API v3"""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self, api_key: Optional[str] = None, redis_cache: Optional[RedisCache] = None):
        self.api_key = api_key or get_settings().youtube_api_key
        self.redis_cache = redis_cache
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def _get(self, endpoint: str, params: Dict[str, Any] = None) -> dict:
        """Make a GET request to the YouTube API with caching"""
        if params is None:
            params = {}
        params["key"] = self.api_key
        
        cache_key = f"youtube:{endpoint}:{json.dumps(params, sort_keys=True)}"
        
        # Try to get from cache
        if self.redis_cache:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
        # Make request
        url = f"{self.BASE_URL}/{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result
        if self.redis_cache:
            # Cache for 1 hour by default
            await self.redis_cache.set(cache_key, json.dumps(data), ex=3600)
        
        return data
    
    async def get_subscriptions(
        self, access_token: str, page_token: Optional[str] = None, max_results: int = 50
    ) -> dict:
        """Get user subscriptions"""
        params = {
            "part": "snippet",
            "mine": "true",
            "maxResults": max_results,
        }
        if page_token:
            params["pageToken"] = page_token
        
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.BASE_URL}/subscriptions"
        
        cache_key = f"youtube:subscriptions:{access_token}:{json.dumps(params, sort_keys=True)}"
        
        # Try to get from cache
        if self.redis_cache:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
        # Make request
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result for a shorter time (15 min) since it's user-specific
        if self.redis_cache:
            await self.redis_cache.set(cache_key, json.dumps(data), ex=900)
        
        return data
    
    async def get_videos_for_channel(
        self, channel_id: str, published_after: Optional[datetime] = None, page_token: Optional[str] = None, max_results: int = 50
    ) -> dict:
        """Get videos for a specific channel"""
        params = {
            "part": "snippet,contentDetails",
            "channelId": channel_id,
            "order": "date",
            "maxResults": max_results,
            "type": "video"
        }
        
        if published_after:
            # Format datetime to RFC 3339 format
            params["publishedAfter"] = published_after.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if page_token:
            params["pageToken"] = page_token
        
        return await self._get("search", params)
    
    async def get_video_details(self, video_id: str) -> dict:
        """Get details for a specific video"""
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id
        }
        
        return await self._get("videos", params)
    
    async def get_video_captions(self, video_id: str, language_code: str = "en") -> Optional[str]:
        """Get captions for a video if available"""
        try:
            # First get the caption tracks for the video
            params = {
                "part": "snippet",
                "videoId": video_id
            }
            
            captions_data = await self._get("captions", params)
            
            # Find the requested language
            caption_id = None
            for item in captions_data.get("items", []):
                if item["snippet"]["language"] == language_code:
                    caption_id = item["id"]
                    break
            
            if not caption_id:
                return None
            
            # Now get the actual captions
            url = f"{self.BASE_URL}/captions/{caption_id}"
            params = {"tfmt": "srt", "key": self.api_key}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            return response.text
        
        except Exception as e:
            logger.error(f"Error fetching captions for video {video_id}: {str(e)}")
            return None