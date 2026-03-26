from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Set
import asyncio
from pathlib import Path
from ..controllers.file_controller import FileController
from ..models.file import FileInfo, FileContent, FileCreate, FileUpdate
from ..services.file_service import FileWatcherService

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.watchers: Dict[str, FileWatcherService] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                # Stop file watcher if no connections
                if session_id in self.watchers:
                    self.watchers[session_id].stop()
                    del self.watchers[session_id]
                del self.active_connections[session_id]
                
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
                    
    def start_watcher(self, session_id: str, workspace_root: str, callback):
        """Start file watcher for session"""
        if session_id not in self.watchers:
            self.watchers[session_id] = FileWatcherService(workspace_root, callback)
            self.watchers[session_id].start()
            
    def stop_watcher(self, session_id: str):
        """Stop file watcher for session"""
        if session_id in self.watchers:
            self.watchers[session_id].stop()
            del self.watchers[session_id]

manager = ConnectionManager()

class FileViews:
    def __init__(self, session_id: str, workspace_root: str):
        self.session_id = session_id
        self.workspace_root = workspace_root
        self.controller = FileController(session_id, workspace_root)
        self._watch_tasks: Dict[str, asyncio.Task] = {}
        
    async def list_files(self, path: str = "") -> List[FileInfo]:
        """List files in directory"""
        return self.controller.list_directory(path)
        
    async def read_file(self, path: str) -> FileContent:
        """Read file content"""
        return self.controller.read_file(path)
        
    async def write_file(self, path: str, file_update: FileUpdate) -> FileContent:
        """Write file content"""
        result = self.controller.write_file(path, file_update.content)
        
        # Notify all clients about file change
        await manager.send_message({
            "type": "file_changed",
            "path": path,
            "action": "write"
        }, self.session_id)
        
        return result
        
    async def create_file(self, file_create: FileCreate) -> FileInfo:
        """Create new file"""
        print(f"\n=== FileViews.create_file CALLED ===")
        print(f"file_create: {file_create}")
        
        try:
            print("\n=== FILEVIEWS: BEFORE CONTROLLER CALL ===")
            result = await self.controller.create_file(file_create)
            print("=== FILEVIEWS: AFTER CONTROLLER CALL ===")
            
            # Notify all clients about file creation
            await manager.send_message({
                "type": "file_created",
                "path": file_create.path,
                "is_directory": file_create.is_directory
            }, self.session_id)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"ERROR in create_file view: {e}")
            import traceback
            traceback.print_exc()
            raise  # Уберите лишний отступ здесь
        
    async def delete_file(self, path: str, force: bool = False):
        """Delete file"""
        self.controller.delete_file(path, force)
        
        # Notify all clients about file deletion
        await manager.send_message({
            "type": "file_deleted",
            "path": path
        }, self.session_id)
        
    async def rename_file(self, old_path: str, new_path: str) -> FileInfo:
        """Rename file"""
        result = await self.controller.rename_file(old_path, new_path)
        
        # Notify all clients about file rename
        await manager.send_message({
            "type": "file_renamed",
            "old_path": old_path,
            "new_path": new_path
        }, self.session_id)
        
        return result
        
    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket for real-time file changes"""
        await manager.connect(websocket, self.session_id)
        
        # Start file watcher for this session
        def on_file_change(event_type: str, path: str):
            """Callback for file system changes"""
            asyncio.create_task(manager.send_message({
                "type": "fs_event",
                "event": event_type,
                "path": path
            }, self.session_id))
            
        # manager.start_watcher(self.session_id, self.workspace_root, on_file_change)
        
        try:
            while True:
                # Receive messages from client
                data = await websocket.receive_json()
                
                # Handle different message types
                message_type = data.get("type")
                
                if message_type == "watch_file":
                    # Start watching specific file
                    file_path = data.get("path")
                    if file_path:
                        await self._watch_file(file_path, websocket)
                        
                elif message_type == "unwatch_file":
                    # Stop watching specific file
                    file_path = data.get("path")
                    if file_path:
                        await self._unwatch_file(file_path, websocket)
                        
                elif message_type == "get_file_content":
                    # Get file content with cursor position
                    file_path = data.get("path")
                    if file_path:
                        content = await self.controller.read_file(file_path)
                        await websocket.send_json({
                            "type": "file_content",
                            "path": file_path,
                            "content": content.content,
                            "language": content.language
                        })
                        
                elif message_type == "save_file":
                    # Save file content
                    file_path = data.get("path")
                    content = data.get("content")
                    if file_path and content is not None:
                        await self.controller.write_file(file_path, content)
                        await websocket.send_json({
                            "type": "file_saved",
                            "path": file_path,
                            "success": True
                        })
                        
                elif message_type == "list_directory":
                    # List directory contents
                    path = data.get("path", "")
                    files = await self.controller.list_directory(path)
                    await websocket.send_json({
                        "type": "directory_list",
                        "path": path,
                        "files": [f.dict() for f in files]
                    })
                    
                elif message_type == "create_directory":
                    # Create directory
                    path = data.get("path")
                    if path:
                        await self.controller.create_file(FileCreate(
                            path=path,
                            content="",
                            is_directory=True
                        ))
                        await websocket.send_json({
                            "type": "directory_created",
                            "path": path,
                            "success": True
                        })
                        
                elif message_type == "search_files":
                    # Search files by pattern
                    pattern = data.get("pattern")
                    if pattern:
                        results = await self.controller.search_files(pattern)
                        await websocket.send_json({
                            "type": "search_results",
                            "pattern": pattern,
                            "results": results
                        })
                        
                elif message_type == "ping":
                    # Health check
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, self.session_id)
        except Exception as e:
            # Handle errors
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except:
                pass
            finally:
                manager.disconnect(websocket, self.session_id)
                
    async def _watch_file(self, file_path: str, websocket: WebSocket):
        """Watch specific file for changes"""
        if file_path not in self._watch_tasks:
            # Create task to watch file
            task = asyncio.create_task(self._watch_file_loop(file_path, websocket))
            self._watch_tasks[file_path] = task
            
    async def _unwatch_file(self, file_path: str, websocket: WebSocket):
        """Stop watching specific file"""
        if file_path in self._watch_tasks:
            self._watch_tasks[file_path].cancel()
            del self._watch_tasks[file_path]
            
    async def _watch_file_loop(self, file_path: str, websocket: WebSocket):
        """Loop to watch file for changes"""
        last_modified = None
        
        try:
            while True:
                # Check file modification time
                full_path = Path(self.workspace_root) / file_path
                if full_path.exists():
                    current_modified = full_path.stat().st_mtime
                    
                    if last_modified is not None and current_modified != last_modified:
                        # File changed, send update
                        try:
                            content = await self.controller.read_file(file_path)
                            await websocket.send_json({
                                "type": "file_updated",
                                "path": file_path,
                                "content": content.content,
                                "modified": current_modified
                            })
                        except:
                            pass
                            
                    last_modified = current_modified
                    
                await asyncio.sleep(0.5)  # Check every 500ms
                
        except asyncio.CancelledError:
            pass