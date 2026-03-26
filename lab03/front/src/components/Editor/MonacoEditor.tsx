import React, { useEffect, useRef } from 'react';
import MonacoEditor from '@monaco-editor/react';
import { useEditorStore } from '../../store/editorStore';
import { api } from '../../services/api';
import { wsService } from '../../services/websocket';

interface EditorProps {
  sessionId: string;
  filePath: string;
}

export const Editor: React.FC<EditorProps> = ({ sessionId, filePath }) => {
  const { files, updateFileContent, setDirty } = useEditorStore();
  const file = files.get(filePath);
  const editorRef = useRef<any>(null);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout>>(1);

  useEffect(() => {
    if (filePath) {
      wsService.watchFile(filePath);
    }
    
    const handleFileUpdate = (data: any) => {
      if (data.path === filePath) {
        updateFileContent(filePath, data.content);
      }
    };
    
    wsService.on('file_updated', handleFileUpdate);
    
    return () => {
      wsService.off('file_updated', handleFileUpdate);
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [filePath]);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
    editor.focus();
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined && file) {
      updateFileContent(filePath, value);
      
      // Auto-save after 1 second of inactivity
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      
      saveTimeoutRef.current = setTimeout(async () => {
        try {
          await api.writeFile(sessionId, filePath, value);
          setDirty(filePath, false);
          wsService.saveFile(filePath, value);
        } catch (error) {
          console.error('Failed to save file:', error);
        }
      }, 1000);
    }
  };

  if (!file) {
    return (
      <div className="flex items-center justify-center h-full text-vs-text">
        <div className="text-center">
          <p className="text-lg mb-2">No file open</p>
          <p className="text-sm">Select a file from the explorer to start editing</p>
        </div>
      </div>
    );
  }

  return (
    <MonacoEditor
      height="100%"
      language={file.language}
      theme="vs-dark"
      value={file.content}
      onChange={handleEditorChange}
      onMount={handleEditorDidMount}
      options={{
        minimap: { enabled: true },
        fontSize: 14,
        fontFamily: 'Fira Code',
        fontLigatures: true,
        lineNumbers: 'on',
        renderWhitespace: 'boundary',
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        wordWrap: 'on',
      }}
    />
  );
};