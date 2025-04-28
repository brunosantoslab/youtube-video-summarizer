# api/infrastructure/youtube/youtube_channels_client.py
"""
Client for YouTube Channels API operations, including subscriptions
Author: Bruno Santos
"""
from typing import Dict, Any, List, Optional
import uuid

from domain.models.auth import OAuthToken
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService
from infrastructure.youtube.youtube_api_client import YouTubeAPIClient, RateLimitExceeded, AuthenticationError, APIRequestError


class YouTubeChannelsClient(YouTubeAPIClient):
    """Client for YouTube Channels API operations"""
    
    def __init__(self, youtube_oauth_service: YouTubeOAuthService, api_key: Optional[str] = None):
        super().__init__(youtube_oauth_service, api_key)
    
    async def get_subscriptions(
        self,
        user_id: uuid.UUID,
        max_results: int = 50,
        part: str = "snippet,contentDetails",
        mine: bool = True,
        order: str = "alphabetical",
        all_pages: bool = False
    ) -> Dict[str, Any]:
        """
        Get a user's YouTube subscriptions
        
        Args:
            user_id: User ID to get subscriptions for
            max_results: Maximum results per page
            part: Parts to include in the response
            mine: Get the authenticated user's subscriptions
            order: Result ordering (alphabetical, relevance, unread)
            all_pages: Whether to fetch all pages of results
            
        Returns:
            Subscription data
        """
        params = {
            "part": part,
            "maxResults": min(max_results, 50),  # YouTube API limit
            "order": order
        }
        
        if mine:
            params["mine"] = "true"
        
        try:
            result = await self.make_authenticated_request(
                user_id=user_id,
                endpoint="subscriptions",
                params=params
            )
            
            # If all pages requested, fetch all pages
            if all_pages and self.extract_page_token(result):
                results = [result]
                page_token = self.extract_page_token(result)
                
                while page_token:
                    params["pageToken"] = page_token
                    next_page = await self.make_authenticated_request(
                        user_id=user_id,
                        endpoint="subscriptions",
                        params=params
                    )
                    results.append(next_page)
                    page_token = self.extract_page_token(next_page)
                
                return self.build_paginated_results(results)
            
            return result
        
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for subscription access: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when fetching subscriptions: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when fetching subscriptions: {str(e)}")
    
    async def get_channel_details(
        self,
        channel_id: str,
        part: str = "snippet,contentDetails,statistics",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get details for a YouTube channel
        
        Args:
            channel_id: Channel ID
            part: Parts to include in the response
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Channel data
        """
        params = {
            "part": part,
            "id": channel_id
        }
        
        try:
            # Use authenticated request if user provided
            if auth_user_id:
                return await self.make_authenticated_request(
                    user_id=auth_user_id,
                    endpoint="channels",
                    params=params
                )
            
            # Otherwise use API key
            return await self.make_api_key_request(
                endpoint="channels",
                params=params
            )
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for channel details: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when fetching channel details: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when fetching channel details: {str(e)}")
    
    async def get_my_channel(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get the authenticated user's channel
        
        Args:
            user_id: User ID
            
        Returns:
            Channel data
        """
        params = {
            "part": "snippet,contentDetails,statistics",
            "mine": "true"
        }
        
        try:
            return await self.make_authenticated_request(
                user_id=user_id,
                endpoint="channels",
                params=params
            )
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for my channel: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when fetching my channel: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when fetching my channel: {str(e)}")
