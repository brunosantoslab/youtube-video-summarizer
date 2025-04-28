# api/infrastructure/youtube/youtube_api_client.py
"""
Base client for YouTube API operations
Author: Bruno Santos
"""
import logging
import json
from typing import Dict, Any, List, Optional, Union
import httpx
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from config import get_settings
from domain.models.auth import OAuthToken
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService


logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when YouTube API rate limit is exceeded."""
    pass


class AuthenticationError(Exception):
    """Exception raised when authentication with YouTube API fails."""
    pass


class APIRequestError(Exception):
    """Exception raised when a request to YouTube API fails."""
    pass


class YouTubeAPIClient:
    """Base client for YouTube API requests with authentication and rate limiting"""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(
        self,
        youtube_oauth_service: YouTubeOAuthService,
        api_key: Optional[str] = None
    ):
        self.youtube_oauth_service = youtube_oauth_service
        self.api_key = api_key or get_settings().youtube_api_key
        self.settings = get_settings()
    
    async def _make_authorized_request(
        self,
        token: OAuthToken,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an authorized request to the YouTube API
        
        Args:
            token: OAuth token for authorization
            endpoint: API endpoint (relative to base URL)
            method: HTTP method
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            API response data
        """
        url = f"{self.BASE_URL}/{endpoint}"
        request_headers = {
            "Authorization": token.authorization_header,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(
                        url,
                        params=params,
                        headers=request_headers
                    )
                elif method == "POST":
                    response = await client.post(
                        url,
                        params=params,
                        json=data,
                        headers=request_headers
                    )
                elif method == "PUT":
                    response = await client.put(
                        url,
                        params=params,
                        json=data,
                        headers=request_headers
                    )
                elif method == "DELETE":
                    response = await client.delete(
                        url,
                        params=params,
                        headers=request_headers
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed")
                
                if response.status_code == 403:
                    error_data = response.json()
                    if "quotaExceeded" in str(error_data):
                        raise RateLimitExceeded("YouTube API quota exceeded")
                    raise APIRequestError(f"Access forbidden: {error_data}")
                
                if response.status_code == 429:
                    raise RateLimitExceeded("YouTube API rate limit exceeded")
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    raise APIRequestError(f"API request failed with status {response.status_code}: {error_data}")
                
                return response.json() if response.content else {}
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIRequestError(f"Request failed: {str(e)}")
    
    async def make_authenticated_request(
        self,
        user_id: str,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the YouTube API using user's token
        
        Args:
            user_id: User ID to get token for
            endpoint: API endpoint (relative to base URL)
            method: HTTP method
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            API response data
        """
        # Get the user's token
        token = await self.youtube_oauth_service.get_user_token(user_id)
        
        if not token:
            raise AuthenticationError("No valid token found for user")
        
        return await self._make_authorized_request(
            token=token,
            endpoint=endpoint,
            method=method,
            params=params,
            data=data,
            headers=headers
        )
    
    async def make_api_key_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the YouTube API using API key
        
        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            method: HTTP method
            data: Request body data
            headers: Additional headers
            
        Returns:
            API response data
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        request_params = params or {}
        request_params["key"] = self.api_key
        
        request_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(
                        url,
                        params=request_params,
                        headers=request_headers
                    )
                elif method == "POST":
                    response = await client.post(
                        url,
                        params=request_params,
                        json=data,
                        headers=request_headers
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method for API key request: {method}")
                
                if response.status_code == 403:
                    error_data = response.json()
                    if "quotaExceeded" in str(error_data):
                        raise RateLimitExceeded("YouTube API quota exceeded")
                    raise APIRequestError(f"Access forbidden: {error_data}")
                
                if response.status_code == 429:
                    raise RateLimitExceeded("YouTube API rate limit exceeded")
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    raise APIRequestError(f"API request failed with status {response.status_code}: {error_data}")
                
                return response.json() if response.content else {}
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIRequestError(f"Request failed: {str(e)}")
    
    def extract_page_token(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract next page token from API response
        
        Args:
            result: API response data
            
        Returns:
            Next page token or None if no more pages
        """
        return result.get("nextPageToken")
    
    def build_paginated_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build combined results from paginated API responses
        
        Args:
            results: List of API response data
            
        Returns:
            Combined result data
        """
        if not results:
            return {}
        
        # Start with first result
        combined = results[0].copy()
        
        # Combine items from all results
        items_key = next((k for k in results[0].keys() if k.endswith("Items") or k == "items"), None)
        
        if not items_key:
            return combined
        
        combined_items = []
        for result in results:
            combined_items.extend(result.get(items_key, []))
        
        combined[items_key] = combined_items
        
        # Remove page token as we've fetched all pages
        if "nextPageToken" in combined:
            del combined["nextPageToken"]
        
        return combined
