# helpers/arcgis_client.py
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def get_total_count(base_url, where="1=1", session=None, timeout=30):
    """Ask the layer directly for its true row count, independent of pagination."""
    session = session or build_session()
    params = {"where": where, "returnCountOnly": "true", "f": "json"}
    resp = session.get(base_url, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS error getting count for {base_url}: {data['error']}")
    return data["count"]


def fetch_all_features(base_url, where="1=1", out_fields="*", record_count=2000, sleep_between=0.5, session=None):
    """Page through an ArcGIS FeatureServer/MapServer query endpoint, return all features as a list."""
    session = session or build_session()
    all_features = []
    offset = 0

    expected_total = get_total_count(base_url, where=where, session=session)
    print(f"Expected total (returnCountOnly): {expected_total}")

    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": record_count,
        }
        resp = session.get(base_url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise RuntimeError(f"ArcGIS error for {base_url}: {data['error']}")

        features = data.get("features", [])
        all_features.extend(features)
        print(f"Fetched {len(features)} at offset {offset} (total: {len(all_features)})")

        if not features or not data.get("exceededTransferLimit", False):
            break

        offset += len(features)   # advance by what the server actually returned, not what you asked for
        time.sleep(sleep_between)

    gap = expected_total - len(all_features)
    if gap != 0:
        print(f"WARNING: fetched {len(all_features)} but returnCountOnly reports {expected_total} "
              f"(gap of {gap}). If gap is small, likely live edits during the run; "
              f"if gap is large, pagination is still incomplete.")

    return all_features