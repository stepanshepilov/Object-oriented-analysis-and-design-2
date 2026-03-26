import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from ..models.file import FileInfo, FileContent, FileCreate
from ..core.state_manager import state_manager
from ..services.file_service import FileSearchService

class FileController:
    def __init__(self, session_id: str, workspace_root: str):
        self.session_id = session_id
        self.workspace_root = Path(workspace_root).resolve()
        print(f"FileController initialized with workspace: {self.workspace_root}")
        
        try:
            self.workspace_root.mkdir(parents=True, exist_ok=True)
            print(f"Workspace directory ready: {self.workspace_root}")
        except Exception as e:
            print(f"Failed to create workspace: {e}")
    
    def _safe_path(self, path: str) -> Path:
        """Ensure path is within workspace and return absolute path"""
        if not path:
            return self.workspace_root
        
        # Normalize path - remove leading/trailing slashes
        clean_path = path.strip('/')
        
        if not clean_path:
            return self.workspace_root
        
        # Build full path
        full_path = (self.workspace_root / clean_path).resolve()
        
        # Security check
        if not str(full_path).startswith(str(self.workspace_root.resolve())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Path outside workspace"
            )
        
        return full_path
    
    async def create_file(self, file_create: FileCreate) -> FileInfo:
        """Create new file or directory - simplified working version"""
        print("\n=== SIMPLIFIED CREATE FILE ===")
        print(f"Path: {file_create.path}")
        print(f"Is directory: {file_create.is_directory}")
        
        # Build target path
        clean_path = file_create.path.strip('/')
        target_path = self.workspace_root / clean_path
        print(f"Target path: {target_path}")
        
        # Create parent directories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_create.is_directory:
            target_path.mkdir(exist_ok=True)
            is_dir = True
            size = None
        else:
            # Write file
            target_path.write_text(file_create.content or "", encoding='utf-8')
            is_dir = False
            size = len(file_create.content or "")
        
        print(f"Successfully created: {target_path}")
        stat = target_path.stat()
        
        return FileInfo(
            name=target_path.name,
            path=clean_path,
            is_directory=is_dir,
            size=size,
            modified=stat.st_mtime
        )
    
    def list_directory(self, path: str = "") -> List[FileInfo]:
        """List files and directories"""
        target_path = self._safe_path(path)
        
        if not target_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path not found: {path}"
            )
            
        if not target_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not a directory: {path}"
            )
            
        items = []
        for item in target_path.iterdir():
            try:
                stat = item.stat()
                items.append(FileInfo(
                    name=item.name,
                    path=str(item.relative_to(self.workspace_root)),
                    is_directory=item.is_dir(),
                    size=stat.st_size if not item.is_dir() else None,
                    modified=stat.st_mtime
                ))
            except Exception:
                continue
                
        return sorted(items, key=lambda x: (not x.is_directory, x.name.lower()))
    
    def read_file(self, path: str) -> FileContent:
        """Read file content"""
        file_path = self._safe_path(path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {path}"
            )
            
        if file_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot read directory: {path}"
            )
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update state
            ide_state = state_manager.get_session(self.session_id)
            if ide_state:
                ide_state.update_file_content(path, content)
                
            return FileContent(
                path=path,
                content=content,
                language=self._get_language(file_path)
            )
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File is not UTF-8 encoded"
            )
            
    def write_file(self, path: str, content: str, create_dirs: bool = True) -> FileContent:
        """Write file content"""
        file_path = self._safe_path(path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Update state
            ide_state = state_manager.get_session(self.session_id)
            if ide_state:
                ide_state.update_file_content(path, content)
                ide_state.save_file(path)
                
            return FileContent(
                path=path,
                content=content,
                language=self._get_language(file_path)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to write file: {str(e)}"
            )
        
    def delete_file(self, path: str, force: bool = False):
        """Delete file or directory"""
        target_path = self._safe_path(path)
        
        if not target_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path not found: {path}"
            )
            
        try:
            if target_path.is_dir():
                if force:
                    shutil.rmtree(target_path)
                else:
                    target_path.rmdir()
            else:
                target_path.unlink()
                
            # Update state
            ide_state = state_manager.get_session(self.session_id)
            if ide_state:
                ide_state.close_file(path)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete: {str(e)}"
            )
            
    def rename_file(self, old_path: str, new_path: str) -> FileInfo:
        """Rename file or directory"""
        old_target = self._safe_path(old_path)
        new_target = self._safe_path(new_path)
        
        if not old_target.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path not found: {old_path}"
            )
            
        if new_target.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Destination already exists: {new_path}"
            )
            
        old_target.rename(new_target)
        
        # Update state
        ide_state = state_manager.get_session(self.session_id)
        if ide_state:
            ide_state.close_file(old_path)
            if new_target.is_file():
                ide_state.open_file(new_path)
                
        return FileInfo(
            name=new_target.name,
            path=new_path,
            is_directory=new_target.is_dir(),
            size=new_target.stat().st_size if not new_target.is_dir() else None,
            modified=new_target.stat().st_mtime
        )
        
    def _get_language(self, file_path: Path) -> str:
        """Get language from file extension"""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown'
        }
        return language_map.get(ext, 'plaintext')
    
    def search_files(self, pattern: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search files by name pattern"""
        search_service = FileSearchService(str(self.workspace_root))
        return search_service.search_files(pattern, max_results)
        
    def search_content(self, search_text: str, file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search content in files"""
        search_service = FileSearchService(str(self.workspace_root))
        return search_service.search_content(search_text, file_pattern)
        
    def search_by_extension(self, extensions: List[str]) -> List[Dict[str, Any]]:
        """Search files by extension"""
        search_service = FileSearchService(str(self.workspace_root))
        return search_service.search_by_extension(extensions)
        
    def get_file_tree(self, base_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get file tree structure"""
        search_service = FileSearchService(str(self.workspace_root))
        return search_service.get_file_tree(base_path)
