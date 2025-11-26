import re
import time
from pathlib import Path

import asyncpg
import polars as pl

from app.core.config import DEFAULT_STORAGE_PATH, Settings


IDENT_RE = re.compile(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)?$")


async def extract_table_to_parquet(table_name: str, settings: Settings) -> dict:
    """Extrai toda a tabela do Postgres e grava em um arquivo Parquet.

    Retorna dict com caminho do arquivo e quantidade de linhas.

    Nota: valida o nome da tabela para evitar SQL injection (aceita 'schema.table' ou 'table').
    """
    if not IDENT_RE.match(table_name):
        raise ValueError("invalid table name; only letters, numbers, underscore and optional schema (schema.table) are allowed")

    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
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
        safe_name = table_name.replace('.', '_')
        out_dir = Path(DEFAULT_STORAGE_PATH)
        out_path = out_dir / f"{safe_name}_{ts}.parquet"
        df.write_parquet(out_path)

        return {"path": str(out_path), "rows": len(df)}
    finally:
        await conn.close()
