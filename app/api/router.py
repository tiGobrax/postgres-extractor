import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.utils.extractor import extract_table_to_gcs, extract_table_to_parquet

router = APIRouter(prefix="")
logger = logging.getLogger(__name__)


class TableRequest(BaseModel):
    table: str


@router.post("/extract")
async def extract(req: TableRequest):
    settings = get_settings()
    try:
        result = await extract_table_to_parquet(req.table, settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to extract table '%s'", req.table)
        raise HTTPException(
            status_code=500,
            detail=f"internal error: {e.__class__.__name__}: {e}",
        ) from e
    return result


@router.post("/extract/gcs")
async def extract_to_gcs(req: TableRequest):
    settings = get_settings()
    try:
        result = await extract_table_to_gcs(req.table, settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to extract table '%s' to GCS", req.table)
        raise HTTPException(
            status_code=500,
            detail=f"internal error: {e.__class__.__name__}: {e}",
        ) from e
    return result
