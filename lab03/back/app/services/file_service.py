import asyncio
import os
from pathlib import Path
from typing import Callable, Optional, Dict, List, Any
import threading
import time
import logging

# Try to import watchdog, fallback to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler as WatchdogEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling fallback.")

logger = logging.getLogger(__name__)

class FileSystemEventHandler:
    """Handle file system events"""
    
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        
    def on_created(self, event):
        if not hasattr(event, 'is_directory') or not event.is_directory:
            self.callback("created", event.src_path)
            
    def on_modified(self, event):
        if not hasattr(event, 'is_directory') or not event.is_directory:
            self.callback("modified", event.src_path)
            
    def on_deleted(self, event):
        if not hasattr(event, 'is_directory') or not event.is_directory:
            self.callback("deleted", event.src_path)
            
    def on_moved(self, event):
        if not hasattr(event, 'is_directory') or not event.is_directory:
            self.callback("moved", event.src_path)
            if hasattr(event, 'dest_path'):
                self.callback("moved", event.dest_path)

class PollingWatcher:
    """Fallback file watcher using polling"""
    
    def __init__(self, watch_path: str, callback: Callable[[str, str], None]):
        self.watch_path = Path(watch_path).resolve()
        self.callback = callback
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._file_states: Dict[str, float] = {}
        
    def start(self):
        """Start polling"""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop polling"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            
    def _poll_loop(self):
        """Poll for file changes"""
        while self._running:
            try:
                self._check_changes()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Polling error: {e}")
                
    def _check_changes(self):
        """Check for file changes"""
        try:
            for file_path in self.watch_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        current_mtime = stat.st_mtime
                        str_path = str(file_path.relative_to(self.watch_path))
                        
                        if str_path in self._file_states:
                            if current_mtime != self._file_states[str_path]:
                                self.callback("modified", str_path)
                        else:
                            self.callback("created", str_path)
                            
                        self._file_states[str_path] = current_mtime
                        
                    except Exception:
                        pass
                        
            # Check for deleted files
            for str_path in list(self._file_states.keys()):
                full_path = self.watch_path / str_path
                if not full_path.exists():
                    self.callback("deleted", str_path)
                    del self._file_states[str_path]
                    
        except Exception as e:
            logger.error(f"Error checking changes: {e}")
            
    @property
    def is_running(self) -> bool:
        return self._running

class FileWatcherService:
    """Service to watch file system changes"""
    
    def __init__(self, watch_path: str, callback: Callable[[str, str], None]):
        self.watch_path = Path(watch_path).resolve()
        self.callback = callback
        self.observer = None
        self._watcher = None
        self._running = False
        self._watchdog_available = WATCHDOG_AVAILABLE
        
    def start(self):
        """Start file watcher"""
        if not self.watch_path.exists():
            self.watch_path.mkdir(parents=True, exist_ok=True)
            
        try:
            if self._watchdog_available:
                # Use watchdog with FSEvents
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler as WatchdogEventHandler
                
                class Handler(WatchdogEventHandler):
                    def __init__(self, callback, watch_path):
                        self.callback = callback
                        self.watch_path = watch_path
                        
                    def on_any_event(self, event):
                        if event.is_directory:
                            return
                        try:
                            rel_path = Path(event.src_path).relative_to(self.watch_path)
                            if event.event_type == 'created':
                                self.callback('created', str(rel_path))
                            elif event.event_type == 'modified':
                                self.callback('modified', str(rel_path))
                            elif event.event_type == 'deleted':
                                self.callback('deleted', str(rel_path))
                        except ValueError:
                            pass
                
                self.observer = Observer()
                handler = Handler(self.callback, self.watch_path)
                self.observer.schedule(handler, str(self.watch_path), recursive=True)
                self.observer.start()
                self._running = True
                logger.info(f"Started watchdog watcher on {self.watch_path}")
            else:
                # Fallback to polling
                self._watcher = PollingWatcher(str(self.watch_path), self.callback)
                self._watcher.start()
                self._running = True
                logger.info(f"Started polling watcher on {self.watch_path}")
                
        except Exception as e:
            logger.error(f"Failed to start watcher: {e}")
            # Fallback to polling
            self._watcher = PollingWatcher(str(self.watch_path), self.callback)
            self._watcher.start()
            self._running = True
            
    def stop(self):
        """Stop file watcher"""
        self._running = False
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2)
            except:
                pass
            self.observer = None
            
        if self._watcher:
            try:
                self._watcher.stop()
            except:
                pass
            self._watcher = None
            
    @property
    def is_running(self) -> bool:
        return self._running


