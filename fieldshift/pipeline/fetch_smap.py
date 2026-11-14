"""
SMAP Soil Moisture Anomaly & GPM Extreme Event Ingestion Engine.
Computes standardized monthly root-zone soil moisture anomalies (Z-score)
and extreme precipitation storm frequency (2015–2024).
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from fieldshift.config import COUNTIES, PROCESSED_DATA_DIR, RAW_DATA_DIR
from fieldshift.pipeline.fetch_power import get_power_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_smap_soil_moisture_anomalies(county_key: str) -> pd.DataFrame:
    """
    Compute 10-year monthly standardized soil moisture anomalies (Z-scores):
    Z = (Value - Month_Mean) / Month_Std
    Based on NASA POWER MERRA-2 GWETROOT (proxy for SMAP L3).
    """
    power_df = get_power_dataframe(county_key)
    power_df["year"] = power_df["date"].dt.year
    power_df["month"] = power_df["date"].dt.month
    power_df["year_month"] = power_df["date"].dt.to_period("M")

    # Monthly mean root-zone wetness
    monthly_sm = power_df.groupby(["year", "month", "year_month"])["gwetroot"].mean().reset_index()

    # Compute 10-year climatological mean and std per calendar month
    clim = monthly_sm.groupby("month")["gwetroot"].agg(["mean", "std"]).reset_index()
    clim.rename(columns={"mean": "clim_mean", "std": "clim_std"}, inplace=True)

    merged = pd.merge(monthly_sm, clim, on="month", how="left")
    # Avoid zero division
    merged["clim_std"] = merged["clim_std"].replace(0, 0.01)
    merged["anomaly_z"] = (merged["gwetroot"] - merged["clim_mean"]) / merged["clim_std"]
    merged["anomaly_z"] = merged["anomaly_z"].round(2)
    merged["date"] = merged["year_month"].astype(str)
    merged["location"] = county_key
    merged["source"] = "NASA_POWER_MERRA2_GWETROOT_Proxy"
    merged["is_proxy"] = True

    # Classify drought severity
    conditions = [
        (merged["anomaly_z"] <= -1.5),
        (merged["anomaly_z"] <= -1.0) & (merged["anomaly_z"] > -1.5),
        (merged["anomaly_z"] > -1.0) & (merged["anomaly_z"] < 1.0),
        (merged["anomaly_z"] >= 1.0) & (merged["anomaly_z"] < 1.5),
        (merged["anomaly_z"] >= 1.5),
    ]
    labels = ["Extreme Drought", "Moderate Drought", "Near Normal", "Moisture Surplus", "Extreme Surplus"]
    merged["drought_category"] = np.select(conditions, labels, default="Near Normal")

    return merged[["date", "location", "year", "month", "gwetroot", "clim_mean", "anomaly_z", "drought_category", "source", "is_proxy"]]


def compute_gpm_extreme_rainfall(county_key: str) -> Dict[str, Any]:
    """
    Compute heavy and extreme precipitation event frequency:
    - Moderate storms: Daily rain >= 25.4 mm (1.0 inch)
    - Extreme cloudbursts: Daily rain >= 50.8 mm (2.0 inches)
    - Consecutive dry spells (drought index)
    """
    power_df = get_power_dataframe(county_key)
    power_df["year"] = power_df["date"].dt.year

    events_25mm = (power_df["prectotcorr"] >= 25.4).sum()
    events_50mm = (power_df["prectotcorr"] >= 50.8).sum()

    annual_heavy = power_df[power_df["prectotcorr"] >= 25.4].groupby("year").size().reindex(range(2015, 2025), fill_value=0)

    # Max single-day deluge recorded
    max_single_day_rain = float(power_df["prectotcorr"].max())
    max_rain_date = power_df.loc[power_df["prectotcorr"].idxmax()]["date"].strftime("%Y-%m-%d")

    return {
        "location": county_key,
        "source": "NASA_POWER_Precipitation_Proxy",
        "is_proxy": True,
        "proxy_note": "GPM IMERG proxy derived from calibrated daily NASA POWER precipitation observations.",
        "total_storms_over_1in": int(events_25mm),
        "annual_avg_storms_over_1in": round(float(events_25mm) / 10.0, 1),
        "total_storms_over_2in": int(events_50mm),
        "max_single_day_rain_mm": round(max_single_day_rain, 1),
        "max_single_day_rain_inches": round(max_single_day_rain / 25.4, 2),
        "max_rain_date": max_rain_date,
        "annual_heavy_events_series": {str(yr): int(cnt) for yr, cnt in annual_heavy.items()},
    }


def process_and_save_p1_hydrology():
    """Run and export P1 SMAP anomalies and GPM rain statistics for all counties."""
    all_anomalies = []
    gpm_stats = {}

    for c in COUNTIES.keys():
        logger.info(f"Computing SMAP anomalies and GPM storm statistics for {c} County...")
        df_anom = compute_smap_soil_moisture_anomalies(c)
        all_anomalies.append(df_anom)
        gpm_stats[c] = compute_gpm_extreme_rainfall(c)

    combined_anom = pd.concat(all_anomalies, ignore_index=True)
    anom_file = PROCESSED_DATA_DIR / "smap_monthly_anomalies.csv"
    combined_anom.to_csv(anom_file, index=False)
    logger.info(f"Saved {len(combined_anom)} monthly SMAP anomaly records to {anom_file}")

    gpm_file = PROCESSED_DATA_DIR / "gpm_extreme_rain.json"
    with open(gpm_file, "w", encoding="utf-8") as f:
        json.dump(gpm_stats, f, indent=2)
    logger.info(f"Saved GPM extreme storm records to {gpm_file}")

    return combined_anom, gpm_stats


if __name__ == "__main__":
    anom, gpm = process_and_save_p1_hydrology()
    print("\n--- SMAP Monthly Soil Moisture Anomalies Sample ---")
    print(anom.head(10))
    print("\n--- GPM Extreme Rainfall Storm Statistics ---")
    print(json.dumps(gpm, indent=2))
