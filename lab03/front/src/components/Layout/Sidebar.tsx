import React from 'react';
import { FileExplorer } from '../Explorer/FileExplorer';
import { Terminal } from '../Terminal/Terminal';

interface SidebarProps {
  activeView: string;
  sessionId: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, sessionId }) => {
  const renderContent = () => {
    switch (activeView) {
      case 'explorer':
        return <FileExplorer sessionId={sessionId} />;
      case 'terminal':
        return <Terminal sessionId={sessionId} />;
      default:
        return (
          <div className="p-4 text-vs-text">
            <h3 className="text-sm font-semibold mb-4">No view selected</h3>
          </div>
        );
    }
  };

  return (
    <div className="w-64 bg-vs-dark border-r border-vs-gray overflow-y-auto">
      {renderContent()}
    </div>
  );
};