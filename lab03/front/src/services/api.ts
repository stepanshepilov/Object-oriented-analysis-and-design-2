import { API_BASE_URL } from '../utils/constants';
import { type FileInfo, type FileContent, type SessionInfo } from '../types';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log('API Request:', {
      url,
      method: options?.method || 'GET',
      headers: options?.headers,
      body: options?.body
    });
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`API Error ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      return data;
    } catch (error) {
      console.error('Network error:', error);
      throw error;
    }
  }
  
  async createSession(workspace_root: string = './workspace'): Promise<SessionInfo> {
    return this.request<SessionInfo>('/sessions/', {
      method: 'POST',
      body: JSON.stringify({ workspace_root }),
    });
  }
  
  async createFile(sessionId: string, path: string, isDirectory: boolean = false): Promise<FileInfo> {
    console.log('=== API createFile ===');
    console.log('sessionId:', sessionId);
    console.log('path:', path);
    console.log('isDirectory:', isDirectory);
    
    const body = { 
        path: path, 
        content: '', 
        is_directory: isDirectory 
    };
    
    console.log('Request body:', body);
    
    return this.request<FileInfo>('/files/', {
        method: 'POST',
        headers: { 'X-Session-ID': sessionId },
        body: JSON.stringify(body),
    });
}
  
  async getSession(sessionId: string): Promise<SessionInfo> {
    return this.request<SessionInfo>(`/sessions/${sessionId}`);
  }
  
  async deleteSession(sessionId: string): Promise<void> {
    return this.request(`/sessions/${sessionId}`, { method: 'DELETE' });
  }
  
  // File endpoints
  async listFiles(sessionId: string, path: string = ''): Promise<FileInfo[]> {
    return this.request<FileInfo[]>(`/files/?path=${encodeURIComponent(path)}`, {
      headers: { 'X-Session-ID': sessionId },
    });
  }
  
  async readFile(sessionId: string, path: string): Promise<FileContent> {
    return this.request<FileContent>(`/files/${encodeURIComponent(path)}`, {
      headers: { 'X-Session-ID': sessionId },
    });
  }
  
  async writeFile(sessionId: string, path: string, content: string): Promise<FileContent> {
    return this.request<FileContent>(`/files/${encodeURIComponent(path)}`, {
      method: 'POST',
      headers: { 'X-Session-ID': sessionId },
      body: JSON.stringify({ content }),
    });
  }
  
  async deleteFile(sessionId: string, path: string, force: boolean = false): Promise<void> {
    return this.request(`/files/${encodeURIComponent(path)}?force=${force}`, {
      method: 'DELETE',
      headers: { 'X-Session-ID': sessionId },
    });
  }
  
  async renameFile(sessionId: string, oldPath: string, newPath: string): Promise<FileInfo> {
    return this.request<FileInfo>(`/files/rename?old_path=${encodeURIComponent(oldPath)}&new_path=${encodeURIComponent(newPath)}`, {
      method: 'PUT',
      headers: { 'X-Session-ID': sessionId },
    });
  }
}

export const api = new ApiService();