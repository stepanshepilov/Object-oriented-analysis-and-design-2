export interface FileInfo {
  name: string;
  path: string;
  is_directory: boolean;
  size?: number;
  modified?: string;
  language?: string;
}

export interface FileContent {
  path: string;
  content: string;
  language: string;
  encoding: string;
}

export interface EditorFile {
  path: string;
  name: string;
  content: string;
  language: string;
  isDirty: boolean;
  cursorPosition: { line: number; column: number };
}

export interface TerminalInfo {
  id: string;
  cwd: string;
  is_running: boolean;
  output: string[];
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  workspace_root: string;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}