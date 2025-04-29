# api/presentation/routes/auth/youtube_auth_routes.py
import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.responses import RedirectResponse

from application.dtos.auth import (
    YouTubeAuthUrlResponse,
    YouTubeCallbackResponse,
    YouTubeAuthStatusResponse,
    RevokeAccessRequest
)
from application.services.auth import AuthenticationService
from infrastructure.auth import YouTubeOAuthService
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory

router = APIRouter(prefix="/api/auth/youtube", tags=["YouTube Authentication"])


# Dependencies
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


@router.get("/auth-url", response_model=YouTubeAuthUrlResponse)
async def get_auth_url(
    user_id: str,
    redirect_path: str = "/",
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Get the YouTube authentication URL"""
    try:
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(user_id)
        
        # Get the auth URL
        auth_url = auth_service.get_youtube_auth_url(user_uuid, redirect_path)
        
        return YouTubeAuthUrlResponse(auth_url=auth_url)
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auth URL: {str(e)}"
        )


@router.get("/callback", response_model=YouTubeCallbackResponse)
async def oauth_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Handle YouTube OAuth callback"""
    try:
        # Process the callback
        success, redirect_path = await auth_service.handle_youtube_callback(code, state)
        
        if success:
            # Redirect to the specified path if successful
            response = RedirectResponse(url=redirect_path)
            return response
        else:
            # Return error response
            return YouTubeCallbackResponse(
                success=False,
                redirect_path="/error",
                error_message="Failed to authenticate with YouTube"
            )
    
    except Exception as e:
        return YouTubeCallbackResponse(
            success=False,
            redirect_path="/error",
            error_message=f"Authentication error: {str(e)}"
        )


@router.get("/status", response_model=YouTubeAuthStatusResponse)
async def check_auth_status(
    user_id: str,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Check if a user is authenticated with YouTube"""
    try:
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(user_id)
        
        # Check authentication status
        is_authenticated = auth_service.is_youtube_authenticated(user_uuid)
        
        # Get scopes if authenticated
        scopes = None
        if is_authenticated:
            token = await auth_service.get_youtube_token(user_uuid)
            if token:
                scopes = token.scope.split(" ")
        
        return YouTubeAuthStatusResponse(
            authenticated=is_authenticated,
            scopes=scopes
        )
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check auth status: {str(e)}"
        )


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_access(
    request: RevokeAccessRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Revoke YouTube access for a user"""
    try:
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(request.user_id)
        
        # Revoke access
        success = await auth_service.revoke_youtube_access(user_uuid)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="YouTube access not found for this user"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke access: {str(e)}"
        )