import React, { useEffect, useState, useRef } from 'react';
import { Folder, FolderOpen, ChevronRight, ChevronDown, FilePlus, FolderPlus } from 'lucide-react';
import { api } from '../../services/api';
import { useFileStore } from '../../store/fileStore';
import { useEditorStore } from '../../store/editorStore';
import { FileIcon } from './FileIcon';
import { type FileInfo } from '../../types';

interface FileExplorerProps {
  sessionId: string;
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ sessionId }) => {
  const { fileTree, expandedFolders, setFileTree, addFiles, toggleFolder, expandFolder } = useFileStore();
  const { openFile } = useEditorStore();
  const [loading, setLoading] = useState(true);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; path: string; isDirectory: boolean } | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [showNewInput, setShowNewInput] = useState<{ path: string; type: 'file' | 'folder' } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadFileTree();
  }, [sessionId]);

  useEffect(() => {
    if (showNewInput && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showNewInput]);

  const loadFileTree = async () => {
    try {
      const files = await api.listFiles(sessionId);
      setFileTree(files);
    } catch (error) {
      console.error('Failed to load file tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFolderContent = async (folderPath: string) => {
    try {
      const files = await api.listFiles(sessionId, folderPath);
      // Добавляем файлы в общее дерево (если их ещё нет)
      addFiles(files);
    } catch (error) {
      console.error('Failed to load folder content:', error);
    }
  };

  const handleFileClick = async (file: FileInfo) => {
    if (file.is_directory) {
      const isExpanded = expandedFolders.has(file.path);
      if (!isExpanded) {
        // Загружаем содержимое папки перед раскрытием
        await loadFolderContent(file.path);
        expandFolder(file.path);
      } else {
        toggleFolder(file.path);
      }
    } else {
      try {
        const content = await api.readFile(sessionId, file.path);
        openFile({
          path: file.path,
          name: file.name,
          content: content.content,
          language: content.language,
          isDirty: false,
          cursorPosition: { line: 0, column: 0 },
        });
      } catch (error) {
        console.error('Failed to open file:', error);
      }
    }
  };

  const handleContextMenu = (e: React.MouseEvent, path: string, isDirectory: boolean) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, path, isDirectory });
  };

  const handleCreateItem = async (path: string, type: 'file' | 'folder', name: string) => {
    if (!name) return;
    
    const fullPath = path === '' ? name : `${path}/${name}`;
    
    try {
      if (type === 'file') {
        await api.createFile(sessionId, fullPath, false);
      } else {
        await api.createFile(sessionId, fullPath, true);
      }
      
      // После создания обновляем содержимое родительской папки, если она раскрыта
      const parentPath = path;
      if (expandedFolders.has(parentPath)) {
        await loadFolderContent(parentPath);
      } else {
        // Если родитель не раскрыт, всё равно обновляем корневой уровень (на случай создания в корне)
        if (parentPath === '') {
          await loadFileTree();
        }
      }
      
      setShowNewInput(null);
      setNewItemName('');
    } catch (error) {
      console.error('Failed to create:', error);
      alert(`Failed to create ${type}: ${error}`);
    }
  };

  const handleDeleteItem = async (path: string) => {
    if (confirm(`Are you sure you want to delete ${path}?`)) {
      try {
        await api.deleteFile(sessionId, path, true);
        // После удаления обновляем содержимое родительской папки
        const parentPath = path.substring(0, path.lastIndexOf('/'));
        if (expandedFolders.has(parentPath)) {
          await loadFolderContent(parentPath);
        } else {
          await loadFileTree();
        }
        setContextMenu(null);
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  const renderFileTree = (files: FileInfo[], level: number = 0, parentPath: string = '') => {
    const folders = files.filter(f => f.is_directory);
    const regularFiles = files.filter(f => !f.is_directory);
    
    return (
      <div>
        {folders.map((folder) => {
          const isExpanded = expandedFolders.has(folder.path);
          // Дети — это файлы, чей путь начинается с пути папки и не выходит за пределы одного уровня
          const childFiles = files.filter(f => 
            f.path.startsWith(folder.path + '/') && 
            f.path !== folder.path &&
            f.path.split('/').length === folder.path.split('/').length + 1
          );
          
          return (
            <div key={folder.path}>
              <div
                onContextMenu={(e) => handleContextMenu(e, folder.path, true)}
                onClick={() => handleFileClick(folder)}
                className="flex items-center gap-1 px-2 py-1 hover:bg-vs-gray cursor-pointer group"
                style={{ paddingLeft: `${level * 16 + 8}px` }}
              >
                {isExpanded ? (
                  <ChevronDown size={14} className="text-vs-text" />
                ) : (
                  <ChevronRight size={14} className="text-vs-text" />
                )}
                {isExpanded ? (
                  <FolderOpen size={16} className="text-vs-blue" />
                ) : (
                  <Folder size={16} className="text-vs-blue" />
                )}
                <span className="text-sm text-vs-text flex-1">{folder.name}</span>
              </div>
              
              {showNewInput && showNewInput.path === folder.path && (
                <div style={{ paddingLeft: `${(level + 1) * 16 + 24}px` }} className="flex items-center gap-2 py-1">
                  {showNewInput.type === 'folder' ? <Folder size={14} className="text-vs-blue" /> : <FileIcon fileName="" />}
                  <input
                    ref={inputRef}
                    type="text"
                    value={newItemName}
                    onChange={(e) => setNewItemName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleCreateItem(folder.path, showNewInput.type, newItemName);
                      } else if (e.key === 'Escape') {
                        setShowNewInput(null);
                        setNewItemName('');
                      }
                    }}
                    className="bg-vs-gray text-vs-text text-sm px-1 rounded outline-none flex-1"
                    placeholder={`${showNewInput.type} name...`}
                  />
                </div>
              )}
              
              {isExpanded && childFiles.length > 0 && (
                <div>
                  {renderFileTree(childFiles, level + 1, folder.path)}
                </div>
              )}
            </div>
          );
        })}
        
        {regularFiles.map((file) => (
          <div
            key={file.path}
            onContextMenu={(e) => handleContextMenu(e, file.path, false)}
            onClick={() => handleFileClick(file)}
            className="flex items-center gap-2 px-2 py-1 hover:bg-vs-gray cursor-pointer group"
            style={{ paddingLeft: `${level * 16 + 8}px` }}
          >
            <FileIcon fileName={file.name} />
            <span className="text-sm text-vs-text flex-1">{file.name}</span>
          </div>
        ))}
      </div>
    );
  };

  // Context menu
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    if (contextMenu) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  if (loading) {
    return (
      <div className="p-4 text-vs-text">
        <div className="animate-pulse-slow">Loading workspace...</div>
      </div>
    );
  }

  return (
    <div className="p-2">
      <div className="text-xs font-semibold text-vs-text mb-2 px-2 flex justify-between items-center">
        <span>EXPLORER</span>
        <div className="flex gap-1">
          <button
            onClick={() => setShowNewInput({ path: '', type: 'file' })}
            className="p-1 hover:bg-vs-gray rounded"
            title="New File"
          >
            <FilePlus size={14} />
          </button>
          <button
            onClick={() => setShowNewInput({ path: '', type: 'folder' })}
            className="p-1 hover:bg-vs-gray rounded"
            title="New Folder"
          >
            <FolderPlus size={14} />
          </button>
        </div>
      </div>
      
      {showNewInput && showNewInput.path === '' && (
        <div className="flex items-center gap-2 px-2 py-1 ml-6">
          {showNewInput.type === 'folder' ? <Folder size={14} className="text-vs-blue" /> : <FileIcon fileName="" />}
          <input
            ref={inputRef}
            type="text"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleCreateItem('', showNewInput.type, newItemName);
              } else if (e.key === 'Escape') {
                setShowNewInput(null);
                setNewItemName('');
              }
            }}
            className="bg-vs-gray text-vs-text text-sm px-1 rounded outline-none flex-1"
            placeholder={`${showNewInput.type} name...`}
          />
        </div>
      )}
      
      {renderFileTree(fileTree)}
      
      {contextMenu && (
        <div
          className="fixed bg-vs-gray-dark border border-vs-gray rounded shadow-lg py-1 z-50"
          style={{ top: contextMenu.y, left: contextMenu.x }}
        >
          <button
            onClick={() => {
              setShowNewInput({ path: contextMenu.path, type: 'file' });
              setContextMenu(null);
            }}
            className="w-full px-4 py-1 text-left text-sm text-vs-text hover:bg-vs-gray"
          >
            New File
          </button>
          <button
            onClick={() => {
              setShowNewInput({ path: contextMenu.path, type: 'folder' });
              setContextMenu(null);
            }}
            className="w-full px-4 py-1 text-left text-sm text-vs-text hover:bg-vs-gray"
          >
            New Folder
          </button>
          <div className="border-t border-vs-gray my-1" />
          <button
            onClick={() => handleDeleteItem(contextMenu.path)}
            className="w-full px-4 py-1 text-left text-sm text-red-400 hover:bg-vs-gray"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
};