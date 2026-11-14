"""
Unit tests for scoring engine in Field Shift.
"""
import pytest
import json
from fieldshift.config import PROCESSED_DATA_DIR, CRITERIA
from fieldshift.engine.scoring import (
    normalize_weights,
    map_3_slider_to_criteria_weights,
    score_strategies,
    load_strategies_ratings,
)

def test_normalize_weights():
    raw = {"water": 5.0, "cover": 5.0, "organic_matter": 0.0}
    norm = normalize_weights(raw)
    assert abs(sum(norm.values()) - 1.0) < 1e-3
    assert norm["water"] == 0.5
    assert norm["cover"] == 0.5

def test_3_slider_mapping():
    w = map_3_slider_to_criteria_weights(save_water=8, protect_soil=5, earn_income=3)
    assert abs(sum(w.values()) - 1.0) < 1e-3
    assert w["water"] > w["income"]

def test_scoring_monotonicity_and_bounds():
    with open(PROCESSED_DATA_DIR / "indicators.json", "r") as f:
        inds = json.load(f)
    results = score_strategies("Thomas", inds["Thomas"])
    assert len(results) == 4
    for r in results:
        assert 1.0 <= r["score"] <= 5.0
        for k, v in r["criteria_breakdown"].items():
            assert 0.70 <= v["adjustment_a"] <= 1.10
