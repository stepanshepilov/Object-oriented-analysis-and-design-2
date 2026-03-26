from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .core.config import settings
from .routers import (
    file_router,
    editor_router,
    terminal_router,
    session_router
)

def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(file_router.router)
    app.include_router(editor_router.router)
    app.include_router(terminal_router.router)
    app.include_router(session_router.router)
    
    @app.get("/")
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    uvicorn.run(app, port=8000)
