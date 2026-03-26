import { create } from 'zustand';
import { type EditorFile } from '../types';

interface EditorStore {
  files: Map<string, EditorFile>;
  activeFile: string | null;
  openFiles: string[];
  
  openFile: (file: EditorFile) => void;
  closeFile: (path: string) => void;
  setActiveFile: (path: string) => void;
  updateFileContent: (path: string, content: string) => void;
  setDirty: (path: string, isDirty: boolean) => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  files: new Map(),
  activeFile: null,
  openFiles: [],
  
  openFile: (file) => {
    const currentFiles = get().files;
    if (!currentFiles.has(file.path)) {
      currentFiles.set(file.path, file);
      set({
        files: new Map(currentFiles),
        openFiles: [...get().openFiles, file.path],
        activeFile: file.path,
      });
    } else {
      set({ activeFile: file.path });
    }
  },
  
  closeFile: (path) => {
    const newOpenFiles = get().openFiles.filter(p => p !== path);
    const newFiles = new Map(get().files);
    newFiles.delete(path);
    
    let newActiveFile = get().activeFile;
    if (newActiveFile === path) {
      newActiveFile = newOpenFiles[0] || null;
    }
    
    set({
      files: newFiles,
      openFiles: newOpenFiles,
      activeFile: newActiveFile,
    });
  },
  
  setActiveFile: (path) => {
    set({ activeFile: path });
  },
  
  updateFileContent: (path, content) => {
    const file = get().files.get(path);
    if (file) {
      file.content = content;
      file.isDirty = true;
      set({ files: new Map(get().files) });
    }
  },
  
  setDirty: (path, isDirty) => {
    const file = get().files.get(path);
    if (file) {
      file.isDirty = isDirty;
      set({ files: new Map(get().files) });
    }
  },
}));