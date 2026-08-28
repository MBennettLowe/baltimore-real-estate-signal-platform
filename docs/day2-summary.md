# Day 2 Summary: Pipeline Debugging + Data Validation

**Project:** Baltimore City Real Estate Investment Signal Platform

## Layer Discovery — DHCD Bundle Service

`Housing/DHCD_Open_Baltimore_Datasets/FeatureServer` turned out to be a 13-layer bundle service, not a single-dataset endpoint like `RealProperty_OB`. Queried the service root (`?f=json`) to get the authoritative layer list and confirmed the three layers this project uses:

| ID | Name | Used for |
|---|---|---|
| 1 | Vacant Building Notice - Open | `vacants.py` |
| 2 | Rehabs of Vacant Buildings | `rehabs_vacant.py` |
| 3 | Building Permits | `permits.py` |

`RealProperty_OB` (layer 0) and `Tax_Lien_Certificate_Sale_Properties1` (layer 0) each live on their own single-layer FeatureServer, so no layer index needed there beyond `/0`.

## Bugs Found and Fixed

**Missing `/query` on `BASE_URL`.** `real_property.py` and (separately) `vacants.py` were pointed at the layer root instead of the query endpoint. The layer root still returns HTTP 200 with metadata, so `fetch_all_features` silently parsed it as zero features instead of erroring — no `"features"` key in the response at all. Fix: append `/query` to `BASE_URL`.

**`permits.py` pointed at the wrong layer.** It was hitting layer 1 (Vacant Building Notice) instead of layer 3 (Building Permits) — a copy/paste artifact. This one didn't error; it silently saved vacant-notice records into `api_response_permits.json` under the wrong label. Caught by inspecting the actual field names in the output file (`NoticeNum`, `DateNotice` — permit fields, not present) rather than by any error message.

**Pagination offset bug — the big one.** `arcgis_client.py`'s loop advanced `offset` by the *requested* page size (`record_count`, 2000) rather than by how many records the server actually returned. The DHCD service's real `maxRecordCount` is 1000, so every cycle silently skipped the second half of each block. Net effect: `vacants.py`, `permits.py`, and `rehabs_vacant.py` were all landing at roughly 50% of their true row counts, while `real_property.py` and `tax_lien.py` were unaffected because those services' `maxRecordCount` happened to match the requested 2000. Fix: `offset += len(features)` instead of `offset += record_count`.

**Read timeout on the large permits pull.** `permits.py` timed out ~91% through its run (offset 266,000 of ~290,591) with the original 30-second `timeout`. Since features were only held in memory and written to disk in one shot at the end, the failure lost all 266,000 already-fetched records. Fixed by increasing the request timeout.

## Hardening Added to `helpers/arcgis_client.py`

- Raises on an ArcGIS `"error"` object in the response body instead of silently treating it as zero features.
- New `get_total_count()` helper calls the layer's `returnCountOnly=true` endpoint independent of pagination.
- `fetch_all_features()` now calls `get_total_count()` before paging and prints a warning if the final fetched count doesn't match it — this is what caught the offset bug's true scope across all three affected files.

## Data Validation Result

All five raw files re-verified against live `returnCountOnly` totals after the fixes above:

| File | Status |
|---|---|
| `api_real_property.json` | Matched — unaffected by the offset bug |
| `vacants.json` | Fixed (missing `/query`) + fixed (offset bug), re-run, matched |
| `api_response_permits.json` | Fixed (wrong layer) + fixed (offset bug) + fixed (timeout), re-run, matched |
| `rehabs_vacant.json` | Fixed (offset bug), re-run, matched |
| `tax_lien.json` | Matched — unaffected by the offset bug (renamed from `tax_lein.json` typo) |

## Repo Hygiene

- Added `.gitignore`: `raw_data/` (large JSON dumps, some 1GB+), `.venv/`, `__pycache__/`. Scripts, `helpers/`, `requirements.txt`, and `docs/` remain tracked so the pipeline stays reproducible from git alone.
- Renamed the ad hoc `script.py` exploration file to `explore_arcgis_layers.py` for clarity; verified its layer references were already correct.

## Next Up

Cleaning and loading the five validated raw JSON files into DuckDB.
