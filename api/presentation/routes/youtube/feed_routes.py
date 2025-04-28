# api/presentation/routes/youtube/feed_routes.py
"""
API routes for YouTube feed operations
Author: Bruno Santos
"""
import uuid
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from pydantic import BaseModel, Field

from application.services.youtube.feed_service import YouTubeFeedService
from application.services.auth import AuthenticationService
from infrastructure.youtube.youtube_api_service import YouTubeAPIService
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory


# DTOs
class SubscriptionResponse(BaseModel):
    """Response DTO for subscription data"""
    channel_id: str
    title: str
    description: str = ""
    thumbnail_url: str = ""


class VideoResponse(BaseModel):
    """Response DTO for video data"""
    video_id: str
    title: str
    description: str = ""
    channel_id: str = ""
    channel_title: str = ""
    published_at: str = ""
    thumbnail_url: str = ""


class FeedCheckResponse(BaseModel):
    """Response DTO for feed check"""
    success: bool
    user_id: str
    new_videos_count: int = 0
    monitored_at: str = ""
    error: str = ""


# Router
router = APIRouter(prefix="/api/youtube/feed", tags=["YouTube Feed"])


# Dependencies
def get_feed_service():
    """Get YouTube feed service"""
    db = get_db()
    repository_factory = get_repository_factory(db)
    user_repository = repository_factory.get(IUserRepository)
    video_repository = repository_factory.get(IVideoRepository)
    oauth_token_repository = repository_factory.get(IOAuthTokenRepository)
    
    youtube_oauth_service = YouTubeOAuthService(oauth_token_repository=oauth_token_repository)
    youtube_api_service = YouTubeAPIService(youtube_oauth_service=youtube_oauth_service)
    
    feed_service = YouTubeFeedService(
        youtube_api_service=youtube_api_service,
        user_repository=user_repository,
        video_repository=video_repository
    )
    
    try:
        yield feed_service
    finally:
        db.close()


def get_auth_service():
    """Get authentication service"""
    db = get_db()
    repository_factory = get_repository_factory(db)
    oauth_token_repository = repository_factory.get(IOAuthTokenRepository)
    
    youtube_oauth_service = YouTubeOAuthService(oauth_token_repository=oauth_token_repository)
    auth_service = AuthenticationService(
        youtube_oauth_service=youtube_oauth_service,
        oauth_token_repository=oauth_token_repository
    )
    
    try:
        yield auth_service
    finally:
        db.close()


# Routes
@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    user_id: str,
    feed_service: YouTubeFeedService = Depends(get_feed_service),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get all subscriptions for a user"""
    try:
        # Validate user_id
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user is authenticated with YouTube
        if not auth_service.is_youtube_authenticated(user_uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authenticated with YouTube"
            )
        
        # Get subscriptions
        subscriptions = await feed_service.get_user_subscriptions(user_uuid)
        
        # Map to response DTOs
        response = []
        for sub in subscriptions:
            snippet = sub.get("snippet", {})
            resource_id = snippet.get("resourceId", {})
            thumbnails = snippet.get("thumbnails", {})
            best_thumbnail = (
                thumbnails.get("high", {}) or 
                thumbnails.get("medium", {}) or 
                thumbnails.get("default", {})
            )
            
            response.append(SubscriptionResponse(
                channel_id=resource_id.get("channelId", ""),
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                thumbnail_url=best_thumbnail.get("url", "")
            ))
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscriptions: {str(e)}"
        )


@router.get("/recent-videos", response_model=List[VideoResponse])
async def get_recent_videos(
    user_id: str,
    max_days: int = Query(7, ge=1, le=30),
    max_videos: int = Query(20, ge=1, le=50),
    feed_service: YouTubeFeedService = Depends(get_feed_service),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get recent videos from subscriptions"""
    try:
        # Validate user_id
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user is authenticated with YouTube
        if not auth_service.is_youtube_authenticated(user_uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authenticated with YouTube"
            )
        
        # Get recent videos
        videos = await feed_service.get_recent_videos_from_subscriptions(
            user_id=user_uuid,
            max_days=max_days,
            max_videos=max_videos
        )
        
        # Map to response DTOs
        response = []
        for video in videos:
            snippet = video.get("snippet", {})
            video_id = video.get("id", {}).get("videoId", "")
            thumbnails = snippet.get("thumbnails", {})
            best_thumbnail = (
                thumbnails.get("high", {}) or 
                thumbnails.get("medium", {}) or 
                thumbnails.get("default", {})
            )
            
            response.append(VideoResponse(
                video_id=video_id,
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                channel_id=snippet.get("channelId", ""),
                channel_title=snippet.get("channelTitle", ""),
                published_at=snippet.get("publishedAt", ""),
                thumbnail_url=best_thumbnail.get("url", "")
            ))
        
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent videos: {str(e)}"
        )


@router.get("/video/{video_id}")
async def get_video_details(
    video_id: str,
    user_id: str,
    with_transcript: bool = False,
    language_code: str = "en",
    feed_service: YouTubeFeedService = Depends(get_feed_service),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get details for a specific video"""
    try:
        # Validate user_id
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user is authenticated with YouTube
        if not auth_service.is_youtube_authenticated(user_uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authenticated with YouTube"
            )
        
        # Get video details with transcript if requested
        if with_transcript:
            result = await feed_service.get_video_with_transcript(
                video_id=video_id,
                language_code=language_code,
                user_id=user_uuid
            )
            return result
        else:
            video_details = await feed_service.get_video_details(
                video_id=video_id,
                user_id=user_uuid
            )
            
            if not video_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Video {video_id} not found"
                )
            
            return video_details
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video details: {str(e)}"
        )


@router.get("/monitor/{user_id}", response_model=FeedCheckResponse)
async def monitor_feed(
    user_id: str,
    feed_service: YouTubeFeedService = Depends(get_feed_service),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Monitor feed for new videos"""
    try:
        # Validate user_id
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user is authenticated with YouTube
        if not auth_service.is_youtube_authenticated(user_uuid):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authenticated with YouTube"
            )
        
        # Monitor feed
        result = await feed_service.monitor_user_feed(user_uuid)
        
        if not result["success"]:
            if "not found" in result.get("error", ""):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        return FeedCheckResponse(
            success=result["success"],
            user_id=result["user_id"],
            new_videos_count=result["new_videos_count"],
            monitored_at=result["monitored_at"],
            error=""
        )
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to monitor feed: {str(e)}"
        )
