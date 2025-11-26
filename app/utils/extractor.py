import asyncio
import re
import time
from pathlib import Path

import asyncpg
import polars as pl
from google.cloud import storage

from app.core.config import Settings


IDENT_RE = re.compile(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)?$")


async def extract_table_to_parquet(table_name: str, db_name: str, settings: Settings) -> dict:
    """Extrai toda a tabela do Postgres (db_name) e grava em um arquivo Parquet.

    Retorna dict com caminho do arquivo e quantidade de linhas.

    Nota: valida o nome da tabela para evitar SQL injection (aceita 'schema.table' ou 'table').
    """
    if not IDENT_RE.match(table_name):
        raise ValueError("invalid table name; only letters, numbers, underscore and optional schema (schema.table) are allowed")

    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=db_name,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    try:
        sql = f"SELECT * FROM {table_name}"
        records = await conn.fetch(sql)

        # convert asyncpg.Record to list[dict]
        rows = [dict(r) for r in records]

        if len(rows) == 0:
            # try to get column names from table metadata
            # fallback: empty DataFrame
            df = pl.DataFrame([])
        else:
            # infer entire schema to avoid mixed-type columns when large datasets have late-appearing types
            df = pl.DataFrame(rows, infer_schema_length=None)

        ts = int(time.time())
        _, safe_table_name = _parse_table_name(table_name)
        out_dir = Path(settings.STORAGE_PATH)
        out_path = out_dir / f"{safe_table_name}_{ts}.parquet"
        df.write_parquet(out_path)

        return {"path": str(out_path), "rows": len(df)}
    finally:
        await conn.close()


def _parse_table_name(table_name: str) -> tuple[str, str]:
    """Return (schema, table) from `schema.table` or `table` (defaults schema to public)."""
    if "." in table_name:
        schema, tbl = table_name.split(".", 1)
    else:
        schema, tbl = "public", table_name
    return schema, tbl


def _upload_file_to_gcs(local_path: Path, table_name: str, db_name: str, settings: Settings) -> str:
    """Upload a Parquet file to GCS and return the gs:// URI."""
    credentials_path = Path(settings.GCP_CREDENTIALS_PATH)
    if not credentials_path.exists():
        raise FileNotFoundError(f"GCP credentials file not found: {credentials_path}")

    if not db_name:
        raise ValueError("database name must be provided for GCS path construction")

    schema, table = _parse_table_name(table_name)
    client = storage.Client.from_service_account_json(str(credentials_path))
    bucket = client.bucket(settings.GCP_BUCKET_NAME)
    blob_path = f"{settings.GCP_BASE_PATH}/{db_name}/{schema}/{table}/{local_path.name}"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(str(local_path))
    return f"gs://{settings.GCP_BUCKET_NAME}/{blob_path}"


async def extract_table_to_gcs(table_name: str, db_name: str, settings: Settings) -> dict:
    """
    Extrai a tabela para parquet local (db_name) e envia o arquivo ao GCS.

    Retorna dict com caminho local, URI gs:// e quantidade de linhas.
    """
    result = await extract_table_to_parquet(table_name, db_name, settings)
    local_path = Path(result["path"])
    if not local_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {local_path}")

    gcs_uri = await asyncio.get_running_loop().run_in_executor(
        None, _upload_file_to_gcs, local_path, table_name, db_name, settings
    )
    result["gcs_uri"] = gcs_uri
    return result
