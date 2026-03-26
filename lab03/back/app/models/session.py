from pydantic import BaseModel
from datetime import datetime

class SessionCreate(BaseModel):
    workspace_root: str = "./workspace"
    
class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    workspace_root: str
    
class SessionInfo(BaseModel):
    session_id: str
    last_active: datetime
    open_files_count: int
    terminals_count: int