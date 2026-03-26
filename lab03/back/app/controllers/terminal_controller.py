import subprocess
import select
import pty
import os
import signal
from typing import Dict
from ..models.terminal import TerminalCommand, TerminalCreate
from ..core.state_manager import state_manager

class TerminalController:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state_manager = state_manager  # Add this line
        self.processes: Dict[str, subprocess.Popen] = {}
        self.fds: Dict[str, int] = {}
        
    def create_terminal(self, terminal_id: str, create_data: TerminalCreate):
        """Create new terminal process"""
        ide_state = state_manager.get_session(self.session_id)
        if not ide_state:
            return False
            
        # Get working directory
        cwd = create_data.cwd or ide_state.state.workspace_root
        
        # Create pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        
        # Start shell process
        process = subprocess.Popen(
            ['/bin/bash'],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=cwd,
            preexec_fn=os.setsid,
            shell=False
        )
        
        # Store process and FD
        self.processes[terminal_id] = process
        self.fds[terminal_id] = master_fd
        
        # Update state
        ide_state.add_terminal(terminal_id, cwd)
        
        return True
        
    def execute_command(self, command: TerminalCommand):
        """Execute command in terminal"""
        if command.terminal_id not in self.processes:
            return False
            
        master_fd = self.fds[command.terminal_id]
        # Write command to terminal
        os.write(master_fd, (command.command + '\n').encode())
        
        # Update state
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            ide_state.add_terminal_output(command.terminal_id, f"$ {command.command}")
            
        return True
        
    def read_output(self, terminal_id: str) -> str:
        """Read terminal output"""
        if terminal_id not in self.processes:
            return ""
            
        master_fd = self.fds[terminal_id]
        output = ""
        
        try:
            # Check if data is available
            rlist, _, _ = select.select([master_fd], [], [], 0.1)
            if rlist:
                data = os.read(master_fd, 4096)
                output = data.decode('utf-8', errors='ignore')
                
                # Update state
                ide_state = state_manager.get_session(self.session_id)
                if ide_state and output:
                    ide_state.add_terminal_output(terminal_id, output)
        except Exception:
            pass
            
        return output
        
    def resize_terminal(self, terminal_id: str, rows: int, cols: int):
        """Resize terminal"""
        if terminal_id in self.fds:
            import fcntl
            import termios
            import struct
            
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.fds[terminal_id], termios.TIOCSWINSZ, winsize)
            
            # Update state
            ide_state = state_manager.get_session(self.session_id)
            if ide_state and terminal_id in ide_state.state.terminals:
                ide_state.state.terminals[terminal_id].dimensions = {
                    "rows": rows,
                    "cols": cols
                }
                
    def kill_terminal(self, terminal_id: str):
        """Kill terminal process"""
        if terminal_id in self.processes:
            try:
                os.killpg(os.getpgid(self.processes[terminal_id].pid), signal.SIGTERM)
                self.processes[terminal_id].terminate()
            except:
                pass
                
            # Clean up
            if terminal_id in self.fds:
                os.close(self.fds[terminal_id])
                
            del self.processes[terminal_id]
            del self.fds[terminal_id]
            
            # Update state
            ide_state = state_manager.get_session(self.session_id)
            if ide_state:
                ide_state.remove_terminal(terminal_id)