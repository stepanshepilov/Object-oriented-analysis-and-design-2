from pydantic import BaseModel
from typing import Optional

class TerminalCreate(BaseModel):
    cwd: Optional[str] = None
    rows: int = 24
    cols: int = 80
    
class TerminalCommand(BaseModel):
    command: str
    terminal_id: str
    
class TerminalOutput(BaseModel):
    terminal_id: str
    output: str
    
class TerminalResize(BaseModel):
    terminal_id: str
    rows: int
    cols: int
    
class TerminalInfo(BaseModel):
    id: str
    cwd: str
    is_running: bool
    pid: Optional[int] = None