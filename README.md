# CampoWechsel (Field Shift: Western Kansas)
### NASA Space Apps Challenge 2026 — *"Field Shift: Adapting Farms with NASA Data"*
**Team**: Galactic Debuggers • **Lead**: Aditya Singh Chauhan (B.Tech Biotechnology, Galgotias University)

**CampoWechsel** is an evidence-based decision-support web application that empowers agricultural producers and county extension agents in Western Kansas to evaluate, compare, and adapt crop-rotation strategies using 10 years of NASA Earth Observation (EO) data alongside validated Kansas State University Extension agronomic benchmarks.

---

## 1. Quickstart & Execution

### Option A: Universally Accessible Interactive Web Demo (Zero Installation)
Experience the full decision-support engine, climate stress-testing, 10-year NDVI bare-field curves, and Gemini AI dossiers **instantly in any web browser** (desktop, laptop, tablet, or phone) without installing Python, Streamlit, or external dependencies:

- **Live GitHub Pages Demo**: [https://aditya891752.github.io/CampoWechsel/](https://aditya891752.github.io/CampoWechsel/)
- **Direct Local Demo**: Double-click [`demo.html`](demo.html) in your browser.
- **7-Slide Pitch Presentation Deck**: Open [`campowechsel_presentation.html`](campowechsel_presentation.html) or [`docs/slides.html`](docs/slides.html).
- **Accessibility Highlights**:
  - **WCAG 2.1 AA/AAA Compliant**: Semantic HTML5, high-contrast ratios (>7:1), visible focus rings, and screen-reader `aria-live` announcements.
  - **Display Modes**: High-Contrast (AAA Black/Gold) and High-Sunlight Field Cab mode for bright tractor cabs.
  - **Multilingual**: Instant English & Español toggle for High Plains agricultural managers and workers.
  - **Text-to-Speech (TTS)**: Built-in voice synthesizer reads agronomic summaries aloud for audio accessibility.
  - **Interactive Visualizations**: Dynamic SVG charts with accessible data tables for all users.

### Option B: Full Python & Streamlit Application (Local Developer Suite)

The application is built offline-first: all remote satellite datasets are preprocessed and cached in `fieldshift/data/processed/`, allowing the application to run immediately with zero external network dependencies.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
streamlit run fieldshift/app.py
# Or use the universal launcher:
python run.py
```

The Streamlit app launches at `http://localhost:8501`.

---

## 2. Core Architecture & Philosophy

```text
fieldshift/
├── app.py                     # Interactive Streamlit application & Farmer UI
├── config.py                  # Single source of truth: Endpoints, coordinates, FIPS
├── data/
│   ├── raw/                   # Immutable raw payload cache (POWER JSON, NDVI CSV)
│   └── processed/             # Offline consumable tidy datasets & evidence cards
├── pipeline/                  # Modular ETL ingestion modules
│   ├── fetch_power.py         # 10-year NASA POWER daily meteorological client
│   ├── fetch_ndvi.py          # MODIS MOD13Q1 250m 16-day NDVI ingest & proxy fallback
│   ├── harmonize.py           # Standardized monthly tidy resampler
│   └── plot_thomas.py         # High-contrast 10-year climatology generator
├── engine/                    # Deterministic scientific & decision engines
│   ├── indicators.py          # Heat stress (≥35°C), frost dates, rainfall CV, bare field
│   ├── scoring.py             # Multi-criteria scoring formula: S_j = Σ (w_i * r_ij * a_ij)
│   ├── scenarios.py           # Climate perturbation engine (ΔRainfall, ΔTemperature)
│   ├── evidence.py            # Structured JSON evidence card synthesis
│   └── gemini_advisor.py      # Gemini AI spatial agronomist (offline dossiers & live queries)
└── ratings/                   # Peer-reviewed agronomic starter matrices
    ├── strategies.json        # 1–5 criteria ratings with K-State Extension citations
    └── crops.json             # Crop water demands, rooting depths, and phenology
```

---

## 3. Data Sources & Provenance

### NASA Earth Observations (Primary Signal)
- **NASA POWER Daily Agroclimatology (2015–2024)**: Temperature at 2m (mean, min, max), precipitation, relative humidity, solar radiation, and root-zone soil wetness.
- **MODIS NDVI (MOD13Q1, 250m 16-day composite)**: Vegetative greenness dynamics, crop canopy peaks, and summer fallow bare-field detection.
- **NASA MERRA-2 (GWETROOT)**: Model-based proxy for root-zone soil moisture context.

### Non-NASA Ground Truth & Agronomic Benchmarks
- **Kansas State University Research & Extension**: Starter 1–5 agronomic suitability matrices, crop budgets, and disease guides (Bulletins MF-2573, SRL-138, C-560, MF-573, MF-3244).
- **USDA NRCS**: Wind erosion tech notes and residue management guidelines.

---

## 4. Multi-Criteria Scoring Formula

$$S_j = \sum_{i=1}^{8} w_i \cdot r_{ij} \cdot a_{ij}$$

- $w_i$: Normalized farmer priority weights ($\sum w_i = 1.0$), modulated by 3 farmer sliders (*Save Water*, *Protect Soil*, *Earn Income*).
- $r_{ij}$: Baseline agronomic score ($1$ to $5$) from K-State Extension published trials.
- $a_{ij}$: Empirical adjustment factor ($0.70$ to $1.10$) computed dynamically from NASA satellite observations:
  - Prolonged bare-field windows ($\text{NDVI} < 0.20$) penalize summer fallow and reward cover crops.
  - Extreme heat-stress days ($T_{\max} \ge 35^\circ\text{C}$) penalize water-demanding corn and reward resilient sorghum.
  - High rainfall variability ($CV$) and dry spells reward crop diversification.

---

## 5. Testing & Verification

Run the automated test suite with:
```bash
pytest tests/
```
All unit tests verify weight normalization, indicator math, and scoring boundary invariance.
