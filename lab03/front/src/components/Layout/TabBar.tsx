import React from 'react';
import { X } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { FileIcon } from '../Explorer/FileIcon';

export const TabBar: React.FC = () => {
  const { openFiles, activeFile, setActiveFile, closeFile, files } = useEditorStore();

  return (
    <div className="h-10 bg-vs-black border-b border-vs-gray flex overflow-x-auto">
      {openFiles.map((path) => {
        const file = files.get(path);
        const isActive = activeFile === path;
        
        return (
          <div
            key={path}
            onClick={() => setActiveFile(path)}
            className={`
              h-full px-4 flex items-center gap-2 border-r border-vs-gray cursor-pointer transition-colors
              ${isActive 
                ? 'bg-vs-dark text-white border-t-2 border-t-vs-blue' 
                : 'bg-vs-black text-vs-text hover:bg-vs-gray'
              }
            `}
          >
            <FileIcon fileName={path} />
            <span className="text-sm">{file?.name || path.split('/').pop()}</span>
            {file?.isDirty && <span className="text-xs text-vs-blue">●</span>}
            <button
              onClick={(e) => {
                e.stopPropagation();
                closeFile(path);
              }}
              className="ml-2 p-0.5 hover:bg-vs-gray-light rounded"
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
};