from fastapi import WebSocket, WebSocketDisconnect
from ..controllers.editor_controller import EditorController
from ..models.editor import EditorAction, EditorState

class EditorViews:
    def __init__(self, session_id: str):
        self.controller = EditorController(session_id)
        
    async def get_state(self) -> EditorState:
        """Get current editor state"""
        return self.controller.get_editor_state()
        
    async def execute_action(self, action: EditorAction) -> bool:
        """Execute editor action"""
        return self.controller.execute_action(action)
        
    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket for real-time editor updates"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                action = EditorAction(**data)
                result = self.controller.execute_action(action)
                await websocket.send_json({"success": result})
        except WebSocketDisconnect:
            pass
