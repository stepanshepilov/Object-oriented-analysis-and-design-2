from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileInfo(BaseModel):
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None
    language: Optional[str] = None
    
class FileContent(BaseModel):
    path: str
    content: str
    language: str
    encoding: str = "utf-8"
    
class FileCreate(BaseModel):
    path: str
    content: str = ""
    is_directory: bool = False
    
class FileUpdate(BaseModel):
    content: str
    encoding: str = "utf-8"
    
class FileDelete(BaseModel):
    path: str
    force: bool = False
    
class FileRename(BaseModel):
    old_path: str
    new_path: str