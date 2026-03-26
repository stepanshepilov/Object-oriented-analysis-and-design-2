from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from ..views.terminal_views import TerminalViews
from ..models.terminal import TerminalCommand, TerminalCreate, TerminalResize, TerminalInfo
from ..core.dependencies import get_terminal_views, get_session_id_from_header
from ..core.state_manager import state_manager
from typing import List

router = APIRouter(prefix="/terminals", tags=["terminals"])

@router.post("/{terminal_id}", response_model=dict)
async def create_terminal(
    terminal_id: str,
    create_data: TerminalCreate,
    terminal_views: TerminalViews = Depends(get_terminal_views)
):
    """Create new terminal"""
    success = await terminal_views.create_terminal(terminal_id, create_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create terminal")
    return {"success": True, "terminal_id": terminal_id}

@router.post("/{terminal_id}/command", response_model=dict)
async def execute_command(
    terminal_id: str,
    command: TerminalCommand,
    terminal_views: TerminalViews = Depends(get_terminal_views)
):
    """Execute command in terminal"""
    success = await terminal_views.execute_command(command)
    return {"success": success}

@router.delete("/{terminal_id}", response_model=dict)
async def kill_terminal(
    terminal_id: str,
    terminal_views: TerminalViews = Depends(get_terminal_views)
):
    """Kill terminal"""
    await terminal_views.kill_terminal(terminal_id)
    return {"success": True}

@router.post("/{terminal_id}/resize", response_model=dict)
async def resize_terminal(
    terminal_id: str,
    resize: TerminalResize,
    terminal_views: TerminalViews = Depends(get_terminal_views)
):
    """Resize terminal"""
    await terminal_views.resize_terminal(terminal_id, resize)
    return {"success": True}

@router.get("/", response_model=List[TerminalInfo])
async def get_terminals(
    terminal_views: TerminalViews = Depends(get_terminal_views)
):
    """Get all terminals"""
    return await terminal_views.get_terminals()

@router.websocket("/ws/{session_id}")
async def terminal_websocket(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket for terminal I/O"""
    try:
        # Validate session exists
        session_state = state_manager.get_session(session_id)
        if not session_state:
            await websocket.close(code=1008, reason=f"Session {session_id} not found")
            return
        
        # Create TerminalViews instance
        terminal_views = TerminalViews(session_id)
        
        # Call websocket endpoint
        await terminal_views.websocket_endpoint(websocket)
        
    except Exception as e:
        print(f"Terminal WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass