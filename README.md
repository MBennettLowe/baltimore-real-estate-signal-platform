# baltimore-real-estate-signal-platform

## Data Sources

Live ArcGIS FeatureServer URLs verified against data.baltimorecity.gov on 2026-07-21. Layer IDs can shift — re-verify against current docs rather than trusting this table blindly if it's been a while.

| Dataset | URL | Update Frequency | Auth Notes |
|---|---|---|---|
| Real Property Information | https://baltegis.baltimorecity.gov/mapping/rest/services/CityView/RealProperty_OB/FeatureServer | Weekly | None — public FeatureServer, no API key |
| Housing and Building Permits (2019–Present) | https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/3 | Not stated in source metadata — confirm by diffing pulls over a few days | None — public FeatureServer, no API key |
| Vacant Building Notices | https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/1 | Daily | None — public FeatureServer, no API key |
| Tax Lien Certificate Sale Properties | https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Tax_Lien_Certificate_Sale_Properties1/FeatureServer | Annual — refreshed per tax-sale cycle (redemption status may update afterward) | None — public FeatureServer, no API key |
