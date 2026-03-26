import { WS_BASE_URL } from '../utils/constants';

export class TerminalService {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private terminalId: string | null = null;
  private onOutputCallback: ((data: string) => void) | null = null;
  
  connect(sessionId: string, terminalId: string) {
      this.sessionId = sessionId;
      this.terminalId = terminalId;
      const wsUrl = `${WS_BASE_URL}/terminals/ws/${sessionId}`;
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
          this.ws?.send(JSON.stringify({
              type: 'init',
              terminal_id: terminalId,
              config: { rows: 24, cols: 80, cwd: '' }  // ← изменили с '.' на ''
          }));
      };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'output' && this.onOutputCallback) {
        this.onOutputCallback(data.data);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('Terminal WebSocket error:', error);
    };
  }
  
  executeCommand(command: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'command',
        terminal_id: this.terminalId,
        command
      }));
    }
  }
  
  onOutput(callback: (data: string) => void) {
    this.onOutputCallback = callback;
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}