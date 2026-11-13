# Day 4 Summary: Loading Raw JSON into DuckDB

**Project:** Baltimore City Real Estate Investment Signal Platform
**Step completed:** 4, load extracted JSON into the `raw` schema

## What I accomplished

- Created `load/load_raw.py`, a re-runnable script that loads the five extracted JSON files from `raw_data/` into the `raw` schema of `data/baltimore.duckdb`.
- Each dataset becomes one table:

  | Table | Source file | Rows |
  |---|---|---|
  | `raw.permits` | `raw_data/api_response_permits.json` | 290,997 |
  | `raw.real_property` | `raw_data/api_real_property.json` | _TBD_ |
  | `raw.rehabs_vacant` | `raw_data/api_response_rehabs_vacant.json` | _TBD_ |
  | `raw.tax_lien` | `raw_data/api_response_tax_lien.json` | _TBD_ |
  | `raw.vacants` | `raw_data/api_response_vacants.json` | _TBD_ |

- Tables are rebuilt on every run with `CREATE OR REPLACE`, so re-running after a fresh extract is safe and doesn't duplicate rows.
- Every table gets two metadata columns, a standard raw-layer habit for tracing where each row came from:
  - `_source_file`: the JSON file the row came from.
  - `_loaded_at`: when the load ran.
- Committed the script and an updated `.gitignore` to git. The data itself (`raw_data/`, `data/*.duckdb*`) stays out of the repo because the pipeline can rebuild it.

## How the script works

1. Connects through the existing `db/duckdb_connection.py` module (`duckdb_conn()`), so it writes to the same `data/baltimore.duckdb` as everything else.
2. Reads each file with DuckDB's `read_json_auto` and detects which layout it has:
   - a plain list of records,
   - ArcGIS REST output: `{"features": [{"attributes": {...}, "geometry": {...}}]}`,
   - a bare list of ArcGIS features: `[{"attributes": {...}, "geometry": {...}}]` (what my extract scripts actually save),
   - GeoJSON: `{"features": [{"properties": {...}, "geometry": {...}}]}`.
3. For feature-based files, it expands each record's `attributes` (or `properties`) into normal columns, one row per record. It keeps `geometry` as a single struct column (`x`, `y`) in case coordinates are needed later.
4. Raises DuckDB's 16 MB single-object limit (`maximum_object_size`), because ArcGIS files are one giant JSON object.
5. Logs the row and column count per table. A missing or broken file logs a warning or error and the remaining files still load.

## Usage

Run from the project root, with the DuckDB CLI closed:

```
python load/load_raw.py
```

Verify in the CLI:

```
duckdb data/baltimore.duckdb
```

```sql
SHOW ALL TABLES;
SELECT count(*) FROM raw.permits;
DESCRIBE raw.permits;
SELECT * FROM raw.permits LIMIT 5;
```

## Gotchas and lessons learned

1. **Watch the path when opening DuckDB.** `duckdb data.baltimore.duckdb` (a dot) and `duckdb baltimore.duckdb` (no folder) each create a new, empty database instead of opening the real one. The correct command is `duckdb data/baltimore.duckdb`, and the prompt should read `baltimore D`.
2. **Point the script at the data. Don't move the data to fit the script.** My extract scripts write to `raw_data/`, so I updated `EXTRACT_DIR` and the file names in `load_raw.py` rather than moving folders, which would have broken the extracts. Also, `api_real_property.json` is named differently from the other four (no `_response`).
3. **Close the CLI before running the script.** Only one program can write to a DuckDB file at a time. With the CLI open, Python fails with "Could not set lock on file". Exit with `.quit`.
4. **Tables live inside the `.duckdb` file.** Like schemas, they don't appear in the file explorer. `raw.permits` means the `permits` table in the `raw` schema of `data/baltimore.duckdb`.
5. **`SHOW TABLES` only lists the current schema (`main`).** It came back empty even though the load worked. Use `SHOW ALL TABLES;`, or `USE raw;` and then `SHOW TABLES;`.
6. **Ignore DuckDB's companion files too.** DuckDB can write a `.wal` file next to the database, so the ignore rule became `data/*.duckdb*` instead of `data/*.duckdb`.
7. **Check the columns, not just the row count.** The first version of the script assumed ArcGIS files were wrapped in `{"features": [...]}`. My extract scripts save a bare list of features, so the tables loaded with the right row counts but only two columns, `attributes` and `geometry`, each holding a whole record as a nested struct. `SHOW ALL TABLES` revealed it. I updated the script to detect bare feature lists and re-ran it. Now every field (`Neighborhood`, `DateNotice`, `BLOCKLOT` and so on) is its own column.
8. **`git status` catches stray files.** A stray `baltimore.duckdb` showed up in the project root as untracked. I compared file sizes and checked the real database with `duckdb data/baltimore.duckdb -c "SHOW ALL TABLES;"`, then deleted the stray file. I kept the ignore rule scoped to `data/` so future strays stay visible.

## Verified

- All five tables exist in the `raw` schema of `data/baltimore.duckdb`, with row counts recorded above.
- Record fields are flattened into individual columns (checked with `DESCRIBE raw.vacants`).
- No stray database files in the project root.
- `git status` shows only code changes. The data files are correctly ignored.

## Next up (step 5)

- Explore the raw tables: column names, data types, null rates, date formats and neighborhood fields, so I know what needs cleaning.
- Set up dbt (`dbt-duckdb`) and build the first `staging` models: rename columns, cast types, standardize neighborhood names and drop unusable rows.
