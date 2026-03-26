import asyncio
import os
import pty
import select
import signal
import subprocess
import threading
from typing import Dict, Optional, Callable
from pathlib import Path

class TerminalProcess:
    """Manage individual terminal process"""
    
    def __init__(self, terminal_id: str, cwd: str, on_output: Callable[[str, str], None]):
        self.terminal_id = terminal_id
        self.cwd = Path(cwd).resolve()
        self.on_output = on_output
        self.process: Optional[subprocess.Popen] = None
        self.master_fd: Optional[int] = None
        self.slave_fd: Optional[int] = None
        self._running = False
        self._read_thread: Optional[threading.Thread] = None
        
    def start(self, shell: str = "/bin/bash"):
        """Start terminal process"""
        try:
            # Create pseudo-terminal
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Start shell process
            self.process = subprocess.Popen(
                [shell],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                cwd=str(self.cwd),
                preexec_fn=os.setsid,
                shell=False,
                text=True
            )
            
            self._running = True
            
            # Start reading thread
            self._read_thread = threading.Thread(target=self._read_output, daemon=True)
            self._read_thread.start()
            
            return True
        except Exception as e:
            self.on_output(self.terminal_id, f"Error starting terminal: {str(e)}")
            return False
            
    def _read_output(self):
        """Read output from terminal"""
        while self._running and self.master_fd:
            try:
                rlist, _, _ = select.select([self.master_fd], [], [], 0.1)
                if rlist:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        self.on_output(self.terminal_id, data.decode('utf-8', errors='ignore'))
            except Exception:
                break
                
    def write(self, command: str):
        """Write command to terminal"""
        if self.master_fd:
            try:
                os.write(self.master_fd, (command + '\n').encode())
                return True
            except Exception:
                return False
        return False
        
    def resize(self, rows: int, cols: int):
        """Resize terminal"""
        if self.master_fd:
            try:
                import fcntl
                import termios
                import struct
                
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
                return True
            except Exception:
                return False
        return False
        
    def kill(self):
        """Kill terminal process"""
        self._running = False
        
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                pass
                
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
                
        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except:
                pass
                
    @property
    def is_running(self) -> bool:
        return self._running and self.process and self.process.poll() is None

class TerminalService:
    """Service to manage multiple terminals"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.terminals: Dict[str, TerminalProcess] = {}
        self._callbacks: Dict[str, Callable] = {}
        
    def create_terminal(self, terminal_id: str, cwd: str, shell: str = "/bin/bash") -> bool:
        """Create new terminal"""
        if terminal_id in self.terminals:
            return False
            
        def on_output(term_id: str, output: str):
            """Handle terminal output"""
            if term_id in self._callbacks:
                self._callbacks[term_id](output)
                
        terminal = TerminalProcess(terminal_id, cwd, on_output)
        if terminal.start(shell):
            self.terminals[terminal_id] = terminal
            return True
            
        return False
        
    def execute_command(self, terminal_id: str, command: str) -> bool:
        """Execute command in terminal"""
        if terminal_id in self.terminals:
            return self.terminals[terminal_id].write(command)
        return False
        
    def resize_terminal(self, terminal_id: str, rows: int, cols: int) -> bool:
        """Resize terminal"""
        if terminal_id in self.terminals:
            return self.terminals[terminal_id].resize(rows, cols)
        return False
        
    def kill_terminal(self, terminal_id: str):
        """Kill terminal"""
        if terminal_id in self.terminals:
            self.terminals[terminal_id].kill()
            del self.terminals[terminal_id]
            
            if terminal_id in self._callbacks:
                del self._callbacks[terminal_id]
                
    def get_terminal_output(self, terminal_id: str) -> str:
        """Get terminal output (for non-WebSocket mode)"""
        # This would need to be implemented with output buffering
        return ""
        
    def set_output_callback(self, terminal_id: str, callback: Callable[[str], None]):
        """Set callback for terminal output"""
        self._callbacks[terminal_id] = callback
        
    def remove_output_callback(self, terminal_id: str):
        """Remove output callback"""
        if terminal_id in self._callbacks:
            del self._callbacks[terminal_id]
            
    def get_active_terminals(self) -> list:
        """Get list of active terminals"""
        return [
            {
                "id": term_id,
                "is_running": term.is_running
            }
            for term_id, term in self.terminals.items()
        ]
        
    def cleanup(self):
        """Clean up all terminals"""
        for terminal in self.terminals.values():
            terminal.kill()
        self.terminals.clear()
        self._callbacks.clear()
