"""FastAPI application factory and configuration."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from provisionR.routes import api_router
from provisionR.database import init_db

NOT_FOUND = HTTPException(status_code=404, detail="Not found")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="provisionR",
        description="An application for generating Kickstart files on the fly with a GUI for configuration.",
        version="0.1.0"
    )

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize the database on application startup."""
        init_db()

    # Include API routes
    app.include_router(api_router, prefix="/api")

    # Get the static directory path
    static_dir = Path(__file__).parent / "static"

    # Serve static files
    if static_dir.exists():
        @app.get("/")
        async def serve_index():
            """Serve index.html at root."""
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            return NOT_FOUND

        @app.get("/{full_path:path}")
        async def serve_static(full_path: str):
            """Serve static files from the static directory."""
            # Build the file path
            file_path = static_dir / full_path


            # Security: ensure the resolved path is within static_dir
            try:
                file_path = file_path.resolve()
                static_dir_resolved = static_dir.resolve()
                if not str(file_path).startswith(str(static_dir_resolved)):
                    # Path traversal attempt
                    raise NOT_FOUND
            except (ValueError, OSError):
                raise NOT_FOUND

            # If file exists, serve it
            if file_path.is_file():
                return FileResponse(file_path)

            raise NOT_FOUND

    return app
