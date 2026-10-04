# Day 3 Summary: DuckDB Setup and Connection

**Project:** Baltimore City Real Estate Investment Signal Platform
**Step completed:** 3, DuckDB setup and connection script

## What I accomplished

- Created `db/duckdb_connection.py` at the project root as a reusable connection module.
- The module resolves the project root from its own location (`Path(__file__).resolve().parents[1]`) and defaults the database to `data/baltimore.duckdb`. The `data/` folder and the `.duckdb` file are created automatically on first run.
- The database path can be overridden with the `BALTIMORE_DUCKDB_PATH` environment variable.
- Exposes two ways to connect: `get_connection()` and the `duckdb_conn()` context manager (closes automatically). Both accept `read_only=True`, which will be useful for Superset or anything that shouldn't write.
- Loads the `httpfs` extension (for reading CSV/Parquet straight from URLs or S3). I dropped `spatial` because the project doesn't need geospatial boundary joins. Extension failures log a warning instead of crashing.
- Bootstraps three schemas on connect: `raw`, `staging`, `marts` (the extract, clean/model, and serve layers).
- Verified from the DuckDB CLI that all three schemas exist in the database file.

## Usage

```python
from db.duckdb_connection import get_connection, duckdb_conn

con = get_connection()

with duckdb_conn() as con:
    con.sql("SELECT * FROM raw.permits LIMIT 5").show()
```

Smoke test (run from the project root):

```
python db/duckdb_connection.py
```

## Gotchas and lessons learned

1. **Run the script from the right place.** The file lives in `db/`, so `python duckdb_connection.py` from the project root fails with "can't open file". Use `python db/duckdb_connection.py` from the root, or `cd db` first.
2. **The script's location matters.** `parents[1]` assumes the file sits exactly one folder below the project root. If it moves (for example to `src/db/`), change it to `parents[2]` or `data/` lands in the wrong place.
3. **Schemas are not files or folders.** They live inside the single `.duckdb` file, so you won't see `raw`, `staging` or `marts` in the file explorer. Check them with a query instead:
   ```sql
   SELECT schema_name FROM information_schema.schemata;
   ```
4. **`duckdb` alone opens a throwaway in-memory database.** Pass the file path to open the real one:
   ```
   duckdb data/baltimore.duckdb
   ```
   The prompt shows `memory D` for the in-memory session and `baltimore D` when connected to the file. If a schema you expect is missing, check the prompt first.
5. **Shell commands don't work at the SQL prompt.** Typing `duckdb data/baltimore.duckdb` inside the CLI gets parsed as SQL and fails with a parser error, and it also swallows the next line you paste. To switch databases from inside the CLI use `.open data/baltimore.duckdb`, and exit with `.quit` or Ctrl+D.
6. **Pasting into the CLI works fine** as long as you start from a clean prompt and the statement ends with `;`. Leftover unfinished text from an earlier attempt is what breaks it.

## Verified

- Script connects and creates `data/baltimore.duckdb` at the project root.
- `raw`, `staging` and `marts` schemas present, confirmed from the CLI at the `baltimore D` prompt.

## Next up (step 4)

- Load the existing extract output (`permits`, `real_property`, `rehabs_vacant`, `tax_lien`, `vacants`) into the `raw` schema using `get_connection()`.
- Consider adding `data/*.duckdb` to `.gitignore` so the database file isn't committed.
