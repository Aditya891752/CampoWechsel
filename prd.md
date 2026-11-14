# Product Requirements Document (PRD)
## Project Name: Field Shift — Western Kansas
**NASA International Space Apps Challenge**  
**Challenge Track**: *Field Shift: Adapting Farms with NASA Data*  
**Target Completion**: P0 Core by Sunday, November 15, 2026

---

### 1. Executive Summary & Problem Statement
Western Kansas sits at the intersection of extreme climate vulnerability and vital agricultural production. Farmers face:
1. **Ogallala Aquifer Depletion & Pumping Restrictions**: In Southwest Kansas (e.g., Finney County), intensive irrigation for corn is draining groundwater faster than natural recharge, triggering strict Local Enhanced Management Area (LEMA) pumping quotas.
2. **Wind Erosion & Moisture Loss in Summer Fallow**: In Northwest Kansas (e.g., Thomas County), traditional wheat-fallow leaves soil bare for up to 14 months, exposing topsoil to catastrophic wind erosion and evaporative loss.

**Field Shift** is a farmer-friendly, evidence-based decision-support web application that leverages NASA Earth Observation (EO) data alongside validated local agronomic context (USDA, Kansas State University Extension). The system detects bare and stressed field periods and provides multi-criteria comparisons of crop-rotation strategies, grounding recommendations in empirical satellite observations while remaining strictly transparent about scientific uncertainties.

---

### 2. Core Philosophy & Governance Rules
1. **Farmer-Centric Augmentation, Not Replacement**: The app explicitly supports farmer and local-expert judgment; it never dictates or acts as an automated black-box advisor.
2. **Absolute Data Integrity**: Zero fabricated data. If an external API is down or throttled, the application uses documented, labeled fallbacks (e.g., NASA POWER root-zone wetness proxy for SMAP) and visibly tags them as proxies in both the UI and documentation.
3. **Offline-First Architecture**: All remote datasets are downloaded to `data/raw/` and harmonized into tidy tables in `data/processed/`. The frontend Streamlit application reads strictly from `data/processed/` to guarantee 100% offline functionality during demos and judging.
4. **Transparent Scoring**: Every score traces back to explicit parameter matrices in `ratings/strategies.json` and documented adjustment equations in `engine/scoring.py`.

---

### 3. User Personas & Study Counties

| Persona | Location & County | Anchor Coordinates & FIPS | Current System | Primary Tensions & Priorities |
| :--- | :--- | :--- | :--- | :--- |
| **Dryland Wheat Grower** | Colby, Thomas County | 39.39° N, 101.05° W<br>`FIPS: 20193` | Wheat–Fallow (14-month fallow) | • Prevent wind erosion during fallow<br>• Maximize stored soil moisture efficiency<br>• Income stability under severe drought |
| **Irrigated Corn Grower** | Garden City, Finney County | 37.97° N, 100.87° W<br>`FIPS: 20055` | Continuous Irrigated Corn | • Ogallala aquifer drawdown & pumping limits<br>• High energy and water input costs<br>• Preserving profit margins and soil organic matter |

---

### 4. Functional Requirements

#### 4.1 Data Ingestion & Harmonization
- **NASA POWER (Daily Point)**: 2015–2024 daily records for precipitation, 2m air temperature (T2M, T2M_MAX, T2M_MIN), relative humidity (RH2M), solar radiation (ALLSKY_SFC_SW_DWN), and root-zone soil wetness (GWETROOT).
- **MODIS NDVI (MOD13Q1 / 250m 16-day)**: 16-day composite vegetative index tracking greenness dynamics, peak vegetative windows, and fallow duration.
- **Tidy Harmonization**: Standard monthly aggregation format across all datasets:
  `date, location, variable, value, source, is_proxy`

#### 4.2 Agronomic Indicators & Stress Engines
- **Heat-Stress Days**: Annual count of days where daily $T_{\max} \ge 35^\circ\text{C}$ (critical threshold for pollen sterility in corn and heat scorch in summer crops).
- **Frost-Risk Dates**: Last spring freeze ($T_{\min} \le 0^\circ\text{C}$) and first autumn freeze dates, defining the effective frost-free growing window.
- **Precipitation Metrics**: Monthly cumulative rainfall, standard deviation (rainfall variability), and dry-spell length (maximum consecutive days with precipitation $< 1.0\text{ mm}$).
- **Bare-Field Detection**: Monthly climatological analysis identifying persistent low-NDVI intervals ($\text{NDVI} < 0.20$ default, interactive slider $0.10 - 0.35$).
- **Soil Moisture Dynamics**: Root-zone moisture trends and dry anomalies relative to 10-year baselines.

