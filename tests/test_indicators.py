"""
Unit tests for indicators engine in Field Shift.
"""
import pytest
import pandas as pd
from fieldshift.engine.indicators import calculate_dry_spells, compute_county_indicators

def test_dry_spells_calculation():
    # 5 dry days, 1 rain day, 3 dry days
    precip = pd.Series([0.0, 0.2, 0.5, 0.0, 0.1, 15.0, 0.0, 0.0, 0.0])
    res = calculate_dry_spells(precip, threshold_mm=1.0)
    assert res["max_dry_days"] == 5
    assert res["mean_dry_days"] == 4.0

def test_thomas_county_indicators():
    inds = compute_county_indicators("Thomas", bare_ndvi_threshold=0.20)
    assert inds["county"] == "Thomas"
    assert inds["heat_stress"]["annual_mean_heat_days"] > 0
    assert inds["frost_risk"]["median_frost_free_days"] > 120
    assert inds["rainfall"]["annual_mean_precip_mm"] > 300
    assert inds["ndvi_bare_field"]["bare_field_months_count"] >= 3
