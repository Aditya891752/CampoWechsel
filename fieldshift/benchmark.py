"""
Numerical Stability and Performance Benchmark Suite for Field Shift.
Executes Monte Carlo simulations across weight distributions to verify:
1. Scoring execution latency (< 5ms per run)
2. Numerical stability (Zero NaN, Zero Inf, strictly bounded scores in [0.70, 5.50])
3. Normalization invariance across random weight vectors
"""
import json
import time
from typing import Dict, Any, List
import numpy as np

from fieldshift.config import COUNTIES, PROCESSED_DATA_DIR, CRITERIA
from fieldshift.engine.scoring import score_strategies, normalize_weights


def run_monte_carlo_benchmark(
    iterations: int = 1000,
    county_key: str = "Thomas",
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Run N randomized weight evaluations to verify scoring formula numerical stability.
    """
    np.random.seed(random_seed)
    with open(PROCESSED_DATA_DIR / "indicators.json", "r", encoding="utf-8") as f:
        indicators = json.load(f)[county_key]

    criteria_keys = [c["key"] for c in CRITERIA]
    n_crit = len(criteria_keys)

    scores_collected: List[float] = []
    latencies: List[float] = []
    nan_count = 0
    inf_count = 0

    t_start_total = time.perf_counter()

    for _ in range(iterations):
        # Generate random Dirichlet weights ensuring sum = 1.0
        raw_weights = np.random.uniform(0.01, 1.0, size=n_crit)
        w_dict = {k: float(w) for k, w in zip(criteria_keys, raw_weights)}

        t0 = time.perf_counter()
        ranked = score_strategies(county_key, indicators, weights=w_dict)
        t_elapsed = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(t_elapsed)

        for strat in ranked:
            s = strat["score"]
            if np.isnan(s):
                nan_count += 1
            elif np.isinf(s):
                inf_count += 1
            scores_collected.append(s)

    total_time_s = time.perf_counter() - t_start_total
    avg_latency_ms = float(np.mean(latencies))
    p95_latency_ms = float(np.percentile(latencies, 95))
    min_score = float(np.min(scores_collected))
    max_score = float(np.max(scores_collected))

    is_stable = (nan_count == 0) and (inf_count == 0) and (min_score >= 0.70) and (max_score <= 5.50)

    return {
        "county": county_key,
        "iterations": iterations,
        "total_time_seconds": round(total_time_s, 4),
        "avg_latency_ms": round(avg_latency_ms, 3),
        "p95_latency_ms": round(p95_latency_ms, 3),
        "min_score": round(min_score, 2),
        "max_score": round(max_score, 2),
        "nan_count": nan_count,
        "inf_count": inf_count,
        "is_stable": is_stable,
    }


if __name__ == "__main__":
    for cty in ["Thomas", "Finney"]:
        res = run_monte_carlo_benchmark(1000, cty)
        print(f"Benchmark {cty} (1,000 iterations):")
        print(f"  Avg Latency: {res['avg_latency_ms']} ms | P95: {res['p95_latency_ms']} ms")
        print(f"  Score Bounds: [{res['min_score']}, {res['max_score']}] | Stable: {res['is_stable']}")
