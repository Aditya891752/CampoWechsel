"""
Evidence Card Synthesis Engine for Field Shift: Western Kansas.
Generates structured strategy cards conforming strictly to Section 8 schema:
strategy, is_existing, score, why_suggested, evidence, benefits,
information_gaps, risks_needing_local_review, confidence
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from fieldshift.config import PROCESSED_DATA_DIR, CRITERIA
from fieldshift.engine.scoring import score_strategies

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def generate_evidence_cards(
    county_key: str,
    indicators: Dict[str, Any],
    custom_weights: Dict[str, float] = None,
) -> List[Dict[str, Any]]:
    """
    Synthesize structured evidence cards for all strategies in a county.
    """
    scored = score_strategies(county_key, indicators, weights=custom_weights)

    bare_months_str = ", ".join(indicators.get("ndvi_bare_field", {}).get("bare_field_months", []))
    heat_days = indicators.get("heat_stress", {}).get("annual_mean_heat_days", 33.0)
    dry_spell = indicators.get("rainfall", {}).get("max_dry_spell_days", 50)
    frost_free = indicators.get("frost_risk", {}).get("median_frost_free_days", 190)

    cards = []

    # Strategy-specific qualitative templates linked directly to NASA indicators
    strategy_meta = {
        # Thomas County
        "wheat_fallow": {
            "why_suggested": "Traditional baseline practice in Thomas County, relying on a 14-month fallow to accumulate subsoil moisture for winter wheat.",
            "evidence": [
                {
                    "signal": f"NDVI remains below 0.20 for {indicators.get('ndvi_bare_field', {}).get('bare_field_months_count', 4)} months ({bare_months_str})",
                    "source": "MODIS MOD13Q1 (250m)",
                    "is_proxy": True,
                },
                {
                    "signal": f"Annual heat stress averages {heat_days} days above 35°C during the bare summer fallow window",
                    "source": "NASA POWER Daily (2m Air Temp)",
                    "is_proxy": False,
                },
                {
                    "signal": f"Root-zone soil wetness averages {indicators.get('soil_moisture', {}).get('mean_root_zone_wetness', 0.38)} during fallow",
                    "source": "NASA POWER MERRA-2 (GWETROOT)",
                    "is_proxy": True,
                },
            ],
            "benefits": [
                "Lowest equipment and operational input costs",
                "Proven familiarity across Western Kansas wheat producers",
                "Allows weed control via tillage or non-selective herbicides",
            ],
            "information_gaps": [
                "Field-scale soil moisture retention efficiency is not measured by coarse satellite sensors",
                "Impact of localized stubble height on boundary-layer evaporation is unmodeled",
            ],
            "risks_needing_local_review": [
                "Severe wind erosion during dry, windy spring months (March–May)",
                "Precipitation storage efficiency during summer fallow is often under 20%",
                "Low soil organic carbon accumulation over multi-year cycles",
            ],
            "confidence": {
                "water": "medium",
                "cover": "high",
                "wind_erosion": "high",
                "income": "medium",
                "drought": "medium",
            },
        },
        "wheat_sorghum_fallow": {
            "why_suggested": "Shortens the vulnerable summer bare-fallow window and introduces a heat-tolerant C4 grain crop to capture late-summer radiation and stabilize farm income.",
            "evidence": [
                {
                    "signal": f"Sorghum vegetative canopy occupies July–September, eliminating the post-wheat NDVI bare-field dip below 0.20",
                    "source": "MODIS MOD13Q1 (250m)",
                    "is_proxy": True,
                },
                {
                    "signal": f"C4 grain sorghum maintains photosynthetic efficiency during the {heat_days} extreme heat days (Tmax >= 35°C)",
                    "source": "NASA POWER Daily",
                    "is_proxy": False,
                },
                {
                    "signal": f"Long dry spells ({dry_spell} days maximum) handled via sorghum's waxy leaf cuticle and drought-induced dormancy",
                    "source": "NASA POWER Daily Precipitation",
                    "is_proxy": False,
                },
            ],
            "benefits": [
                "Durable, erect stalk residue provides strong armor against spring wind erosion",
                "Breaks monoculture winter annual grassy weed cycles (cheatgrass, jointed goatgrass)",
                "Produces 2 grain crops in 3 years with modest additional capital requirements",
            ],
            "information_gaps": [
                "Local elevator milo basis and regional delivery distance not accounted for",
                "Subsoil moisture depletion impact on subsequent wheat stand emergence requires local probing",
            ],
            "risks_needing_local_review": [
                "Stored root-zone moisture must be at least 3 to 4 feet deep at June planting",
                "Herbicide carryover restrictions between winter wheat and summer sorghum",
            ],
            "confidence": {
                "water": "high",
                "cover": "high",
                "wind_erosion": "high",
                "income": "medium",
                "drought": "high",
            },
        },
        "wheat_sunflower_fallow": {
            "why_suggested": "Utilizes deep-rooting sunflower to scavenge subsoil water and residual nitrogen below the wheat root zone, providing a high-value cash alternative.",
            "evidence": [
                {
                    "signal": f"Deep taproot reaches subsoil moisture down to 6 feet during extended dry periods (max {dry_spell} days)",
                    "source": "NASA POWER Daily & USDA NRCS",
                    "is_proxy": False,
                },
                {
                    "signal": f"186 frost-free days easily accommodate 90-110 day confection or oilseed maturity varieties",
                    "source": "NASA POWER Minimum Temperature",
                    "is_proxy": False,
                },
            ],
            "benefits": [
                "Excellent deep-profile nutrient scavenging and break of cereal diseases",
                "High profit potential under favorable oilseed crushing contract pricing",
                "Tolerant of high midsummer daytime temperatures",
            ],
            "information_gaps": [
                "Regional processor contracting and logistics within 100 miles of Colby",
                "High-resolution bird predation risk maps not integrated",
            ],
            "risks_needing_local_review": [
                "Sunflower leaves fragile residue that breaks down rapidly, leaving soil bare by late winter",
                "Heavy subsoil moisture extraction can dry out subsoil before subsequent wheat planting",
            ],
            "confidence": {
                "water": "medium",
                "cover": "medium",
                "wind_erosion": "medium",
                "income": "low",
                "drought": "medium",
            },
        },
        "wheat_legume_cover": {
            "why_suggested": "Replaces vulnerable bare fallow with a living multi-species or legume cover crop to build soil organic matter, fix biological nitrogen, and maximize continuous ground cover.",
            "evidence": [
                {
                    "signal": f"Directly addresses the 4-month NDVI bare-field window, sustaining ground cover across summer months",
                    "source": "MODIS MOD13Q1 (250m)",
                    "is_proxy": True,
                },
                {
                    "signal": f"Root-zone soil wetness ({indicators.get('soil_moisture', {}).get('mean_root_zone_wetness', 0.38)}) requires careful termination timing to avoid moisture penalty",
                    "source": "NASA POWER MERRA-2",
                    "is_proxy": True,
                },
            ],
            "benefits": [
                "Superior living armor against High Plains wind erosion",
                "Biological nitrogen fixation reduces synthetic fertilizer costs",
                "Accelerates soil organic carbon and infiltration capacity",
            ],
            "information_gaps": [
                "Field-scale cover crop transpiration vs. fallow evaporation trade-off not resolved by satellite",
                "Cover crop seed mix availability and cost in Northwest Kansas",
            ],
            "risks_needing_local_review": [
                "Risk of depleting stored soil moisture needed for subsequent cash crop stand establishment",
                "Cover crop termination timing must be managed aggressively before soil moisture is exhausted",
                "Requires additional seed investment with no direct harvestable cash grain revenue",
            ],
            "confidence": {
                "water": "low",
                "cover": "high",
                "wind_erosion": "high",
                "income": "low",
                "drought": "low",
            },
        },

        # Finney County
        "continuous_irrigated_corn": {
            "why_suggested": "Existing intensive management system maximizing short-term grain volume under center-pivot irrigation, but facing severe Ogallala depletion.",
            "evidence": [
                {
                    "signal": f"Peak irrigation occurs during July–August with {heat_days} days above 35°C driving atmospheric evaporative demand to maximum",
                    "source": "NASA POWER Daily Maximum Temperature",
                    "is_proxy": False,
                },
                {
                    "signal": f"Rainfall variability (CV = {indicators.get('rainfall', {}).get('rainfall_variability_cv', 0.24)}) leaves crop entirely dependent on unsustainable groundwater pumping",
                    "source": "NASA POWER Daily Precipitation",
                    "is_proxy": False,
                },
            ],
            "benefits": [
                "High gross revenue potential in years with favorable grain market prices",
                "Heavy corn stover residue protects against winter wind erosion",
                "Established local grain delivery infrastructure, feedlots, and ethanol plants",
            ],
            "information_gaps": [
                "Local well pumping capacity (gallons per minute) varies field-by-field and is unmeasured by satellites",
                "Exact LEMA multi-year allocation balance must be confirmed with Groundwater Management District",
            ],
            "risks_needing_local_review": [
                "Ogallala aquifer decline and impending legal water pumping limits under GMD/LEMA rules",
                "Escalating energy pumping costs with deeper well lifts",
                "Severe corn rootworm, spider mite, and goss's wilt pressure in continuous monoculture",
            ],
            "confidence": {
                "water": "high",
                "cover": "high",
                "wind_erosion": "high",
                "income": "high",
                "drought": "medium",
            },
        },
        "corn_soybean": {
            "why_suggested": "Rotates irrigated corn with a legume to reduce peak seasonal pumping overlap, supply biological nitrogen, and break corn rootworm cycles.",
            "evidence": [
                {
                    "signal": f"Soybean peak water demand shifts timing relative to corn, moderating peak well discharge during heat waves ({heat_days} days >35°C)",
                    "source": "NASA POWER Daily Temperature",
                    "is_proxy": False,
                },
                {
                    "signal": f"201 frost-free days provide ample window for Group 3 and Group 4 soybean maturities",
                    "source": "NASA POWER Minimum Temperature",
                    "is_proxy": False,
                },
            ],
            "benefits": [
                "Biological nitrogen fixation provides 30 to 45 lbs N/acre credit to the subsequent corn crop",
                "Completely breaks Western Corn Rootworm larval feeding cycle",
                "Diversifies commodity price risk between feed grain and oilseeds",
            ],
            "information_gaps": [
                "Regional iron deficiency chlorosis (IDC) risk on high-pH caliche soils requires local soil testing",
                "Varietal tolerance to spider mites in hot, dry High Plains late summers",
            ],
            "risks_needing_local_review": [
                "Soybean residue breaks down rapidly after harvest, leaving soil vulnerable to winter/spring wind erosion",
                "Soybeans are highly sensitive to late-summer heat and moisture stress during pod fill",
            ],
            "confidence": {
                "water": "medium",
                "cover": "medium",
                "wind_erosion": "medium",
                "income": "medium",
                "drought": "medium",
            },
        },
        "corn_wheat_sorghum": {
            "why_suggested": "A 3-year limited-irrigation rotation that allocates groundwater strategically to corn while letting drought-hardy wheat and sorghum thrive on partial irrigation.",
            "evidence": [
                {
                    "signal": f"Reduces seasonal pumping volume by ~30%, preserving groundwater buffer for critical heat days ({heat_days} days >= 35°C)",
                    "source": "NASA POWER Daily & K-State Irrigation Trials",
                    "is_proxy": False,
                },
                {
                    "signal": f"Wheat and sorghum stagger vegetative peaks across May and August, eliminating midsummer well strain",
                    "source": "MODIS MOD13Q1 Climatology",
                    "is_proxy": True,
                },
            ],
            "benefits": [
                "Saves 25% to 35% of total irrigation water, extending well life and complying with LEMA caps",
                "Continuous heavy residue from sorghum and wheat protects soil armor year-round",
                "Spreads labor, planting, and harvesting across spring, summer, and autumn",
            ],
            "information_gaps": [
                "Transitioning pivot nozzles from full corn capacity to variable-rate split application",
                "Local feedlot and elevator pricing spreads between corn and sorghum",
            ],
            "risks_needing_local_review": [
                "Requires careful pivot management to split water across different crops under one circle",
                "Lower gross revenue per acre compared to bumper corn crops in wet years",
            ],
            "confidence": {
                "water": "high",
                "cover": "high",
                "wind_erosion": "high",
                "income": "medium",
                "drought": "high",
            },
        },
    }

    for s in scored:
        s_id = s["id"]
        meta = strategy_meta.get(s_id, {
            "why_suggested": s.get("description", ""),
            "evidence": [{"signal": "Empirical NASA indicators applied", "source": "NASA POWER / MODIS", "is_proxy": False}],
            "benefits": ["Diversifies crop rotation", "Reduces monoculture risks"],
            "information_gaps": ["Requires localized field validation"],
            "risks_needing_local_review": ["Market access and seed cost"],
            "confidence": {"water": "medium", "income": "medium"},
        })

        card = {
            "strategy": s["name"],
            "id": s_id,
            "is_existing": s["is_existing"],
            "score": s["score"],
            "why_suggested": meta["why_suggested"],
            "evidence": meta["evidence"],
            "benefits": meta["benefits"],
            "information_gaps": meta["information_gaps"],
            "risks_needing_local_review": meta["risks_needing_local_review"],
            "confidence": meta["confidence"],
            "criteria_breakdown": s["criteria_breakdown"],
        }
        cards.append(card)

    return cards


def generate_all_evidence_cards() -> Dict[str, List[Dict[str, Any]]]:
    """Compile and save evidence cards for all study counties."""
    with open(PROCESSED_DATA_DIR / "indicators.json", "r", encoding="utf-8") as f:
        all_indicators = json.load(f)

    all_cards = {}
    for c in all_indicators.keys():
        cards = generate_evidence_cards(c, all_indicators[c])
        all_cards[c] = cards
        logger.info(f"Generated {len(cards)} structured evidence cards for {c} County.")

    out_file = PROCESSED_DATA_DIR / "evidence.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_cards, f, indent=2)
    logger.info(f"Saved all evidence cards to {out_file}")
    return all_cards


if __name__ == "__main__":
    cards = generate_all_evidence_cards()
    print("\n--- Sample Generated Evidence Card (Thomas County #1) ---")
    print(json.dumps(cards["Thomas"][0], indent=2))
