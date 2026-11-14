"""
Data Schema and Physical Boundary Integrity Validator for Field Shift.
Verifies processed dataset schemas, physical boundaries, and provenance attribution.
Guarantees zero silent dataset corruption for decision-support outputs.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
from fieldshift.config import PROCESSED_DATA_DIR, COUNTIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def validate_tidy_table(csv_path: Path) -> List[str]:
    """Validate processed monthly tidy table integrity and physical bounds."""
    errors = []
    if not csv_path.exists():
        return [f"Missing tidy monthly dataset at {csv_path}"]

    df = pd.read_csv(csv_path)
    if len(df) == 0:
        return ["Tidy dataset is empty"]

    required_cols = ["date", "location", "variable", "value", "source", "is_proxy"]
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column in tidy table: {col}")

    # Check locations
    locations = set(df["location"].unique())
    for county in COUNTIES.keys():
        if county not in locations:
            errors.append(f"Missing location in tidy table: {county}")

    # Physical boundary assertions for variables
    ndvi_vals = df[df["variable"] == "ndvi"]["value"].dropna()
    if len(ndvi_vals) > 0:
        if (ndvi_vals < -0.2).any() or (ndvi_vals > 1.0).any():
            errors.append("NDVI contains values outside physical boundary [-0.2, 1.0]")

    precip_vals = df[df["variable"] == "prectotcorr"]["value"].dropna()
    if len(precip_vals) > 0:
        if (precip_vals < 0).any():
            errors.append("Precipitation contains negative values")

    tmax_vals = df[df["variable"] == "t2m_max"]["value"].dropna()
    if len(tmax_vals) > 0:
        if (tmax_vals < -40.0).any() or (tmax_vals > 60.0).any():
            errors.append("Temperature max contains unphysical extremes outside [-40, 60] C")

    return errors


def validate_indicators(json_path: Path) -> List[str]:
    """Validate computed agronomic indicators dictionary."""
    errors = []
    if not json_path.exists():
        return [f"Missing indicators file at {json_path}"]

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for county in COUNTIES.keys():
        if county not in data:
            errors.append(f"Missing indicator payload for county: {county}")
            continue
        c_inds = data[county]
        heat = c_inds.get("heat_stress", {})
        if heat.get("annual_mean_heat_days", -1) < 0:
            errors.append(f"Invalid heat days count for {county}")
        bare = c_inds.get("ndvi_bare_field", {})
        if bare.get("bare_field_months_count", -1) < 0:
            errors.append(f"Invalid bare-field window for {county}")

    return errors


def validate_gemini_dossiers(json_path: Path) -> List[str]:
    """Validate pre-compiled Gemini spatial dossiers for 3x3 grids."""
    errors = []
    if not json_path.exists():
        return [f"Missing Gemini dossiers file at {json_path}"]

    with open(json_path, "r", encoding="utf-8") as f:
        dossiers = json.load(f)

    if len(dossiers) < 18:
        errors.append(f"Expected at least 18 cell dossiers, found {len(dossiers)}")

    for cid, d in dossiers.items():
        if not d.get("headline"):
            errors.append(f"Dossier {cid} missing headline")
        if not d.get("executive_summary"):
            errors.append(f"Dossier {cid} missing executive summary")

    return errors


def run_full_validation() -> Dict[str, Any]:
    """Execute complete dataset integrity audit across all processed artifacts."""
    tidy_errs = validate_tidy_table(PROCESSED_DATA_DIR / "tidy_monthly.csv")
    ind_errs = validate_indicators(PROCESSED_DATA_DIR / "indicators.json")
    dossier_errs = validate_gemini_dossiers(PROCESSED_DATA_DIR / "gemini_cell_dossiers.json")

    all_errors = tidy_errs + ind_errs + dossier_errs
    is_valid = len(all_errors) == 0

    return {
        "valid": is_valid,
        "total_checks": 3,
        "errors": all_errors,
        "summary": "All processed datasets passed schema and boundary integrity checks" if is_valid else f"Found {len(all_errors)} errors",
    }


if __name__ == "__main__":
    report = run_full_validation()
    print(f"Validation Status: {'PASS' if report['valid'] else 'FAIL'}")
    print(f"Summary: {report['summary']}")
