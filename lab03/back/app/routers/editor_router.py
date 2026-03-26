from fastapi import APIRouter, Depends, WebSocket
from ..views.editor_views import EditorViews
from ..models.editor import EditorAction, EditorState
from ..core.dependencies import get_editor_views

router = APIRouter(prefix="/editor", tags=["editor"])

@router.get("/state", response_model=EditorState)
async def get_editor_state(
    editor_views: EditorViews = Depends(get_editor_views)
):
    """Get current editor state"""
    return await editor_views.get_state()

@router.post("/action")
async def execute_editor_action(
    action: EditorAction,
    editor_views: EditorViews = Depends(get_editor_views)
):
    """Execute editor action"""
    return await editor_views.execute_action(action)

@router.websocket("/ws/{session_id}")
async def editor_websocket(
    websocket: WebSocket,
    session_id: str,
    editor_views: EditorViews = Depends(get_editor_views)
):
    """WebSocket for editor updates"""
    await editor_views.websocket_endpoint(websocket)