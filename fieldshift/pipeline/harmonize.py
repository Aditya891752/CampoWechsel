"""
Harmonization Pipeline for Field Shift: Western Kansas.
Resamples daily NASA POWER and 16-day MODIS NDVI data into a standardized monthly tidy table:
date, location, variable, value, source, is_proxy
"""
import logging
from pathlib import Path
import pandas as pd
import numpy as np

from fieldshift.config import (
    COUNTIES,
    PROCESSED_DATA_DIR,
    HEAT_STRESS_TEMP_C,
)
from fieldshift.pipeline.fetch_power import get_power_dataframe
from fieldshift.pipeline.fetch_ndvi import get_ndvi_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_monthly_tidy_data() -> pd.DataFrame:
    """
    Compile daily NASA POWER and 16-day NDVI data into a single harmonized tidy table.
    Columns: date (YYYY-MM), location, variable, value, source, is_proxy
    """
    tidy_rows = []
    summary_rows = []

    for county_key in COUNTIES.keys():
        logger.info(f"Harmonizing monthly data for {county_key}...")
        power_df = get_power_dataframe(county_key)
        ndvi_df = get_ndvi_dataframe(county_key)

        # 1. Process NASA POWER to monthly
        power_df["year_month"] = power_df["date"].dt.to_period("M")

        monthly_power = power_df.groupby("year_month").agg(
            t2m=("t2m", "mean"),
            t2m_max=("t2m_max", "mean"),
            t2m_min=("t2m_min", "mean"),
            prectotcorr=("prectotcorr", "sum"),
            rh2m=("rh2m", "mean"),
            allsky_sfc_sw_dwn=("allsky_sfc_sw_dwn", "mean"),
            gwetroot=("gwetroot", "mean"),
            heat_days=("t2m_max", lambda s: float((s >= HEAT_STRESS_TEMP_C).sum())),
        ).reset_index()

        # 2. Process NDVI to monthly
        ndvi_df["year_month"] = ndvi_df["date"].dt.to_period("M")
        monthly_ndvi = ndvi_df.groupby("year_month").agg(
            ndvi=("ndvi", "mean")
        ).reset_index()
        ndvi_source = ndvi_df["source"].iloc[0]
        ndvi_is_proxy = bool(ndvi_df["is_proxy"].iloc[0])

        # Merge monthly series
        merged = pd.merge(monthly_power, monthly_ndvi, on="year_month", how="outer").sort_values("year_month")

        for _, row in merged.iterrows():
            ym_str = str(row["year_month"])
            
            # POWER variables (Direct NASA observations)
            power_vars = {
                "t2m": row["t2m"],
                "t2m_max": row["t2m_max"],
                "t2m_min": row["t2m_min"],
                "prectotcorr": row["prectotcorr"],
                "rh2m": row["rh2m"],
                "allsky_sfc_sw_dwn": row["allsky_sfc_sw_dwn"],
                "heat_days": row["heat_days"],
            }
            for v_name, val in power_vars.items():
                if pd.notna(val):
                    tidy_rows.append({
                        "date": ym_str,
                        "location": county_key,
                        "variable": v_name,
                        "value": round(float(val), 3),
                        "source": "NASA_POWER",
                        "is_proxy": False,
                    })

            # Root-zone soil wetness (POWER model-based proxy for SMAP)
            if pd.notna(row["gwetroot"]):
                tidy_rows.append({
                    "date": ym_str,
                    "location": county_key,
                    "variable": "gwetroot",
                    "value": round(float(row["gwetroot"]), 4),
                    "source": "NASA_POWER_MERRA2",
                    "is_proxy": True,
                })

            # MODIS NDVI
            if pd.notna(row["ndvi"]):
                tidy_rows.append({
                    "date": ym_str,
                    "location": county_key,
                    "variable": "ndvi",
                    "value": round(float(row["ndvi"]), 4),
                    "source": ndvi_source,
                    "is_proxy": ndvi_is_proxy,
                })

            # For wide summary table
            sum_row = {"date": ym_str, "location": county_key}
            sum_row.update(power_vars)
            sum_row["gwetroot"] = row["gwetroot"]
            sum_row["ndvi"] = row["ndvi"]
            summary_rows.append(sum_row)

    tidy_df = pd.DataFrame(tidy_rows)
    tidy_path = PROCESSED_DATA_DIR / "tidy_monthly.csv"
    tidy_df.to_csv(tidy_path, index=False)
    logger.info(f"Saved {len(tidy_df)} tidy records to {tidy_path}")

    wide_df = pd.DataFrame(summary_rows)
    wide_path = PROCESSED_DATA_DIR / "monthly_summary.csv"
    wide_df.to_csv(wide_path, index=False)
    logger.info(f"Saved {len(wide_df)} monthly summary records to {wide_path}")

    return tidy_df


if __name__ == "__main__":
    df = build_monthly_tidy_data()
    print(f"\n--- Harmonized Tidy Table ({len(df)} rows) ---")
    print(df.head(15))
    print("\nDistinct variables and sources:")
    print(df.groupby(["variable", "source", "is_proxy"]).size())
