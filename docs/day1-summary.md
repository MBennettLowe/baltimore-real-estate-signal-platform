# Day 1 Summary: Setup + Endpoint Discovery (~1 hr)

**Project:** Baltimore City Real Estate Investment Signal Platform

## Environment Setup
- `git init` for the repo
- Created a Python virtual environment
- Installed: `requests`, `duckdb`, `dbt-core`, `dbt-duckdb`

## Endpoint Discovery
Found and verified 4 live ArcGIS FeatureServer endpoints on data.baltimorecity.gov, each confirmed to return data via a `requests.get()` test. No API keys required — all public FeatureServers.

| Dataset | URL | Update Frequency | Auth |
|---|---|---|---|
| Real Property Information | https://baltegis.baltimorecity.gov/mapping/rest/services/CityView/RealProperty_OB/FeatureServer | Weekly | None |
| Housing and Building Permits (2019–Present) | https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/3 | Not stated — confirm by diffing pulls over a few days | None |
| Vacant Building Notices | https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/1 | Daily | None |
| Tax Lien Certificate Sale Properties | https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Tax_Lien_Certificate_Sale_Properties1/FeatureServer | Annual (per tax-sale cycle) | None |

*Layer IDs verified 2026-07-21 — re-check against current docs if revisiting after a gap, since IDs can shift.*
