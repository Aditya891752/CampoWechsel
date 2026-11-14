"""
Unit tests for scoring engine numerical stability and benchmark verification.
"""
from fieldshift.benchmark import run_monte_carlo_benchmark


def test_scoring_numerical_stability_thomas():
    result = run_monte_carlo_benchmark(iterations=200, county_key="Thomas")
    assert result["is_stable"] is True
    assert result["nan_count"] == 0
    assert result["inf_count"] == 0
    assert result["avg_latency_ms"] < 10.0  # Must be fast (<10ms per score run)
    assert 0.70 <= result["min_score"] <= 5.50
    assert 0.70 <= result["max_score"] <= 5.50


def test_scoring_numerical_stability_finney():
    result = run_monte_carlo_benchmark(iterations=200, county_key="Finney")
    assert result["is_stable"] is True
    assert result["nan_count"] == 0
    assert result["inf_count"] == 0
    assert result["avg_latency_ms"] < 10.0
    assert 0.70 <= result["min_score"] <= 5.50
    assert 0.70 <= result["max_score"] <= 5.50
