# api/infrastructure/youtube/youtube_videos_client.py
"""
Client for YouTube Videos API operations
Author: Bruno Santos
"""
from typing import Dict, Any, List, Optional, Union
import uuid
from datetime import datetime, timedelta

from domain.models.auth import OAuthToken
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService
from infrastructure.youtube.youtube_api_client import YouTubeAPIClient, RateLimitExceeded, AuthenticationError, APIRequestError


class YouTubeVideosClient(YouTubeAPIClient):
    """Client for YouTube Videos API operations"""
    
    def __init__(self, youtube_oauth_service: YouTubeOAuthService, api_key: Optional[str] = None):
        super().__init__(youtube_oauth_service, api_key)
    
    async def get_video_details(
        self,
        video_id: Union[str, List[str]],
        part: str = "snippet,contentDetails,statistics",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get details for one or more YouTube videos
        
        Args:
            video_id: Video ID or list of video IDs
            part: Parts to include in the response
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Video data
        """
        # Handle both single ID and list of IDs
        if isinstance(video_id, list):
            # YouTube API allows max 50 IDs per request
            video_ids = video_id[:50]
            video_id_param = ",".join(video_ids)
        else:
            video_id_param = video_id
        
        params = {
            "part": part,
            "id": video_id_param
        }
        
        try:
            # Use authenticated request if user provided
            if auth_user_id:
                return await self.make_authenticated_request(
                    user_id=auth_user_id,
                    endpoint="videos",
                    params=params
                )
            
            # Otherwise use API key
            return await self.make_api_key_request(
                endpoint="videos",
                params=params
            )
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for video details: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when fetching video details: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when fetching video details: {str(e)}")
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 25,
        published_after: Optional[datetime] = None,
        channel_id: Optional[str] = None,
        order: str = "relevance",
        all_pages: bool = False,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Search for YouTube videos
        
        Args:
            query: Search query
            max_results: Maximum results per page
            published_after: Only include videos published after this date
            channel_id: Only include videos from this channel
            order: Result ordering (relevance, date, rating, title, videoCount, viewCount)
            all_pages: Whether to fetch all pages of results
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Search results
        """
        params = {
            "part": "snippet",
            "maxResults": min(max_results, 50),  # YouTube API limit
            "q": query,
            "type": "video",
            "order": order
        }
        
        if published_after:
            # Format datetime to RFC 3339 timestamp
            params["publishedAfter"] = published_after.isoformat("T") + "Z"
        
        if channel_id:
            params["channelId"] = channel_id
        
        try:
            # Choose request method based on auth
            if auth_user_id:
                result = await self.make_authenticated_request(
                    user_id=auth_user_id,
                    endpoint="search",
                    params=params
                )
            else:
                result = await self.make_api_key_request(
                    endpoint="search",
                    params=params
                )
            
            # If all pages requested, fetch all pages
            if all_pages and self.extract_page_token(result):
                results = [result]
                page_token = self.extract_page_token(result)
                
                while page_token:
                    params["pageToken"] = page_token
                    
                    if auth_user_id:
                        next_page = await self.make_authenticated_request(
                            user_id=auth_user_id,
                            endpoint="search",
                            params=params
                        )
                    else:
                        next_page = await self.make_api_key_request(
                            endpoint="search",
                            params=params
                        )
                    
                    results.append(next_page)
                    page_token = self.extract_page_token(next_page)
                
                return self.build_paginated_results(results)
            
            return result
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for video search: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when searching videos: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when searching videos: {str(e)}")
    
    async def get_recent_videos_from_channel(
        self,
        channel_id: str,
        max_days: int = 7,
        max_results: int = 50,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get recent videos from a channel
        
        Args:
            channel_id: Channel ID
            max_days: Maximum age of videos in days
            max_results: Maximum results to return
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Video search results
        """
        published_after = datetime.now() - timedelta(days=max_days)
        
        return await self.search_videos(
            query="",
            max_results=max_results,
            published_after=published_after,
            channel_id=channel_id,
            order="date",  # Sort by date to get newest first
            all_pages=False,  # Only get first page to limit results
            auth_user_id=auth_user_id
        )
    
    async def get_videos_from_playlist(
        self,
        playlist_id: str,
        max_results: int = 50,
        all_pages: bool = False,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get videos from a playlist
        
        Args:
            playlist_id: Playlist ID
            max_results: Maximum results per page
            all_pages: Whether to fetch all pages of results
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Playlist items
        """
        params = {
            "part": "snippet,contentDetails",
            "maxResults": min(max_results, 50),  # YouTube API limit
            "playlistId": playlist_id
        }
        
        try:
            # Choose request method based on auth
            if auth_user_id:
                result = await self.make_authenticated_request(
                    user_id=auth_user_id,
                    endpoint="playlistItems",
                    params=params
                )
            else:
                result = await self.make_api_key_request(
                    endpoint="playlistItems",
                    params=params
                )
            
            # If all pages requested, fetch all pages
            if all_pages and self.extract_page_token(result):
                results = [result]
                page_token = self.extract_page_token(result)
                
                while page_token:
                    params["pageToken"] = page_token
                    
                    if auth_user_id:
                        next_page = await self.make_authenticated_request(
                            user_id=auth_user_id,
                            endpoint="playlistItems",
                            params=params
                        )
                    else:
                        next_page = await self.make_api_key_request(
                            endpoint="playlistItems",
                            params=params
                        )
                    
                    results.append(next_page)
                    page_token = self.extract_page_token(next_page)
                
                return self.build_paginated_results(results)
            
            return result
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for playlist items: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when fetching playlist items: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when fetching playlist items: {str(e)}")
