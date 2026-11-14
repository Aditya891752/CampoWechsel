"""
Agronomic and Climate Indicators Engine for Field Shift: Western Kansas.
Calculates heat-stress days (Tmax >= 35C), frost dates, rainfall variability,
dry-spell duration, and NDVI bare-field windows from daily and monthly observations.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import pandas as pd

from fieldshift.config import (
    COUNTIES,
    PROCESSED_DATA_DIR,
    HEAT_STRESS_TEMP_C,
    FROST_TEMP_C,
    DEFAULT_BARE_FIELD_NDVI,
    DRY_SPELL_RAIN_LIMIT_MM,
)
from fieldshift.pipeline.fetch_power import get_power_dataframe
from fieldshift.pipeline.fetch_ndvi import get_ndvi_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def calculate_dry_spells(precip_series: pd.Series, threshold_mm: float = DRY_SPELL_RAIN_LIMIT_MM) -> Dict[str, Any]:
    """Calculate maximum and mean consecutive dry spell days (rain < threshold_mm)."""
    is_dry = (precip_series < threshold_mm).astype(int)
    # Group consecutive dry days
    dry_periods = []
    current_run = 0
    for val in is_dry:
        if val == 1:
            current_run += 1
        else:
            if current_run > 0:
                dry_periods.append(current_run)
            current_run = 0
    if current_run > 0:
        dry_periods.append(current_run)

    if not dry_periods:
        return {"max_dry_days": 0, "mean_dry_days": 0, "p90_dry_days": 0}

    return {
        "max_dry_days": int(np.max(dry_periods)),
        "mean_dry_days": round(float(np.mean(dry_periods)), 1),
        "p90_dry_days": int(np.percentile(dry_periods, 90)),
    }


def compute_county_indicators(county_key: str, bare_ndvi_threshold: float = DEFAULT_BARE_FIELD_NDVI) -> Dict[str, Any]:
    """
    Compute comprehensive scientific indicators for a county anchor point over 2015–2024.
    """
    power_df = get_power_dataframe(county_key)
    ndvi_df = get_ndvi_dataframe(county_key)

    power_df["year"] = power_df["date"].dt.year
    power_df["month"] = power_df["date"].dt.month
    power_df["day_of_year"] = power_df["date"].dt.dayofyear

    # 1. Heat-Stress Metrics (Tmax >= 35C / 95F)
    heat_mask = power_df["t2m_max"] >= HEAT_STRESS_TEMP_C
    annual_heat_days = power_df[heat_mask].groupby("year").size().reindex(range(2015, 2025), fill_value=0)
    monthly_heat_days = power_df[heat_mask].groupby("month").size().reindex(range(1, 13), fill_value=0)

    heat_indicators = {
        "annual_mean_heat_days": round(float(annual_heat_days.mean()), 1),
        "max_annual_heat_days": int(annual_heat_days.max()),
        "worst_heat_year": int(annual_heat_days.idxmax()),
        "annual_heat_series": {str(yr): int(cnt) for yr, cnt in annual_heat_days.items()},
        "monthly_heat_distribution": {MONTH_NAMES[m - 1]: int(cnt) for m, cnt in monthly_heat_days.items()},
        "max_temp_c": round(float(power_df["t2m_max"].max()), 1),
    }

    # 2. Frost Risk & Growing Window
    # Spring freeze: last date Tmin <= 0C between Jan 1 and June 30
    # Fall freeze: first date Tmin <= 0C between July 1 and Dec 31
    spring_freeze_doys = []
    fall_freeze_doys = []

    for yr, group in power_df.groupby("year"):
        spring_group = group[group["month"] <= 6]
        freezes_spring = spring_group[spring_group["t2m_min"] <= FROST_TEMP_C]
        if not freezes_spring.empty:
            spring_freeze_doys.append(freezes_spring["day_of_year"].max())

        fall_group = group[group["month"] >= 7]
        freezes_fall = fall_group[fall_group["t2m_min"] <= FROST_TEMP_C]
        if not freezes_fall.empty:
            fall_freeze_doys.append(freezes_fall["day_of_year"].min())

    median_spring_doy = int(np.median(spring_freeze_doys)) if spring_freeze_doys else 115
    median_fall_doy = int(np.median(fall_freeze_doys)) if fall_freeze_doys else 285
    growing_season_length = median_fall_doy - median_spring_doy

    # Convert DOY to representative calendar dates
    dummy_date = pd.to_datetime("2024-01-01")
    median_spring_date = (dummy_date + pd.Timedelta(days=median_spring_doy - 1)).strftime("%B %d")
    median_fall_date = (dummy_date + pd.Timedelta(days=median_fall_doy - 1)).strftime("%B %d")

    frost_indicators = {
        "median_last_spring_freeze_doy": median_spring_doy,
        "median_last_spring_freeze_date": median_spring_date,
        "median_first_fall_freeze_doy": median_fall_doy,
        "median_first_fall_freeze_date": median_fall_date,
        "median_frost_free_days": growing_season_length,
    }

    # 3. Rainfall Climatology & Variability
    annual_precip = power_df.groupby("year")["prectotcorr"].sum()
    monthly_precip = power_df.groupby("month")["prectotcorr"].agg(["mean", "std"])
    precip_mean = float(annual_precip.mean())
    precip_std = float(annual_precip.std())
    precip_cv = round(precip_std / precip_mean, 2) if precip_mean > 0 else 0.0

    dry_spells = calculate_dry_spells(power_df["prectotcorr"])

    rainfall_indicators = {
        "annual_mean_precip_mm": round(precip_mean, 1),
        "annual_mean_precip_inches": round(precip_mean / 25.4, 1),
        "annual_precip_std_mm": round(precip_std, 1),
        "rainfall_variability_cv": precip_cv,
        "max_dry_spell_days": dry_spells["max_dry_days"],
        "mean_dry_spell_days": dry_spells["mean_dry_days"],
        "p90_dry_spell_days": dry_spells["p90_dry_days"],
        "monthly_precip_mm": {
            MONTH_NAMES[m - 1]: {
                "mean": round(float(row["mean"]), 1),
                "std": round(float(row["std"]), 1),
            }
            for m, row in monthly_precip.iterrows()
        },
    }

    # 4. NDVI Bare-Field Analysis
    ndvi_df["month"] = ndvi_df["date"].dt.month
    monthly_ndvi_clim = ndvi_df.groupby("month")["ndvi"].agg(["mean", "std", "min", "max"]).reset_index()

    bare_months_list = []
    for _, row in monthly_ndvi_clim.iterrows():
        m_idx = int(row["month"])
        if row["mean"] < bare_ndvi_threshold:
            bare_months_list.append({
                "month_num": m_idx,
                "month_name": MONTH_NAMES[m_idx - 1],
                "mean_ndvi": round(float(row["mean"]), 3),
            })

    bare_month_names = [m["month_name"] for m in bare_months_list]
    ndvi_indicators = {
        "threshold": bare_ndvi_threshold,
        "bare_field_months_count": len(bare_months_list),
        "bare_field_months": bare_month_names,
        "bare_field_summary": f"Bare field detected for {len(bare_months_list)} months ({', '.join(bare_month_names)}) with NDVI < {bare_ndvi_threshold:.2f}",
        "monthly_climatology": [
            {
                "month": int(r["month"]),
                "month_name": MONTH_NAMES[int(r["month"]) - 1],
                "mean": round(float(r["mean"]), 4),
                "std": round(float(r["std"]), 4),
                "min": round(float(r["min"]), 4),
                "max": round(float(r["max"]), 4),
                "is_bare": bool(r["mean"] < bare_ndvi_threshold),
            }
            for _, r in monthly_ndvi_clim.iterrows()
        ],
    }

    # 5. Root-Zone Soil Moisture
    monthly_soil_wet = power_df.groupby("month")["gwetroot"].mean()
    soil_indicators = {
        "mean_root_zone_wetness": round(float(power_df["gwetroot"].mean()), 3),
        "monthly_root_zone_wetness": {MONTH_NAMES[m - 1]: round(float(val), 3) for m, val in monthly_soil_wet.items()},
        "is_proxy": True,
        "proxy_source": "NASA_POWER_MERRA2_GWETROOT",
    }

    return {
        "county": county_key,
        "heat_stress": heat_indicators,
        "frost_risk": frost_indicators,
        "rainfall": rainfall_indicators,
        "ndvi_bare_field": ndvi_indicators,
        "soil_moisture": soil_indicators,
    }


def generate_all_indicators() -> Dict[str, Any]:
    """Compute and save indicators for both study counties."""
    all_indicators = {}
    for c in COUNTIES.keys():
        logger.info(f"Computing indicators for {c} County...")
        all_indicators[c] = compute_county_indicators(c)

    out_file = PROCESSED_DATA_DIR / "indicators.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_indicators, f, indent=2)
    logger.info(f"Saved all scientific indicators to {out_file}")
    return all_indicators


if __name__ == "__main__":
    inds = generate_all_indicators()
    for c, data in inds.items():
        print(f"\n================ {c} County Indicators ================")
        print(f"Heat Stress: Avg {data['heat_stress']['annual_mean_heat_days']} days/yr (Worst: {data['heat_stress']['worst_heat_year']} with {data['heat_stress']['max_annual_heat_days']} days)")
        print(f"Frost Window: Last Spring Freeze {data['frost_risk']['median_last_spring_freeze_date']} | First Fall Freeze {data['frost_risk']['median_first_fall_freeze_date']} ({data['frost_risk']['median_frost_free_days']} frost-free days)")
        print(f"Rainfall: Mean {data['rainfall']['annual_mean_precip_inches']}\" ({data['rainfall']['annual_mean_precip_mm']} mm) | CV: {data['rainfall']['rainfall_variability_cv']} | Max Dry Spell: {data['rainfall']['max_dry_spell_days']} days")
        print(f"NDVI Bare-Field: {data['ndvi_bare_field']['bare_field_summary']}")
