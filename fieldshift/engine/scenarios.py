"""
Scenario Perturbation Engine for Field Shift: Western Kansas.
Perturbs precipitation (-30% to +20%) and temperature (0 to +3C),
recalculating indicators and dynamic scoring live.
"""
from typing import Dict, Any
import copy

def perturb_indicators(
    base_indicators: Dict[str, Any],
    temp_delta_c: float = 0.0,
    rain_delta_pct: float = 0.0,
) -> Dict[str, Any]:
    """
    Apply temperature and precipitation shifts to indicators.
    """
    indicators = copy.deepcopy(base_indicators)

    # 1. Adjust Heat Stress Days
    base_heat_days = indicators.get("heat_stress", {}).get("annual_mean_heat_days", 30.0)
    # Approximately 7 additional days >= 35C per +1C in Western Kansas summer
    added_heat_days = round(temp_delta_c * 7.5, 1)
    indicators["heat_stress"]["annual_mean_heat_days"] = max(0.0, base_heat_days + added_heat_days)

    # 2. Adjust Rainfall
    base_rain_mm = indicators.get("rainfall", {}).get("annual_mean_precip_mm", 500.0)
    adjusted_rain_mm = round(base_rain_mm * (1.0 + (rain_delta_pct / 100.0)), 1)
    indicators["rainfall"]["annual_mean_precip_mm"] = adjusted_rain_mm
    indicators["rainfall"]["annual_mean_precip_inches"] = round(adjusted_rain_mm / 25.4, 1)

    # 3. Adjust Dry Spells & Variability
    base_dry_spell = indicators.get("rainfall", {}).get("max_dry_spell_days", 45)
    if rain_delta_pct < 0:
        indicators["rainfall"]["max_dry_spell_days"] = int(base_dry_spell * (1.0 + abs(rain_delta_pct) / 60.0))
    else:
        indicators["rainfall"]["max_dry_spell_days"] = max(20, int(base_dry_spell * (1.0 - rain_delta_pct / 100.0)))

    # 4. Adjust Root-zone Soil Wetness
    base_wetness = indicators.get("soil_moisture", {}).get("mean_root_zone_wetness", 0.35)
    wetness_shift = (rain_delta_pct / 100.0) * 0.08 - (temp_delta_c * 0.02)
    indicators["soil_moisture"]["mean_root_zone_wetness"] = round(max(0.15, min(0.60, base_wetness + wetness_shift)), 3)

    return indicators