#### 4.3 Strategy Scoring & Evaluation Framework
- **Eight Agronomic & Economic Criteria**:
  1. *Water Efficiency*
  2. *Soil Cover Duration*
  3. *Organic Matter Building*
  4. *Nitrogen Fixation & Efficiency*
  5. *Wind Erosion Protection*
  6. *Pest/Weed Cycle Break*
  7. *Net Income Reliability*
  8. *Drought Resilience*
- **Base Matrix**: 1 to 5 ratings per strategy based on K-State Extension agronomic benchmarks.
- **Data-Driven Dynamic Adjustments ($a_{ij}$)**: NASA climate indicators scale base ratings between $0.7$ and $1.1$ (e.g., severe summer drought anomalies adjust water-demanding rotations downward and resilience upward).
- **Weighted Ranking**:
  $$S_j = \sum_{i=1}^{8} w_i \cdot r_{ij} \cdot a_{ij}$$
  Weights $w_i$ are pre-configured by selected persona and fully customizable via farmer priority sliders (normalized to $\sum w_i = 1$).

#### 4.4 Structured Evidence Cards
Every rotation alternative produces a structured card detailing:
- Overall ranking and composite score ($S_j$).
- Plain-language explanation ("Why suggested").
- Concrete satellite evidence (e.g., *"NDVI stays below 0.20 for 4 consecutive months from June to September under wheat-fallow"*).
- Expected agronomic benefits.
- Known information gaps (e.g., *"SMAP resolution is coarse (9-36km); localized field-scale soil variations require in-situ testing"*).
- Risks requiring local agronomic review (e.g., *"Check subsoil moisture profile to 4 feet before planting summer sorghum"*).
- Data confidence ratings (`High`, `Medium`, `Low`).

---

### 5. Phased Roadmap (P0, P1, P2)

#### Phase 0: Submittable Core (Must-Have Baseline)
- [x] Fetch and cache NASA POWER daily data (2015–2024) for Thomas and Finney anchor points.
- [x] Fetch and cache MODIS NDVI for both anchor points over the same decade.
- [x] Process and store monthly tidy table with strict `source` and `is_proxy` fields.
- [x] Compute climate indicators: heat-stress days ($T_{\max} \ge 35^\circ\text{C}$), frost boundaries, dry-spell lengths, NDVI monthly climatology.
- [x] Implement bare-field detection with configurable NDVI threshold.
- [x] Implement dynamic multi-criteria scoring engine with persona weight presets.
- [x] Generate structured evidence cards for $\ge 3$ strategies per county (current baseline + 2+ alternatives).
- [x] Build core Streamlit user interface:
  - Header with persistent disclaimer banner.
  - Persona & County selector.
  - Farmer priority sliders.
  - Interactive NDVI timeline with shaded bare-field period.
  - Climate conditions visualizer (rainfall, heat, frost).
  - Side-by-side strategy comparison cards.
  - Plain-language glossary and Data Sources modal (NASA vs. Non-NASA separation).

#### Phase 1: Full-Featured Version
- [ ] GPM IMERG satellite precipitation integration (or clearly labeled POWER proxy fallback).
- [ ] SMAP L3 Soil Moisture anomaly engine.
- [ ] USDA CropScape CDL historical rotation detection (5–10 year crop frequency).
- [ ] USDA SSURGO soil characteristics (organic matter, available water capacity, wind erodibility index).
- [ ] SRTM digital elevation slope analysis and wind-erosion topography context.
- [ ] Spatial 2D Folium interactive map grid around anchor points.
- [ ] Interactive Climate Scenario Perturbation Sliders ($\Delta \text{Rainfall}: -30\% \text{ to } +20\%$, $\Delta \text{Temperature}: 0 \text{ to } +3^\circ\text{C}$) with live strategy re-ranking.

#### Phase 2: Stretch Capabilities
- [ ] ECOSTRESS thermal stress / LST anomalies.
- [ ] OpenET evapotranspiration demand calculations.
- [ ] USGS NWIS Ogallala monitoring well water level historical trends.
- [ ] One-page summary PDF export for field agronomist consultation.
- [ ] Bilingual localization toggle (English / Hindi).

---

### 6. Non-Functional Requirements
- **Performance**: Instant page load (< 1.5 seconds) powered exclusively by local parquet/csv processed cache.
- **Reliability**: Fault-tolerant data ingest with persistent retries, backoff, and documented proxy fallback pathways.
- **Usability**: High visual contrast, large readable typography, zero ambiguous jargon, mobile/tablet accessible for cab or field use.
