"""
Unit tests for Phase 1 features: SMAP anomalies, CDL history, SSURGO soils, SRTM slope, and spatial grid.
"""
import pytest
import json
from fieldshift.config import PROCESSED_DATA_DIR
from fieldshift.pipeline.fetch_smap import compute_smap_soil_moisture_anomalies
from fieldshift.pipeline.fetch_cdl import get_cdl_crop_history
from fieldshift.pipeline.fetch_soils import get_ssurgo_soil_properties
from fieldshift.pipeline.fetch_srtm import get_srtm_terrain_analysis
from fieldshift.engine.spatial_grid import build_county_spatial_grid

def test_smap_monthly_anomalies():
    df = compute_smap_soil_moisture_anomalies("Thomas")
    assert len(df) == 120  # 10 years * 12 months
    assert "anomaly_z" in df.columns
    assert "drought_category" in df.columns
    # Check that anomalies roughly center near 0
    assert -3.0 < df["anomaly_z"].mean() < 3.0

def test_cdl_crop_history():
    cdl_t = get_cdl_crop_history("Thomas")
    assert "Winter Wheat" in cdl_t["average_annual_acreage_pct"]
    assert cdl_t["average_annual_acreage_pct"]["Winter Wheat"] > 40.0
    cdl_f = get_cdl_crop_history("Finney")
    assert "Field Corn (Center-Pivot Irrigated)" in cdl_f["average_annual_acreage_pct"]

def test_ssurgo_and_srtm():
    soils = get_ssurgo_soil_properties("Thomas")
    assert "Keith silt loam" in soils["dominant_soil_series"]
    assert soils["available_water_capacity_awc"]["value_inches_per_foot"] > 1.5

    srtm = get_srtm_terrain_analysis("Thomas")
    assert srtm["mean_slope_pct"] < 2.0  # Flat tablelands
    assert "why_wind_drives_erosion" in srtm

def test_spatial_grid():
    grid = build_county_spatial_grid("Thomas")
    assert len(grid["cells"]) == 9  # 3x3 grid
    assert len(grid["geojson"]["features"]) == 9
    for cell in grid["cells"]:
        assert 35.0 < cell["lat"] < 42.0
        assert -103.0 < cell["lon"] < -98.0
