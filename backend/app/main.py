from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import lectures
from .utils.logging_config import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    setup_logging()

    app = FastAPI(
        title="AI-Powered Lecture Voice-to-Notes Generator",
        version="1.0.0",
        description=(
            "Local, open-source system for converting lecture audio into "
            "transcripts and AI-generated study notes."
        ),
    )

    # CORS for local frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(lectures.router)

    return app


app = create_app()

