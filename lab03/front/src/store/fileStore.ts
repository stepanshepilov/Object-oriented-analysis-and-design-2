import { create } from 'zustand';
import { type FileInfo } from '../types';

interface FileStore {
  fileTree: FileInfo[];
  expandedFolders: Set<string>;
  setFileTree: (tree: FileInfo[]) => void;
  addFiles: (newFiles: FileInfo[]) => void;
  toggleFolder: (path: string) => void;
  expandFolder: (path: string) => void;
  collapseFolder: (path: string) => void;
}

export const useFileStore = create<FileStore>((set, get) => ({
  fileTree: [],
  expandedFolders: new Set(['']),
  
  setFileTree: (tree) => set({ fileTree: tree }),
  
  addFiles: (newFiles) => {
    set((state) => {
      const existingPaths = new Set(state.fileTree.map(f => f.path));
      const uniqueNewFiles = newFiles.filter(f => !existingPaths.has(f.path));
      return { fileTree: [...state.fileTree, ...uniqueNewFiles] };
    });
  },
  
  toggleFolder: (path) => {
    const expanded = new Set(get().expandedFolders);
    if (expanded.has(path)) {
      expanded.delete(path);
    } else {
      expanded.add(path);
    }
    set({ expandedFolders: expanded });
  },
  
  expandFolder: (path) => {
    const expanded = new Set(get().expandedFolders);
    expanded.add(path);
    set({ expandedFolders: expanded });
  },
  
  collapseFolder: (path) => {
    const expanded = new Set(get().expandedFolders);
    expanded.delete(path);
    set({ expandedFolders: expanded });
  },
}));