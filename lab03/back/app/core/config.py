from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IDE Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # File system settings
    WORKSPACE_ROOT: str = "./workspace"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Terminal settings
    TERMINAL_SHELL: str = "/bin/bash"
    TERMINAL_MAX_OUTPUT: int = 10000
    
    class Config:
        env_file = ".env"

settings = Settings()
