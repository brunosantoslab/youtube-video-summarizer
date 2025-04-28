# api/application/dtos/auth/auth_dtos.py
from typing import Optional
from pydantic import BaseModel, Field


class YouTubeAuthUrlResponse(BaseModel):
    """Response DTO for getting YouTube auth URL"""
    auth_url: str
    

class YouTubeCallbackRequest(BaseModel):
    """Request DTO for YouTube OAuth callback"""
    code: str
    state: str


class YouTubeCallbackResponse(BaseModel):
    """Response DTO for YouTube OAuth callback"""
    success: bool
    redirect_path: str
    error_message: Optional[str] = None


class YouTubeAuthStatusResponse(BaseModel):
    """Response DTO for checking YouTube auth status"""
    authenticated: bool
    scopes: Optional[list] = None


class RevokeAccessRequest(BaseModel):
    """Request DTO for revoking access"""
    user_id: str
    provider: str = Field(default="youtube")