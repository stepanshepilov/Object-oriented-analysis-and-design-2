from fastapi import Request, HTTPException, WebSocket, Depends
from ..views.file_views import FileViews
from ..views.editor_views import EditorViews
from ..views.terminal_views import TerminalViews
from ..views.session_views import SessionViews
from ..core.state_manager import state_manager

async def get_session_id_from_header(request: Request) -> str:
    """Extract session ID from request headers"""
    print(f"\n=== get_session_id_from_header CALLED ===")
    session_id = request.headers.get("X-Session-ID")
    print(f"X-Session-ID header: {session_id}")
    
    if not session_id:
        print("ERROR: No session ID in header")
        raise HTTPException(status_code=400, detail="Session ID required in X-Session-ID header")
    
    # Validate session exists
    session = state_manager.get_session(session_id)
    print(f"Session exists: {session is not None}")
    
    if not session:
        print(f"ERROR: Session {session_id} not found")
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    return session_id

async def get_file_views(
    session_id: str = Depends(get_session_id_from_header)
) -> FileViews:
    """Dependency for FileViews"""
    print(f"\n=== get_file_views CALLED ===")
    print(f"session_id: {session_id}")
    
    session = state_manager.get_session(session_id)
    if not session:
        print(f"ERROR: Session {session_id} not found!")
        raise HTTPException(status_code=404, detail="Session not found")
    
    print(f"Workspace root: {session.state.workspace_root}")
    
    try:
        file_views = FileViews(session_id, session.state.workspace_root)
        print(f"FileViews created successfully")
        return file_views
    except Exception as e:
        print(f"ERROR creating FileViews: {e}")
        import traceback
        traceback.print_exc()
        raise

async def get_session_id_from_path(session_id: str) -> str:
    """Extract session ID from path parameter"""
    # Validate session exists
    session = state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    return session_id

async def get_editor_views(
    session_id: str = Depends(get_session_id_from_header)
) -> EditorViews:
    """Dependency for EditorViews"""
    return EditorViews(session_id)

async def get_terminal_views(
    session_id: str = Depends(get_session_id_from_header)
) -> TerminalViews:
    """Dependency for TerminalViews"""
    return TerminalViews(session_id)

async def get_session_views() -> SessionViews:
    """Dependency for SessionViews"""
    return SessionViews()

# For WebSocket endpoints
async def get_session_id_websocket(
    websocket: WebSocket,
    session_id: str
) -> str:
    """Extract session ID from WebSocket path"""
    session = state_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason=f"Session {session_id} not found")
        raise HTTPException(status_code=404, detail="Session not found")
    return session_id
