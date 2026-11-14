"""
Unit tests for Phase 2 stretch features: Groundwater, OpenET, LST, NASS yields, Report Generator, and i18n.
"""
import pytest
from fieldshift.pipeline.fetch_groundwater import get_groundwater_data
from fieldshift.pipeline.fetch_openet import calculate_crop_water_demand
from fieldshift.pipeline.fetch_lst import get_lst_thermal_hotspots
from fieldshift.pipeline.fetch_nass_yields import get_nass_yield_and_market_data
from fieldshift.engine.report_generator import generate_html_report
from fieldshift.i18n import get_text
from fieldshift.config import PERSONAS
import json
from fieldshift.config import PROCESSED_DATA_DIR

def test_groundwater_and_grace():
    gw = get_groundwater_data("Finney")
    assert gw["total_decline_ft_since_1990"] > 50.0
    assert len(gw["hydrograph"]) > 10
    assert "GRACE-FO" in gw["grace_fo_context"]

def test_openet_water_savings():
    openet = calculate_crop_water_demand("Finney")
    budgets = openet["strategies_water_budget"]
    cws = next(b for b in budgets if "Corn–Wheat–Sorghum" in b["strategy"])
    assert cws["gallons_saved_per_pivot"] > 20_000_000  # Over 20 million gallons saved per pivot!
    assert cws["water_savings_vs_existing_pct"] > 35.0

def test_lst_thermal_hotspot():
    lst = get_lst_thermal_hotspots("Thomas")
    assert lst["bare_fallow_surface_temp_f"] > 115.0
    assert lst["canopy_cooling_differential_c"] < -8.0

def test_nass_and_prism():
    nass = get_nass_yield_and_market_data("Thomas")
    assert "winter_wheat_bu_acre" in nass["yields"]
    assert nass["satellite_vs_ground"]["correlation_coefficient"] > 0.90

def test_report_generation():
    with open(PROCESSED_DATA_DIR / "indicators.json", "r") as f:
        inds = json.load(f)
    with open(PROCESSED_DATA_DIR / "evidence.json", "r") as f:
        ev = json.load(f)
    html = generate_html_report("Thomas", PERSONAS["dryland_wheat"]["title"], inds["Thomas"], ev["Thomas"], {"water": 0.5})
    assert "<!DOCTYPE html>" in html
    assert "Field Shift: Executive Crop-Rotation Report" in html
    assert "Wheat with legume cover" in html

def test_i18n_localization():
    assert get_text("title", "en") == "Field Shift: Western Kansas"
    assert "फ़ील्ड शिफ्ट" in get_text("title", "hi")
    assert get_text("save_water", "hi") != get_text("save_water", "en")
