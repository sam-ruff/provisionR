"""Main entry point for the provisionR FastAPI application."""

import uvicorn
from provisionR.app import create_app


def main():
    """Run the FastAPI application with uvicorn."""
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
