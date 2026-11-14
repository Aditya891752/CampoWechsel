"""
Central Configuration for Field Shift: Western Kansas.
Single source of truth for endpoints, coordinates, county metadata, and thresholds.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RATINGS_DIR = BASE_DIR / "ratings"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
RATINGS_DIR.mkdir(parents=True, exist_ok=True)

# Study Counties & Anchor Points (verified coordinates and FIPS)
COUNTIES = {
    "Thomas": {
        "name": "Thomas County",
        "seat": "Colby",
        "lat": 39.39,
        "lon": -101.05,
        "fips": "20193",
        "system": "Dryland wheat–fallow",
        "main_tension": "Long bare fallow, wind erosion, drought",
        "default_persona": "dryland_wheat",
        "elevation_m": 960,
    },
    "Finney": {
        "name": "Finney County",
        "seat": "Garden City",
        "lat": 37.97,
        "lon": -100.87,
        "fips": "20055",
        "system": "Irrigated corn",
        "main_tension": "Ogallala aquifer decline, pumping limits",
        "default_persona": "irrigated_corn",
        "elevation_m": 865,
    },
}

# Strict whitelist for security (prevents path injection)
ALLOWED_COUNTIES = set(COUNTIES.keys())

# Personas
PERSONAS = {
    "dryland_wheat": {
        "title": "Dryland Wheat Grower (Thomas County)",
        "county": "Thomas",
        "description": "Conserve stored soil moisture, minimize wind erosion during summer fallow, keep income stable with low equipment overhead.",
        "default_weights": {
            "water": 0.20,
            "cover": 0.15,
            "organic_matter": 0.10,
            "nitrogen": 0.05,
            "wind_erosion": 0.20,
            "pest_break": 0.10,
            "income": 0.10,
            "drought": 0.10,
        },
    },
    "irrigated_corn": {
        "title": "Irrigated Corn Grower (Finney County)",
        "county": "Finney",
        "description": "Reduce irrigation pumping volume under LEMA caps, protect margins against high energy/chemical costs, maintain soil organic matter.",
        "default_weights": {
            "water": 0.25,
            "cover": 0.10,
            "organic_matter": 0.15,
            "nitrogen": 0.10,
            "wind_erosion": 0.10,
            "pest_break": 0.10,
            "income": 0.10,
            "drought": 0.10,
        },
    },
}

# Date Range for Climatological Analysis (10 years)
START_YEAR = 2015
END_YEAR = 2024
START_DATE_STR = f"{START_YEAR}0101"
END_DATE_STR = f"{END_YEAR}1231"

# Remote API Endpoints
# 1. NASA POWER API (Daily Agroclimatology)
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_POWER_COMMUNITY = "AG"
NASA_POWER_PARAMETERS = [
    "T2M",            # Temperature at 2 Meters (°C)
    "T2M_MAX",        # Maximum Temperature at 2 Meters (°C)
    "T2M_MIN",        # Minimum Temperature at 2 Meters (°C)
    "PRECTOTCORR",    # Corrected Total Precipitation (mm/day)
    "RH2M",           # Relative Humidity at 2 Meters (%)
    "ALLSKY_SFC_SW_DWN", # All Sky Surface Shortwave Downward Irradiance (MJ/m^2/day)
    "GWETROOT",       # Root Zone Soil Wetness (0 to 1, proxy for SMAP)
]

# 2. ORNL DAAC MODIS Web Service (MOD13Q1: 250m 16-day NDVI)
ORNL_DAAC_BASE_URL = "https://modis.ornl.gov/rst/api/v1/"
MODIS_PRODUCT = "MOD13Q1"
MODIS_BAND = "250m_16_days_NDVI"
MODIS_SCALE_FACTOR = 0.0001
MODIS_VALID_MIN = -2000
MODIS_VALID_MAX = 10000

# Agronomic & Climate Thresholds
DEFAULT_BARE_FIELD_NDVI = 0.20
HEAT_STRESS_TEMP_C = 35.0
FROST_TEMP_C = 0.0
DRY_SPELL_RAIN_LIMIT_MM = 1.0

# 8 Core Evaluation Criteria
CRITERIA = [
    {"key": "water", "name": "Water Efficiency", "desc": "Reduced water use / efficient moisture preservation"},
    {"key": "cover", "name": "Soil Cover Duration", "desc": "Months soil remains protected by living roots or residue"},
    {"key": "organic_matter", "name": "Organic Matter Building", "desc": "Soil organic carbon enhancement over time"},
    {"key": "nitrogen", "name": "Nitrogen Efficiency", "desc": "Biological nitrogen fixation or reduced synthetic fertilizer reliance"},
    {"key": "wind_erosion", "name": "Wind Erosion Protection", "desc": "Armor against High Plains wind erosion during spring"},
    {"key": "pest_break", "name": "Pest & Weed Break", "desc": "Disrupts monoculture weed, insect, and fungal pathogen cycles"},
    {"key": "income", "name": "Income Reliability", "desc": "Stability of net returns under market and weather shocks"},
    {"key": "drought", "name": "Drought Resilience", "desc": "Yield buffer and survival during extreme precipitation deficits"},
]
