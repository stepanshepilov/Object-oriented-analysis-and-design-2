from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class EditorMode(str, Enum):
    NORMAL = "normal"
    INSERT = "insert"
    VISUAL = "visual"
    COMMAND = "command"
    
class CursorPosition(BaseModel):
    line: int
    column: int
    
class Selection(BaseModel):
    start: CursorPosition
    end: CursorPosition
    
class EditorState(BaseModel):
    open_files: List[str] = []
    active_file: Optional[str] = None
    mode: EditorMode = EditorMode.NORMAL
    
class FileStateUpdate(BaseModel):
    path: str
    content: Optional[str] = None
    cursor_position: Optional[CursorPosition] = None
    selections: Optional[List[Selection]] = None
    scroll_position: Optional[Dict[str, int]] = None
    
class EditorAction(BaseModel):
    type: str  # open, close, save, switch, update_cursor, etc.
    file_path: Optional[str] = None
    data: Optional[Dict[str, Any]] = None