"""
DuckDB setup and connection utility for the Baltimore City Real Estate
Investment Signal Platform.

This module centralizes:
  - the path to the local DuckDB database file
  - connection creation (with sane defaults)
  - extension loading (httpfs for remote/S3 reads)
  - basic schema bootstrapping (raw / staging / marts schemas)

Usage:
    from db.duckdb_connection import get_connection

    con = get_connection()
    con.sql("SELECT * FROM raw.permits LIMIT 5").show()

Or as a context manager:
    from db.duckdb_connection import duckdb_conn

    with duckdb_conn() as con:
        con.sql("...")
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import duckdb

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Project root assumed to be two levels up from this file (db/duckdb_connection.py
# -> project root). Adjust if you move this module.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Allow overriding via env var so CI / other machines can point elsewhere.
DB_PATH = Path(os.environ.get("BALTIMORE_DUCKDB_PATH", PROJECT_ROOT / "data" / "baltimore.duckdb"))

# Schemas we expect the pipeline to use. Kept here so any fresh connection
# can self-heal a blank database file.
SCHEMAS = ("raw", "staging", "marts")


# ---------------------------------------------------------------------------
# Core connection logic
# ---------------------------------------------------------------------------

def get_connection(db_path: Path | str | None = None, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Open (and lightly bootstrap) a DuckDB connection.

    Args:
        db_path: override the default database file location.
        read_only: open in read-only mode (useful for Superset / dbt docs
            serving processes that shouldn't write).

    Returns:
        A live duckdb.DuckDBPyConnection.
    """
    path = Path(db_path) if db_path is not None else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Opening DuckDB at %s (read_only=%s)", path, read_only)
    con = duckdb.connect(database=str(path), read_only=read_only)

    _load_extensions(con)

    if not read_only:
        _bootstrap_schemas(con)

    return con


@contextmanager
def duckdb_conn(db_path: Path | str | None = None, read_only: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
    """Context-manager version of get_connection(), closes on exit."""
    con = get_connection(db_path=db_path, read_only=read_only)
    try:
        yield con
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_extensions(con: duckdb.DuckDBPyConnection) -> None:
    """
    Install/load extensions used across the pipeline:
      - httpfs: read CSV/Parquet directly from URLs or S3 (e.g. Open Baltimore
        API exports, Census/HUD files hosted remotely).
    """
    for ext in ("httpfs",):
        try:
            con.install_extension(ext)
            con.load_extension(ext)
        except duckdb.Error as e:
            # Non-fatal: log and continue so a missing/unreachable extension
            # doesn't block work that doesn't need it.
            logger.warning("Could not load extension '%s': %s", ext, e)


def _bootstrap_schemas(con: duckdb.DuckDBPyConnection) -> None:
    """Create the raw/staging/marts schemas if they don't exist yet."""
    for schema in SCHEMAS:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")


# ---------------------------------------------------------------------------
# Manual smoke test: `python duckdb_connection.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with duckdb_conn() as con:
        schemas = con.sql("SELECT schema_name FROM information_schema.schemata").fetchall()
        print(f"Connected to {DB_PATH}")
        print("Schemas present:", [s[0] for s in schemas])