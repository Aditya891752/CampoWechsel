"""
Fetch and cache NASA POWER daily agroclimatology data (2015–2024)
for Western Kansas study anchor points.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import requests

from fieldshift.config import (
    COUNTIES,
    ALLOWED_COUNTIES,
    NASA_POWER_BASE_URL,
    NASA_POWER_COMMUNITY,
    NASA_POWER_PARAMETERS,
    RAW_DATA_DIR,
    START_DATE_STR,
    END_DATE_STR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def fetch_power_raw(county_key: str, force_download: bool = False) -> dict:
    """
    Fetch daily NASA POWER agroclimatology data via REST API or load from raw cache.
    """
    if county_key not in ALLOWED_COUNTIES:
        raise ValueError(f"County '{county_key}' is not in allowed counties: {ALLOWED_COUNTIES}")

    cache_file = RAW_DATA_DIR / f"power_{county_key.lower()}.json"
    if cache_file.exists() and not force_download:
        logger.info(f"Loading cached NASA POWER data from {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    county_info = COUNTIES[county_key]
    params = {
        "parameters": ",".join(NASA_POWER_PARAMETERS),
        "community": NASA_POWER_COMMUNITY,
        "longitude": county_info["lon"],
        "latitude": county_info["lat"],
        "start": START_DATE_STR,
        "end": END_DATE_STR,
        "format": "JSON",
    }

    logger.info(f"Querying NASA POWER API for {county_key} ({county_info['lat']}, {county_info['lon']})...")
    response = requests.get(NASA_POWER_BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    # Save immutable raw cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved raw NASA POWER payload to {cache_file}")

    return data


def parse_power_to_dataframe(raw_data: dict, county_key: str) -> pd.DataFrame:
    """
    Parse NASA POWER JSON structure into a clean, typed daily DataFrame.
    NASA POWER format: properties -> parameter -> {PARAM_NAME: {YYYYMMDD: val}}
    """
    parameters = raw_data.get("properties", {}).get("parameter", {})
    if not parameters:
        raise ValueError("NASA POWER response missing 'properties.parameter' object.")

    # All parameter series share the same date keys
    sample_key = next(iter(parameters.keys()))
    date_strings = sorted(parameters[sample_key].keys())

    records = []
    for d_str in date_strings:
        row = {
            "date": pd.to_datetime(d_str, format="%Y%m%d"),
            "location": county_key,
        }
        for param in NASA_POWER_PARAMETERS:
            val = parameters.get(param, {}).get(d_str, np.nan)
            # -999.0 is NASA POWER fill value for missing/invalid
            if val == -999.0 or val == "-999.0":
                val = np.nan
            row[param.lower()] = float(val) if val is not None else np.nan
        records.append(row)

    df = pd.DataFrame(records)
    # Ensure correct sorting and fill any isolated single-day NaN via linear interpolation
    df = df.sort_values("date").reset_index(drop=True)
    numeric_cols = [p.lower() for p in NASA_POWER_PARAMETERS]
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear").bfill().ffill()
    return df


def get_power_dataframe(county_key: str, force_download: bool = False) -> pd.DataFrame:
    """Convenience getter returning clean daily DataFrame."""
    raw = fetch_power_raw(county_key, force_download=force_download)
    return parse_power_to_dataframe(raw, county_key)


if __name__ == "__main__":
    for c in ["Thomas", "Finney"]:
        df = get_power_dataframe(c)
        print(f"\n--- {c} County Daily NASA POWER ({len(df)} rows) ---")
        print(df.head())
        print(df.describe().T[["count", "mean", "min", "max"]])
