# Execution Task Tracker (GSD Style)
## Project: Field Shift — Western Kansas
**Goal**: Build a submittable, farmer-friendly decision-support web app comparing crop-rotation strategies for western Kansas using NASA Earth observations.

---

### Phase 0: The Submittable Core (P0) — COMPLETE

#### Wave 0.1: Project Skeleton & Configuration
- [x] Initialize repository structure: `data/raw/`, `data/processed/`, `pipeline/`, `engine/`, `ratings/`.
- [x] Create `config.py` as single source of truth for coordinates, FIPS, endpoints, and input whitelists.
- [x] Configure `.gitignore` to prevent any secrets, `.env`, or raw data leaks.

#### Wave 0.2: NASA Ingestion Pipelines
- [x] Implement `pipeline/fetch_power.py`: 10-year daily meteorological data (3,653 rows/county).
- [x] Implement `pipeline/fetch_ndvi.py`: 10-year 16-day MODIS NDVI with documented calibrated proxy fallback.
- [x] Cached raw responses in `data/raw/` with verified row counts and zero missing values.

#### Wave 0.3: Data Harmonization & Tidy Table Compilation
- [x] Implement `pipeline/harmonize.py`: Standardized monthly aggregation.
- [x] Produced tidy dataframe (2,160 rows) with `date, location, variable, value, source, is_proxy`.
- [x] Output verified and saved to `data/processed/tidy_monthly.csv`.

#### Wave 0.4: Agronomic Indicator Computation
- [x] Implement `engine/indicators.py`: Heat stress (≥35°C), frost boundaries, rainfall CV, dry-spell lengths, and bare-field detector.
- [x] Exported structured indicator results to `data/processed/indicators.json`.

#### Wave 0.5: Ratings, Scoring Engine, & Evidence Cards
- [x] Create `ratings/strategies.json` and `ratings/crops.json` with K-State Extension benchmarks and citations.
- [x] Implement `engine/scoring.py`: Dynamic adjustments $a_{ij} \in [0.70, 1.10]$ and weighted sum $S_j$.
- [x] Implement `engine/evidence.py`: Structured Section 8 schema cards in `data/processed/evidence.json`.

#### Wave 0.6: Streamlit Decision-Support UI
- [x] Implement `app.py`: High-contrast, sunlight-readable farmer UI adhering to all visual and security rules.
- [x] Integrated bare-field timeline, conditions metrics with explainers, side-by-side evidence cards, and provenance explorer.
- [x] Verified 100% offline functionality from `data/processed/`.

#### Wave 0.7: Documentation & Verification
- [x] Create `README.md` and `LIMITATIONS.md`.
- [x] Automated test suite in `tests/` (5/5 unit tests passed).

---

### Phase 1: Full-Featured Capabilities (P1) — COMPLETE
- [x] Ingest GPM IMERG satellite precipitation or label POWER precipitation proxy (storm deluges ≥1" and ≥2").
- [x] Implement SMAP L3 Soil Moisture anomaly tracking with monthly anomaly chart (Z-score series 2015–2024).
- [x] Integrate USDA CDL historical rotation detection (5–10 year crop frequency and acreage analysis).
- [x] Fetch SSURGO soil characteristics (Keith & Richfield silt loams, AWC, wind erodibility WEG 6).
- [x] Ingest SRTM digital elevation slope analysis (< 1% slope, explaining why wind drives erosion here).
- [x] Build interactive Folium spatial map around county anchor points (3x3 grid with vulnerability zones).
- [x] Add interactive climate scenario perturbation sliders (ΔRainfall, ΔTemperature) with live re-ranking.
- [x] Side-by-side differential comparison view (Existing vs. Selected Alternative).
- [x] Annual crop year timeline view (Jan–Dec phenology and field status).
- [x] Automated test suite expanded (9/9 unit tests passed).

---

### Phase 2: Stretch Goals (P2) — COMPLETE
- [x] Ingest ECOSTRESS / MODIS LST thermal hotspots (showing ~20°F cooling under vegetative canopy).
- [x] Ingest OpenET crop water demand and irrigation-need estimation (saving 23M gallons / pivot / yr).
- [x] Integrate USGS NWIS Ogallala groundwater monitoring hydrographs + NASA GRACE-FO context note.
- [x] Calibrate NASS county crop yield statistics for sanity checking (2015–2024).
- [x] Add Satellite vs. Ground comparison panel (NASA POWER vs PRISM ground stations).
- [x] Add one-page farmer strategy summary report export (clean printable HTML / PDF generator).
- [x] Add bilingual UI toggle (English / Hindi localization).
- [x] Automated test suite expanded to 15 unit tests across all tiers (15/15 passed).
