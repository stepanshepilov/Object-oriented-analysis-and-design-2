from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from ..models.session import SessionResponse, SessionInfo
from ..core.state_manager import state_manager
from pathlib import Path

class SessionController:
    def __init__(self):
        self.state_manager = state_manager
        
    def create_session(self, workspace_root: str = "./workspace") -> SessionResponse:
        """Create new IDE session"""
        # Normalize workspace path
        workspace_path = Path(workspace_root).resolve()
        
        # Create workspace directory if it doesn't exist
        try:
            workspace_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create workspace directory: {str(e)}"
            )
        
        # Create session
        session_id = self.state_manager.create_session(str(workspace_path))
        
        # Get session state
        session_state = self.state_manager.get_state(session_id)
        
        return SessionResponse(
            session_id=session_id,
            created_at=session_state.created_at,
            workspace_root=session_state.workspace_root
        )
    
    def get_session(self, session_id: str) -> SessionResponse:
        """Get session information"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
            
        return SessionResponse(
            session_id=session_id,
            created_at=session_state.created_at,
            workspace_root=session_state.workspace_root
        )
    
    def get_session_info(self, session_id: str) -> SessionInfo:
        """Get detailed session information"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
            
        return SessionInfo(
            session_id=session_id,
            last_active=session_state.last_active,
            open_files_count=len(session_state.editor.open_files),
            terminals_count=len(session_state.terminals)
        )
    
    def delete_session(self, session_id: str):
        """Delete session and cleanup resources"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Kill all terminal processes if any
        ide_state = self.state_manager.get_session(session_id)
        if ide_state and hasattr(ide_state, '_terminals'):
            for terminal_id in list(ide_state.state.terminals.keys()):
                try:
                    # Send kill signal to terminal process
                    if terminal_id in getattr(ide_state, 'processes', {}):
                        process = ide_state.processes[terminal_id]
                        process.terminate()
                        process.wait(timeout=5)
                except:
                    pass
        
        # Remove session
        self.state_manager.delete_session(session_id)
        
        # Optional: Cleanup workspace directory
        # if session_state.workspace_root and Path(session_state.workspace_root).exists():
        #     try:
        #         import shutil
        #         shutil.rmtree(session_state.workspace_root)
        #     except:
        #         pass
        
        return {"message": f"Session {session_id} deleted successfully"}
    
    def get_all_sessions(self) -> list[SessionInfo]:
        """Get all active sessions"""
        sessions = []
        # Access internal states (you might want to add a method to get all session IDs)
        if hasattr(self.state_manager, '_states'):
            for session_id, ide_state in self.state_manager._states.items():
                sessions.append(SessionInfo(
                    session_id=session_id,
                    last_active=ide_state.state.last_active,
                    open_files_count=len(ide_state.state.editor.open_files),
                    terminals_count=len(ide_state.state.terminals)
                ))
        return sorted(sessions, key=lambda x: x.last_active, reverse=True)
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get complete session state for debugging/restoration"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Convert to dictionary for JSON serialization
        return {
            "session_id": session_state.session_id,
            "created_at": session_state.created_at.isoformat(),
            "last_active": session_state.last_active.isoformat(),
            "workspace_root": session_state.workspace_root,
            "editor": {
                "open_files": session_state.editor.open_files,
                "active_file": session_state.editor.active_file,
                "mode": session_state.editor.mode.value,
                "file_states": {
                    path: {
                        "path": file_state.path,
                        "is_dirty": file_state.is_dirty,
                        "language": file_state.language,
                        "cursor_position": file_state.cursor_position,
                        "last_saved": file_state.last_saved.isoformat() if file_state.last_saved else None
                    }
                    for path, file_state in session_state.editor.file_states.items()
                }
            },
            "terminals": {
                terminal_id: {
                    "id": terminal.id,
                    "cwd": terminal.cwd,
                    "is_running": terminal.is_running,
                    "dimensions": terminal.dimensions
                }
                for terminal_id, terminal in session_state.terminals.items()
            },
            "active_terminal": session_state.active_terminal
        }
    
    def update_session_workspace(self, session_id: str, new_workspace: str) -> SessionResponse:
        """Update session workspace root"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        new_workspace_path = Path(new_workspace).resolve()
        
        # Check if new workspace is valid
        if not new_workspace_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace path does not exist: {new_workspace}"
            )
        
        if not new_workspace_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace path is not a directory: {new_workspace}"
            )
        
        # Update workspace root in state
        ide_state = self.state_manager.get_session(session_id)
        if ide_state:
            old_workspace = ide_state.state.workspace_root
            ide_state.state.workspace_root = str(new_workspace_path)
            
            # Optionally close all files from old workspace
            if old_workspace != str(new_workspace_path):
                # Close all open files
                for file_path in list(ide_state.state.editor.open_files):
                    ide_state.close_file(file_path)
                
                # Clear file states
                ide_state.state.editor.file_states.clear()
        
        return SessionResponse(
            session_id=session_id,
            created_at=session_state.created_at,
            workspace_root=str(new_workspace_path)
        )
    
    def cleanup_inactive_sessions(self, max_inactive_minutes: int = 60):
        """Clean up sessions that haven't been active for a while"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        if hasattr(self.state_manager, '_states'):
            for session_id, ide_state in self.state_manager._states.items():
                inactive_time = (current_time - ide_state.state.last_active).total_seconds() / 60
                if inactive_time > max_inactive_minutes:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            try:
                self.delete_session(session_id)
            except:
                pass
        
        return {
            "cleaned": len(sessions_to_remove),
            "remaining": len(self.state_manager._states) if hasattr(self.state_manager, '_states') else 0
        }
    
    def duplicate_session(self, session_id: str, new_workspace: Optional[str] = None) -> SessionResponse:
        """Create a copy of existing session"""
        session_state = self.state_manager.get_state(session_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Determine workspace for new session
        workspace = new_workspace or f"{session_state.workspace_root}_copy"
        
        # Create new session
        new_session = self.create_session(workspace)
        
        # Copy editor state if workspace is the same
        if new_workspace == session_state.workspace_root:
            original_ide = self.state_manager.get_session(session_id)
            new_ide = self.state_manager.get_session(new_session.session_id)
            
            if original_ide and new_ide:
                # Copy open files
                for file_path in original_ide.state.editor.open_files:
                    try:
                        # Read file content
                        from pathlib import Path
                        full_path = Path(original_ide.state.workspace_root) / file_path
                        if full_path.exists() and full_path.is_file():
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Open in new session
                            new_ide.update_file_content(file_path, content)
                            new_ide.open_file(file_path)
                    except:
                        pass
        
        return new_session
