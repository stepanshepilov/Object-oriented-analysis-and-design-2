from ..models.editor import EditorAction, CursorPosition
from ..core.state_manager import state_manager

class EditorController:
    def __init__(self, session_id: str):
        self.session_id = session_id
        
    def open_file(self, file_path: str):
        """Open file in editor"""
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            ide_state.open_file(file_path)
            return True
        return False
        
    def close_file(self, file_path: str):
        """Close file"""
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            ide_state.close_file(file_path)
            return True
        return False
        
    def switch_file(self, file_path: str):
        """Switch active file"""
        ide_state = state_manager.get_session(self.session_id)
        if ide_state and file_path in ide_state.state.editor.open_files:
            ide_state.state.editor.active_file = file_path
            return True
        return False
        
    def update_cursor(self, file_path: str, position: CursorPosition):
        """Update cursor position"""
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            ide_state.update_cursor(file_path, position.line, position.column)
            return True
        return False
        
    def get_editor_state(self):
        """Get current editor state"""
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            return ide_state.state.editor
        return None
        
    def execute_action(self, action: EditorAction):
        """Execute editor action"""
        if action.type == "open":
            return self.open_file(action.file_path)
        elif action.type == "close":
            return self.close_file(action.file_path)
        elif action.type == "switch":
            return self.switch_file(action.file_path)
        elif action.type == "update_cursor" and action.data:
            position = CursorPosition(**action.data)
            return self.update_cursor(action.file_path, position)
        return False