import os

from fastapi import FastAPI
from app.api import router as api_router
import uvicorn

app = FastAPI(title="Postgres Extractor")

app.include_router(api_router.router)

@app.get("/health")
async def health():
    return {"status": "ok"}


def main():
    """Entry point for python -m app"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False  # reload é tratado no docker se você quiser dev/hotreload
    )


if __name__ == "__main__":
    main()
