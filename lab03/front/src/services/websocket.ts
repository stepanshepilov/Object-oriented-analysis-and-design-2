import { type WebSocketMessage } from '../types';

type MessageHandler = (data: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private sessionId: string | null = null;
  
  connect(sessionId: string) {
    this.sessionId = sessionId;
    const wsUrl = `ws://localhost:8000/files/ws/${sessionId}`;
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(() => {
        if (this.sessionId) {
          this.connect(this.sessionId);
        }
      }, 3000);
    };
  }
  
  private handleMessage(data: WebSocketMessage) {
    const handlers = this.handlers.get(data.type);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }
  
  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);
  }
  
  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }
  
  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
  
  watchFile(path: string) {
    this.send({ type: 'watch_file', path });
  }
  
  saveFile(path: string, content: string) {
    this.send({ type: 'save_file', path, content });
  }
  
  listDirectory(path: string = '') {
    this.send({ type: 'list_directory', path });
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();