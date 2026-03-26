import React from 'react';
import { useEditorStore } from '../../store/editorStore';
import { Editor } from './MonacoEditor';
import { RunButton } from './RunButton';
import { type TerminalHandle } from '../Terminal/Terminal';

interface EditorGroupProps {
  sessionId: string;
  onRunCommand?: (command: string) => void;
  terminalRef?: React.RefObject<TerminalHandle | null>;
}

export const EditorGroup: React.FC<EditorGroupProps> = ({ sessionId, onRunCommand, terminalRef }) => {
  const { activeFile, files } = useEditorStore();
  const activeFileData = activeFile ? files.get(activeFile) : null;

  const handleRun = (command: string) => {
    if (onRunCommand) {
      onRunCommand(command);
    } else if (terminalRef?.current) {
      terminalRef.current.executeCode(command);
    }
  };

  return (
    <div className="flex-1 bg-vs-dark overflow-hidden flex flex-col">
      {activeFileData && (
        <div className="h-10 bg-vs-gray-dark border-b border-vs-gray flex items-center px-4 gap-2">
          <RunButton
            filePath={activeFile || ''}
            fileContent={activeFileData.content}
            language={activeFileData.language}
            onRun={handleRun}
          />
          <div className="text-xs text-vs-text">
            {activeFileData.language.toUpperCase()}
          </div>
        </div>
      )}
      
      {activeFile ? (
        <Editor sessionId={sessionId} filePath={activeFile} />
      ) : (
        <div className="flex items-center justify-center h-full text-vs-text">
          <div className="text-center">
            <h1 className="text-2xl mb-4">Welcome to IDE</h1>
            <p className="text-sm">Open a file from the explorer to start coding</p>
          </div>
        </div>
      )}
    </div>
  );
};