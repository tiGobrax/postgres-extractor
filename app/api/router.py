import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.utils.extractor import extract_table_to_gcs

router = APIRouter(prefix="")
logger = logging.getLogger(__name__)


class TableRequest(BaseModel):
    table: str
    db: str | None = None


@router.post("/run")
async def run_extract(req: TableRequest):
    settings = get_settings()
    db_name = req.db or settings.DB_NAME
    if not db_name:
        raise HTTPException(status_code=400, detail="database name is required (send 'db' in body or set DB_NAME env var)")
    try:
        result = await extract_table_to_gcs(req.table, db_name, settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to extract table '%s' to GCS", req.table)
        raise HTTPException(
            status_code=500,
            detail=f"internal error: {e.__class__.__name__}: {e}",
        ) from e
    return result
