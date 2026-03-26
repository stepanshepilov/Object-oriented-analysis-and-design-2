from typing import Dict, Optional
import uuid
from .state import IDEState, SessionState

class StateManager:
    """Singleton manager for all IDE states"""
    
    _instance = None
    _states: Dict[str, IDEState] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_session(self, workspace_root: str) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        self._states[session_id] = IDEState(session_id, workspace_root)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[IDEState]:
        """Get session by ID"""
        return self._states.get(session_id)
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self._states:
            del self._states[session_id]
            
    def get_state(self, session_id: str) -> Optional[SessionState]:
        """Get current state for session"""
        session = self.get_session(session_id)
        return session.get_state() if session else None
    
    def update_state(self, session_id: str, updater):
        """Update state with function"""
        session = self.get_session(session_id)
        if session:
            updater(session)
            
state_manager = StateManager()