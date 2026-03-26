import React from 'react';

interface StatusBarProps {
  sessionId: string;
  activeFile?: string;
  cursorPosition?: { line: number; column: number };
}

export const StatusBar: React.FC<StatusBarProps> = ({ sessionId, activeFile, cursorPosition }) => {
  return (
    <div className="h-6 bg-vs-blue text-white text-xs flex items-center px-4 gap-4">
      <div className="flex items-center gap-2">
        <span>🐍 Python</span>
        <span>|</span>
        <span>UTF-8</span>
        <span>|</span>
        <span>LF</span>
      </div>
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        {cursorPosition && (
          <>
            <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
            <span>|</span>
          </>
        )}
        <span>Spaces: 2</span>
        <span>|</span>
        <span>Session: {sessionId.slice(0, 8)}</span>
      </div>
    </div>
  );
};