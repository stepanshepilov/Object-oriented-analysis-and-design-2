from fastapi import WebSocket, WebSocketDisconnect
from ..controllers.terminal_controller import TerminalController
from ..models.terminal import TerminalCommand, TerminalCreate, TerminalResize, TerminalInfo
from typing import List
import asyncio

class TerminalViews:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.controller = TerminalController(session_id)
        self.active_connections = set()
        
    async def create_terminal(self, terminal_id: str, create_data: TerminalCreate) -> bool:
        """Create new terminal"""
        return self.controller.create_terminal(terminal_id, create_data)
        
    async def execute_command(self, command: TerminalCommand) -> bool:
        """Execute command in terminal"""
        return self.controller.execute_command(command)
        
    async def kill_terminal(self, terminal_id: str):
        """Kill terminal"""
        return self.controller.kill_terminal(terminal_id)
        
    async def resize_terminal(self, terminal_id: str, resize: TerminalResize):
        """Resize terminal"""
        return self.controller.resize_terminal(terminal_id, resize.rows, resize.cols)
        
    async def get_terminals(self) -> List[TerminalInfo]:
        """Get all terminals"""
        terminals = []
        ide_state = self.controller.state_manager.get_session(self.session_id)
        if ide_state:
            for term_id, term in ide_state.state.terminals.items():
                terminals.append(TerminalInfo(
                    id=term_id,
                    cwd=term.cwd,
                    is_running=term.is_running,
                    pid=None
                ))
        return terminals
        
    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket for terminal I/O"""
        await websocket.accept()
        self.active_connections.add(websocket)
        terminal_id = None
        
        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "connected",
                "message": "Terminal WebSocket connected"
            })
            
            while True:
                # Receive messages from client
                data = await websocket.receive_json()
                
                if data.get("type") == "init":
                    terminal_id = data.get("terminal_id")
                    config = data.get("config", {})
                    cwd = config.get("cwd", ".")
                    rows = config.get("rows", 24)
                    cols = config.get("cols", 80)
                    
                    create_data = TerminalCreate(cwd=cwd, rows=rows, cols=cols)
                    success = self.controller.create_terminal(terminal_id, create_data)
                    
                    if success:
                        await websocket.send_json({
                            "type": "init_success",
                            "terminal_id": terminal_id,
                            "message": "Terminal created successfully"
                        })
                        
                        # Start output reader task
                        asyncio.create_task(self._read_output_loop(websocket, terminal_id))
                    else:
                        await websocket.send_json({
                            "type": "init_failed",
                            "error": "Failed to create terminal"
                        })
                        
                elif data.get("type") == "command":
                    cmd_terminal_id = data.get("terminal_id")
                    command = data.get("command")
                    
                    if cmd_terminal_id and command:
                        cmd = TerminalCommand(terminal_id=cmd_terminal_id, command=command)
                        success = self.controller.execute_command(cmd)
                        
                        await websocket.send_json({
                            "type": "command_executed",
                            "terminal_id": cmd_terminal_id,
                            "success": success
                        })
                        
                elif data.get("type") == "resize":
                    cmd_terminal_id = data.get("terminal_id")
                    rows = data.get("rows")
                    cols = data.get("cols")
                    
                    if cmd_terminal_id and rows and cols:
                        self.controller.resize_terminal(cmd_terminal_id, rows, cols)
                        
                elif data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })
                        
        except WebSocketDisconnect:
            print(f"Terminal WebSocket disconnected for {terminal_id}")
        except Exception as e:
            print(f"Terminal WebSocket error: {e}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except:
                pass
        finally:
            self.active_connections.discard(websocket)
            if terminal_id:
                self.controller.kill_terminal(terminal_id)
                
    async def _read_output_loop(self, websocket: WebSocket, terminal_id: str):
        """Read output from terminal and send to client"""
        try:
            while True:
                output = self.controller.read_output(terminal_id)
                if output:
                    await websocket.send_json({
                        "type": "output",
                        "terminal_id": terminal_id,
                        "data": output
                    })
                await asyncio.sleep(0.1)  # Check every 100ms
        except Exception as e:
            print(f"Error reading terminal output: {e}")