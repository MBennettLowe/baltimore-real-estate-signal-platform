
#tax_lein.py
import os
import json
from helpers.arcgis_client import fetch_all_features

BASE_URL = "https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Tax_Lien_Certificate_Sale_Properties1/FeatureServer/0/query"
OUT_PATH = os.path.join("raw_data", "api_response_tax_lien.json")

os.makedirs("raw_data", exist_ok=True)
features = fetch_all_features(BASE_URL)

with open(OUT_PATH, "w") as f:
    json.dump(features, f, indent=4)

print(f"Saved {len(features)} records to {OUT_PATH}")
print(f"File successfully saved to: {OUT_PATH}")