class FileSearchService:
    """Service for searching files and content"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        
    def search_files(self, pattern: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search files by name pattern"""
        results = []
        
        try:
            # Check if workspace exists
            if not self.workspace_root.exists():
                return results
                
            for path in self.workspace_root.rglob("*"):
                # Skip if we have enough results
                if len(results) >= max_results:
                    break
                    
                # Skip directories
                if path.is_dir():
                    continue
                    
                # Check if pattern matches filename
                if pattern.lower() in path.name.lower():
                    try:
                        stat = path.stat()
                        results.append({
                            "name": path.name,
                            "path": str(path.relative_to(self.workspace_root)),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "is_directory": False
                        })
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            
        return results
        
    def search_content(self, search_text: str, file_pattern: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search content within files"""
        results = []
        
        try:
            # Check if workspace exists
            if not self.workspace_root.exists():
                return results
                
            for file_path in self.workspace_root.rglob("*"):
                # Skip if we have enough results
                if len(results) >= max_results:
                    break
                    
                # Skip directories
                if file_path.is_dir():
                    continue
                    
                # Check file pattern if specified
                if file_pattern and file_pattern not in file_path.name:
                    continue
                    
                # Try to read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    # Search in each line
                    for i, line in enumerate(lines):
                        if search_text.lower() in line.lower():
                            results.append({
                                "file": str(file_path.relative_to(self.workspace_root)),
                                "line": i + 1,
                                "content": line.strip(),
                                "match": search_text
                            })
                            
                            # Limit results per file
                            if len(results) >= max_results:
                                break
                                
                except Exception:
                    # Skip files that can't be read
                    continue
                    
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            
        return results
        
    def search_by_extension(self, extensions: List[str], max_results: int = 100) -> List[Dict[str, Any]]:
        """Search files by extension"""
        results = []
        
        try:
            if not self.workspace_root.exists():
                return results
                
            for path in self.workspace_root.rglob("*"):
                if len(results) >= max_results:
                    break
                    
                if path.is_file() and path.suffix in extensions:
                    try:
                        stat = path.stat()
                        results.append({
                            "name": path.name,
                            "path": str(path.relative_to(self.workspace_root)),
                            "extension": path.suffix,
                            "size": stat.st_size,
                            "modified": stat.st_mtime
                        })
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.error(f"Error searching by extension: {e}")
            
        return results
        
    def get_file_tree(self, base_path: Optional[str] = None, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Get file tree structure"""
        start_path = self.workspace_root
        if base_path:
            start_path = self.workspace_root / base_path
            
        if not start_path.exists():
            return []
            
        def build_tree(path: Path, current_depth: int = 0) -> List[Dict[str, Any]]:
            if current_depth > max_depth:
                return []
                
            items = []
            try:
                for item in sorted(path.iterdir()):
                    try:
                        item_info = {
                            "name": item.name,
                            "path": str(item.relative_to(self.workspace_root)),
                            "is_directory": item.is_dir()
                        }
                        
                        if item.is_dir():
                            item_info["children"] = build_tree(item, current_depth + 1)
                            
                        items.append(item_info)
                    except Exception:
                        continue
            except Exception:
                pass
                
            return items
            
        return build_tree(start_path)
        
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        full_path = self.workspace_root / file_path
        
        if not full_path.exists():
            return None
            
        try:
            stat = full_path.stat()
            return {
                "name": full_path.name,
                "path": file_path,
                "is_directory": full_path.is_dir(),
                "size": stat.st_size if not full_path.is_dir() else None,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "extension": full_path.suffix if full_path.is_file() else None
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
