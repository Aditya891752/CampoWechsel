"""
Spatial Grid and Field Vulnerability Engine for Field Shift.
Generates a 3x3 spatial grid around each study county anchor point
to demonstrate spatial variation in NDVI, soil moisture, and heat vulnerability.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from fieldshift.config import COUNTIES, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_county_spatial_grid(county_key: str) -> Dict[str, Any]:
    """
    Generate 3x3 spatial grid cells around county anchor point.
    """
    county = COUNTIES[county_key]
    c_lat = county["lat"]
    c_lon = county["lon"]
    step = 0.07  # ~7.5 km grid spacing

    # Offsets in (d_lat, d_lon)
    grid_offsets = [
        ("NW", step, -step, "Northwest Upland"),
        ("N",  step, 0.0,   "North Tableland"),
        ("NE", step, step,  "Northeast Transition"),
        ("W",  0.0,  -step, "West Flats"),
        ("C",  0.0,  0.0,   f"{county['seat']} Anchor Hub"),
        ("E",  0.0,  step,  "East Plains"),
        ("SW", -step, -step, "Southwest Terrace"),
        ("S",  -step, 0.0,   "South Draw"),
        ("SE", -step, step,  "Southeast Plain"),
    ]

    features = []
    cells_list = []

    for idx, (code, d_lat, d_lon, label) in enumerate(grid_offsets, start=1):
        lat = round(c_lat + d_lat, 4)
        lon = round(c_lon + d_lon, 4)
        cell_id = f"{county_key[:3].upper()}-{code}"

        if county_key == "Thomas":
            # Variation across Thomas County
            ndvi_val = round(0.55 + (d_lat * 0.4) - (d_lon * 0.2), 3)
            heat_val = round(33.9 - (d_lat * 8.0) + (d_lon * 5.0), 1)
            soil_moist = round(0.38 + (d_lon * 0.1), 3)
            bare_mo = 4 if d_lat >= 0 else 5
            vuln_type = "Severe Wind Detachment Zone" if d_lat > 0 else "Prolonged Fallow Moisture Deficit"
            priority_rec = "Wheat w/ Legume Cover" if d_lat > 0 else "Wheat–Sorghum–Fallow"
        else:
            # Variation across Finney County
            ndvi_val = round(0.78 - (d_lat * 0.3) + (d_lon * 0.2), 3)
            heat_val = round(42.3 + (d_lat * 6.0) - (d_lon * 4.0), 1)
            soil_moist = round(0.34 - (d_lat * 0.08), 3)
            bare_mo = 5 if d_lat < 0 else 4
            vuln_type = "Critical Ogallala Drawdown Zone" if d_lat < 0 else "High Atmospheric Heat Stress"
            priority_rec = "Corn–Wheat–Sorghum" if d_lat < 0 else "Corn–Soybean"

        props = {
            "cell_id": cell_id,
            "county": county_key,
            "label": label,
            "lat": lat,
            "lon": lon,
            "peak_ndvi": ndvi_val,
            "annual_heat_days": heat_val,
            "root_zone_moisture": soil_moist,
            "bare_months_count": bare_mo,
            "vulnerability_classification": vuln_type,
            "recommended_strategy": priority_rec,
        }
        cells_list.append(props)

        # Polygon bounding box for Folium GeoJSON (~7km tile)
        half = step / 2.0
        coords = [
            [lon - half, lat - half],
            [lon + half, lat - half],
            [lon + half, lat + half],
            [lon - half, lat + half],
            [lon - half, lat - half],
        ]
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
        })

    geojson = {
        "type": "FeatureCollection",
        "county": county_key,
        "anchor_lat": c_lat,
        "anchor_lon": c_lon,
        "cells": cells_list,
        "geojson": {
            "type": "FeatureCollection",
            "features": features,
        },
    }
    return geojson


def generate_all_spatial_grids():
    """Build and save spatial grid layers for both counties."""
    spatial_dict = {}
    for c in COUNTIES.keys():
        logger.info(f"Building 3x3 spatial vulnerability grid for {c} County...")
        spatial_dict[c] = build_county_spatial_grid(c)

    out_file = PROCESSED_DATA_DIR / "spatial_grid.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(spatial_dict, f, indent=2)
    logger.info(f"Saved spatial grid data to {out_file}")
    return spatial_dict


if __name__ == "__main__":
    grids = generate_all_spatial_grids()
    print("\n--- Thomas County Spatial Grid Sample ---")
    print(json.dumps(grids["Thomas"]["cells"][:3], indent=2))
