from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..views.session_views import SessionViews
from ..models.session import SessionCreate, SessionResponse, SessionInfo
from ..core.dependencies import get_session_views

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
async def create_session(
    session_create: SessionCreate,
    session_views: SessionViews = Depends(get_session_views)
):
    """Create new IDE session"""
    return await session_views.create_session(session_create)

@router.get("/", response_model=List[SessionInfo])
async def get_all_sessions(
    session_views: SessionViews = Depends(get_session_views)
):
    """Get all active sessions"""
    return await session_views.get_all_sessions()

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    session_views: SessionViews = Depends(get_session_views)
):
    """Get session info"""
    return await session_views.get_session(session_id)

@router.get("/{session_id}/info", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    session_views: SessionViews = Depends(get_session_views)
):
    """Get detailed session information"""
    return await session_views.get_session_info(session_id)

@router.get("/{session_id}/state")
async def get_session_state(
    session_id: str,
    session_views: SessionViews = Depends(get_session_views)
):
    """Get full session state"""
    return await session_views.get_session_state(session_id)

@router.put("/{session_id}/workspace", response_model=SessionResponse)
async def update_session_workspace(
    session_id: str,
    workspace: str,
    session_views: SessionViews = Depends(get_session_views)
):
    """Update session workspace"""
    return await session_views.update_session_workspace(session_id, workspace)

@router.post("/{session_id}/duplicate", response_model=SessionResponse)
async def duplicate_session(
    session_id: str,
    workspace: Optional[str] = None,
    session_views: SessionViews = Depends(get_session_views)
):
    """Duplicate existing session"""
    return await session_views.duplicate_session(session_id, workspace)

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_views: SessionViews = Depends(get_session_views)
):
    """Delete session"""
    return await session_views.delete_session(session_id)

@router.post("/cleanup")
async def cleanup_sessions(
    max_inactive_minutes: int = Query(60, ge=1),
    session_views: SessionViews = Depends(get_session_views)
):
    """Clean up inactive sessions"""
    return await session_views.cleanup_inactive_sessions(max_inactive_minutes)
    