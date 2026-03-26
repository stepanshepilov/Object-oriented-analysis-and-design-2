from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import List
from ..views.file_views import FileViews, manager as ws_manager
from ..models.file import FileInfo, FileContent, FileCreate, FileUpdate
from ..core.dependencies import get_file_views, get_session_id_websocket
from ..core.state_manager import state_manager

router = APIRouter(prefix="/files", tags=["files"])

print("FILE_ROUTER LOADED")

@router.get("/", response_model=List[FileInfo])
async def list_files(
    path: str = Query("", description="Directory path"),
    file_views: FileViews = Depends(get_file_views)
):
    """List files in directory"""
    return await file_views.list_files(path)

@router.get("/{path:path}", response_model=FileContent)
async def read_file(
    path: str,
    file_views: FileViews = Depends(get_file_views)
):
    """Read file content"""
    return await file_views.read_file(path)

@router.post("/", response_model=FileInfo)
async def create_file(
    file_create: FileCreate,
    file_views: FileViews = Depends(get_file_views)
):
    """Create new file"""
    print("\n" + "="*50)
    print("ROUTER: create_file CALLED")
    print("="*50)
    print(f"file_create.path: {file_create.path}")
    print(f"file_create.is_directory: {file_create.is_directory}")
    print(f"file_create.content length: {len(file_create.content or '')}")
    print(f"file_views: {file_views}")
    
    try:
        result = await file_views.create_file(file_create)
        print(f"ROUTER: result = {result}")
        return result
    except Exception as e:
        print(f"ROUTER: exception {e}")
        import traceback
        traceback.print_exc()
        raise

@router.post("/{path:path}", response_model=FileContent)
async def write_file(
    path: str,
    file_update: FileUpdate,
    file_views: FileViews = Depends(get_file_views)
):
    """Write file content"""
    return await file_views.write_file(path, file_update)



@router.delete("/{path:path}")
async def delete_file(
    path: str,
    force: bool = Query(False),
    file_views: FileViews = Depends(get_file_views)
):
    """Delete file or directory"""
    return await file_views.delete_file(path, force)

@router.put("/rename")
async def rename_file(
    old_path: str = Query(...),
    new_path: str = Query(...),
    file_views: FileViews = Depends(get_file_views)
):
    """Rename file"""
    return await file_views.rename_file(old_path, new_path)

@router.websocket("/ws/{session_id}")
async def file_websocket(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket for file watching"""
    try:
        # Validate session exists
        session_state = state_manager.get_session(session_id)
        if not session_state:
            await websocket.close(code=1008, reason=f"Session {session_id} not found")
            return
        
        # Create FileViews instance
        file_views = FileViews(session_id, session_state.state.workspace_root)
        
        # Call websocket endpoint
        await file_views.websocket_endpoint(websocket)
        
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
