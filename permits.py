#permits.py
import os
import json
from helpers.arcgis_client import fetch_all_features

BASE_URL = "https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/3/query"
OUT_PATH = os.path.join("raw_data", "api_response_permits.json")

os.makedirs("raw_data", exist_ok=True)
features = fetch_all_features(BASE_URL)

with open(OUT_PATH, "w") as f:
    json.dump(features, f, indent=4)

print(f"Saved {len(features)} records to {OUT_PATH}")
print(f"File successfully saved to: {OUT_PATH}")