"""CLI helpers for launching the FastAPI app."""

import os

import uvicorn


def main() -> None:
    """Run the FastAPI development server with reload enabled."""
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    port = int(os.getenv("UVICORN_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
