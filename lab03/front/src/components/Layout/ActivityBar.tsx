import React, { useState } from 'react';
import { Files, Terminal, Search, Settings, GitBranch } from 'lucide-react';

interface ActivityBarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export const ActivityBar: React.FC<ActivityBarProps> = ({ activeView, onViewChange }) => {
  const activities = [
    { id: 'explorer', icon: Files, label: 'Explorer' },
    { id: 'search', icon: Search, label: 'Search' },
    { id: 'source-control', icon: GitBranch, label: 'Source Control' },
    { id: 'terminal', icon: Terminal, label: 'Terminal' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-12 bg-vs-black border-r border-vs-gray flex flex-col items-center py-4">
      {activities.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          onClick={() => onViewChange(id)}
          className={`w-10 h-10 flex items-center justify-center rounded-lg mb-2 transition-all ${
            activeView === id
              ? 'bg-vs-blue text-white'
              : 'text-vs-text hover:bg-vs-gray hover:text-white'
          }`}
          title={label}
        >
          <Icon size={20} />
        </button>
      ))}
    </div>
  );
};