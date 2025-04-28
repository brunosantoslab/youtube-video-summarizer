# api/infrastructure/youtube/youtube_captions_client.py
"""
Client for YouTube Captions API operations
Author: Bruno Santos
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import uuid
import httpx
import re
import xml.etree.ElementTree as ET
from html import unescape

from domain.models.auth import OAuthToken
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService
from infrastructure.youtube.youtube_api_client import YouTubeAPIClient, RateLimitExceeded, AuthenticationError, APIRequestError


logger = logging.getLogger(__name__)


class YouTubeCaptionsClient(YouTubeAPIClient):
    """Client for YouTube Captions API operations"""
    
    def __init__(self, youtube_oauth_service: YouTubeOAuthService, api_key: Optional[str] = None):
        super().__init__(youtube_oauth_service, api_key)
    
    async def list_captions(
        self,
        video_id: str,
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        List available captions for a video
        
        Args:
            video_id: Video ID
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Caption list data
        """
        params = {
            "part": "snippet",
            "videoId": video_id
        }
        
        try:
            # YouTube Captions API requires authentication
            if auth_user_id:
                return await self.make_authenticated_request(
                    user_id=auth_user_id,
                    endpoint="captions",
                    params=params
                )
            else:
                # Fall back to API key for listing (may not work for all videos)
                return await self.make_api_key_request(
                    endpoint="captions",
                    params=params
                )
            
        except AuthenticationError as e:
            raise AuthenticationError(f"Failed to authenticate for captions list: {str(e)}")
        
        except RateLimitExceeded as e:
            raise RateLimitExceeded(f"Rate limit exceeded when listing captions: {str(e)}")
        
        except APIRequestError as e:
            raise APIRequestError(f"API error when listing captions: {str(e)}")
    
    async def download_caption(
        self,
        caption_id: str,
        auth_user_id: uuid.UUID,
        format: str = "srt"
    ) -> str:
        """
        Download caption track content
        
        Args:
            caption_id: Caption track ID
            auth_user_id: User ID for authentication
            format: Caption format (srt, ttml, vtt)
            
        Returns:
            Caption content as string
        """
        params = {
            "tfmt": format
        }
        
        try:
            # Get user's token
            token = await self.youtube_oauth_service.get_user_token(auth_user_id)
            
            if not token:
                raise AuthenticationError("No valid token found for user")
            
            # Make direct request to download caption
            url = f"{self.BASE_URL}/captions/{caption_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={"Authorization": token.authorization_header}
                )
                
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed for caption download")
                
                if response.status_code == 403:
                    error_data = response.json() if response.content else {"error": "Access forbidden"}
                    if "quotaExceeded" in str(error_data):
                        raise RateLimitExceeded("YouTube API quota exceeded")
                    raise APIRequestError(f"Access forbidden for caption download: {error_data}")
                
                if response.status_code == 429:
                    raise RateLimitExceeded("YouTube API rate limit exceeded")
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    raise APIRequestError(f"API request failed with status {response.status_code}: {error_data}")
                
                return response.text
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIRequestError(f"Request failed: {str(e)}")
    
    async def find_caption_for_language(
        self,
        video_id: str,
        language_code: str = "en",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[str], bool]:
        """
        Find appropriate caption track for a language
        
        Args:
            video_id: Video ID
            language_code: Language code (ISO 639-1)
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Tuple of (caption_id, is_auto_generated)
        """
        try:
            captions_list = await self.list_captions(video_id, auth_user_id)
            items = captions_list.get("items", [])
            
            # Try to find exact match for language
            exact_matches = [
                item for item in items 
                if item["snippet"]["language"] == language_code
            ]
            
            # Prioritize manual captions over auto-generated
            manual_captions = [
                item for item in exact_matches 
                if not item["snippet"].get("trackKind") == "ASR"  # ASR = Auto-generated
            ]
            
            # If we have manual captions, use the first one
            if manual_captions:
                return manual_captions[0]["id"], False
            
            # If we have auto-generated captions, use the first one
            if exact_matches:
                return exact_matches[0]["id"], True
            
            # No matches found
            return None, False
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error finding caption for language: {str(e)}")
            return None, False
    
    async def get_transcript(
        self,
        video_id: str,
        language_code: str = "en",
        auth_user_id: Optional[uuid.UUID] = None
    ) -> Optional[str]:
        """
        Get transcript text for a video
        
        Args:
            video_id: Video ID
            language_code: Language code (ISO 639-1)
            auth_user_id: Optional user ID for authenticated request
            
        Returns:
            Transcript text or None if not available
        """
        # Need auth user ID for downloading captions
        if not auth_user_id:
            logger.warning("Cannot download captions without authenticated user")
            return None
        
        # Find appropriate caption track
        caption_id, is_auto_generated = await self.find_caption_for_language(
            video_id, language_code, auth_user_id
        )
        
        if not caption_id:
            return None
        
        try:
            # Download the caption in TTML format (XML-based)
            caption_content = await self.download_caption(
                caption_id, auth_user_id, format="ttml"
            )
            
            # Parse the TTML content to extract text
            return self._parse_ttml_transcript(caption_content)
            
        except (AuthenticationError, RateLimitExceeded, APIRequestError) as e:
            logger.error(f"Error getting transcript: {str(e)}")
            return None
    
    def _parse_ttml_transcript(self, ttml_content: str) -> str:
        """
        Parse TTML (Timed Text Markup Language) content to extract transcript text
        
        Args:
            ttml_content: TTML content as string
            
        Returns:
            Plain text transcript
        """
        try:
            # Parse XML
            root = ET.fromstring(ttml_content)
            
            # Find namespace
            ns = {"tt": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
            
            # Find all text elements
            if ns:
                text_elements = root.findall(".//tt:p", ns)
            else:
                text_elements = root.findall(".//p")
            
            # Extract text from each element
            transcript_parts = []
            for elem in text_elements:
                # Get text content, including nested elements
                text = "".join(elem.itertext()).strip()
                
                # Skip empty lines
                if not text:
                    continue
                
                # Unescape HTML entities
                text = unescape(text)
                
                # Clean up text (remove extra whitespace, etc.)
                text = re.sub(r'\s+', ' ', text).strip()
                
                transcript_parts.append(text)
            
            # Join all parts with newlines
            return "\n".join(transcript_parts)
            
        except Exception as e:
            logger.error(f"Error parsing TTML transcript: {str(e)}")
            return ""
    
    def _parse_srt_transcript(self, srt_content: str) -> str:
        """
        Parse SRT (SubRip Text) content to extract transcript text
        
        Args:
            srt_content: SRT content as string
            
        Returns:
            Plain text transcript
        """
        try:
            lines = srt_content.strip().split("\n")
            transcript_parts = []
            
            for i, line in enumerate(lines):
                # Skip empty lines, index numbers, and timestamp lines
                if not line.strip() or line.strip().isdigit() or "-->" in line:
                    continue
                
                # Clean up text
                text = unescape(line.strip())
                text = re.sub(r'\s+', ' ', text).strip()
                
                if text:
                    transcript_parts.append(text)
            
            # Join all parts with newlines
            return "\n".join(transcript_parts)
            
        except Exception as e:
            logger.error(f"Error parsing SRT transcript: {str(e)}")
            return ""
