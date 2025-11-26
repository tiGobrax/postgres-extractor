from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="Postgres Extractor")

app.include_router(api_router.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
