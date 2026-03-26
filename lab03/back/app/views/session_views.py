from typing import List, Optional
from ..controllers.session_controller import SessionController
from ..models.session import SessionCreate, SessionResponse, SessionInfo

class SessionViews:
    def __init__(self):
        self.controller = SessionController()
        
    async def create_session(self, session_create: SessionCreate) -> SessionResponse:
        """Create new IDE session"""
        return self.controller.create_session(session_create.workspace_root)
    
    async def get_session(self, session_id: str) -> SessionResponse:
        """Get session info"""
        return self.controller.get_session(session_id)
    
    async def get_session_info(self, session_id: str) -> SessionInfo:
        """Get detailed session info"""
        return self.controller.get_session_info(session_id)
    
    async def get_all_sessions(self) -> List[SessionInfo]:
        """Get all active sessions"""
        return self.controller.get_all_sessions()
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        return self.controller.delete_session(session_id)
    
    async def get_session_state(self, session_id: str):
        """Get full session state"""
        return self.controller.get_session_state(session_id)
    
    async def update_session_workspace(self, session_id: str, workspace: str) -> SessionResponse:
        """Update session workspace"""
        return self.controller.update_session_workspace(session_id, workspace)
    
    async def duplicate_session(self, session_id: str, workspace: Optional[str] = None) -> SessionResponse:
        """Duplicate session"""
        return self.controller.duplicate_session(session_id, workspace)
    
    async def cleanup_inactive_sessions(self, max_inactive_minutes: int = 60):
        """Clean up inactive sessions"""
        return self.controller.cleanup_inactive_sessions(max_inactive_minutes)
