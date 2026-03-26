from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime

class EditorMode(str, Enum):
    NORMAL = "normal"
    INSERT = "insert"
    VISUAL = "visual"
    COMMAND = "command"

class FileState(BaseModel):
    path: str
    content: str
    is_dirty: bool = False
    language: str
    cursor_position: Dict[str, int] = {"line": 0, "column": 0}
    selections: List[Dict[str, int]] = []
    scroll_position: Dict[str, int] = {"top": 0, "left": 0}
    last_saved: Optional[datetime] = None
    syntax_errors: List[Dict[str, Any]] = []

class EditorState(BaseModel):
    open_files: List[str] = []
    active_file: Optional[str] = None
    mode: EditorMode = EditorMode.NORMAL
    file_states: Dict[str, FileState] = {}
    split_panes: List[Dict[str, Any]] = []
    layout: str = "single"  # single, split-vertical, split-horizontal
    
class TerminalState(BaseModel):
    id: str
    process_id: Optional[int] = None
    cwd: str
    history: List[str] = []
    output: List[str] = []
    is_running: bool = False
    dimensions: Dict[str, int] = {"rows": 24, "cols": 80}
    
class SessionState(BaseModel):
    session_id: str
    created_at: datetime
    last_active: datetime
    editor: EditorState = EditorState()
    terminals: Dict[str, TerminalState] = {}
    active_terminal: Optional[str] = None
    workspace_root: str
    
class IDEState:
    """Main state manager for IDE"""
    
    def __init__(self, session_id: str, workspace_root: str):
        self.state = SessionState(
            session_id=session_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            workspace_root=workspace_root
        )
        
    def update_file_content(self, file_path: str, content: str):
        """Update file content with state tracking"""
        if file_path not in self.state.editor.file_states:
            self.state.editor.file_states[file_path] = FileState(
                path=file_path,
                content=content,
                language=self._detect_language(file_path),
                is_dirty=True
            )
        else:
            self.state.editor.file_states[file_path].content = content
            self.state.editor.file_states[file_path].is_dirty = True
            self.state.editor.file_states[file_path].last_saved = None
            
        self._update_last_active()
        
    def save_file(self, file_path: str):
        """Mark file as saved"""
        if file_path in self.state.editor.file_states:
            self.state.editor.file_states[file_path].is_dirty = False
            self.state.editor.file_states[file_path].last_saved = datetime.now()
            
    def open_file(self, file_path: str):
        """Open file in editor"""
        if file_path not in self.state.editor.open_files:
            self.state.editor.open_files.append(file_path)
        
        self.state.editor.active_file = file_path
        
        if file_path not in self.state.editor.file_states:
            self.state.editor.file_states[file_path] = FileState(
                path=file_path,
                content="",
                language=self._detect_language(file_path)
            )
            
        self._update_last_active()
        
    def close_file(self, file_path: str):
        """Close file in editor"""
        if file_path in self.state.editor.open_files:
            self.state.editor.open_files.remove(file_path)
            
        if self.state.editor.active_file == file_path:
            self.state.editor.active_file = self.state.editor.open_files[0] if self.state.editor.open_files else None
            
        self._update_last_active()
        
    def update_cursor(self, file_path: str, line: int, column: int):
        """Update cursor position"""
        if file_path in self.state.editor.file_states:
            self.state.editor.file_states[file_path].cursor_position = {
                "line": line,
                "column": column
            }
            self._update_last_active()
            
    def add_terminal(self, terminal_id: str, cwd: str):
        """Add new terminal"""
        self.state.terminals[terminal_id] = TerminalState(
            id=terminal_id,
            cwd=cwd,
            is_running=True
        )
        self.state.active_terminal = terminal_id
        self._update_last_active()
        
    def remove_terminal(self, terminal_id: str):
        """Remove terminal"""
        if terminal_id in self.state.terminals:
            self.state.terminals.pop(terminal_id)
            
        if self.state.active_terminal == terminal_id:
            self.state.active_terminal = next(iter(self.state.terminals.keys())) if self.state.terminals else None
            
        self._update_last_active()
        
    def add_terminal_output(self, terminal_id: str, output_line: str):
        """Add output to terminal"""
        if terminal_id in self.state.terminals:
            self.state.terminals[terminal_id].output.append(output_line)
            # Keep only last N lines
            if len(self.state.terminals[terminal_id].output) > 1000:
                self.state.terminals[terminal_id].output = self.state.terminals[terminal_id].output[-1000:]
                
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".md": "markdown",
            ".cpp": "cpp",
            ".c": "c",
            ".java": "java",
            ".go": "go",
            ".rs": "rust"
        }
        
        import os
        ext = os.path.splitext(file_path)[1]
        return extension_map.get(ext, "plaintext")
        
    def _update_last_active(self):
        """Update last active timestamp"""
        self.state.last_active = datetime.now()
        
    def get_state(self) -> SessionState:
        """Get current state"""
        return self.state
