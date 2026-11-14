# Technology Stack Specification
## Project: Field Shift — Western Kansas

---

### 1. Core Runtime & Language
- **Language**: Python 3.11+ (Compatible through Python 3.14)
- **Execution Model**: Modular Python pipelines for ingestion and compute; lightweight reactive Streamlit runtime for the farmer UI.
- **Environment Management**: Virtual environment (`venv` or `uv`) with pinned reproducible requirements.

---

### 2. Dependency Breakdown by Subsystem

#### 2.1 Web Application & User Interface
| Library | Recommended Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- |
| **Streamlit** | `^1.40.0` | Primary application framework | Native support for reactive data visualization, rapid prototyping, local execution, and low friction for offline demos. |
| **Streamlit-Folium** | `^0.23.0` | Leaflet/Folium integration | Embeds interactive geospatial maps within Streamlit for anchor point and grid cell visualization. |

#### 2.2 Visualization & Charting
| Library | Recommended Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- |
| **Plotly** | `^5.24.0` | Interactive charts | Generates interactive, high-contrast, fully annotated time-series charts (NDVI curves, rainfall distributions, thermal anomalies) with hover tooltips and clean export capabilities. |
| **Folium** | `^0.18.0` | Geospatial mapping | Renders study area basemaps, county outlines, and spatial vulnerability layers. |

#### 2.3 Data Ingestion & Networking
| Library | Recommended Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- |
| **Requests** | `^2.32.0` | Synchronous REST client | Used for NASA POWER API, ORNL DAAC web services, and NRCS Soil Data Access with robust connection pooling and timeout management. |
| **Tenacity** | `^9.0.0` | Network retry & backoff | Handles transient API timeouts, exponential backoff, and rate limits gracefully. |

#### 2.4 Data Processing & Scientific Computation
| Library | Recommended Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- |
| **Pandas** | `^2.2.0` / `^3.0.0` | Dataframe manipulation | Tidy data transformations, rolling averages, monthly resampling, and tabular indicators. |
| **NumPy** | `^2.0.0` | Vectorized numerical compute | Matrix scoring operations ($S_j = \sum w_i r_{ij} a_{ij}$), climatology calculations, and anomaly scaling. |
| **SciPy** | `^1.14.0` | Statistical indicators | Percentile distributions, standard deviations of rainfall, and trend regressions. |

#### 2.5 Extended Geospatial & Earth Observation (P1 & P2 Expansion)
| Library | Recommended Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- |
| **Earthaccess** | `^0.11.0` | NASA Earthdata access | Streamlined search and authenticated download of SMAP and GPM IMERG HDF5/NetCDF assets. |
| **Xarray** | `^2024.09.0` | Multidimensional arrays | Grid-cell manipulation and temporal slicing of Gridded Earth Observation products. |
| **Rasterio** | `^1.4.0` | GeoTIFF raster processing | Digital elevation (SRTM) and high-resolution land surface temperature processing. |

---

### 3. File Storage & Serialization Formats
- **Raw Cache (`data/raw/`)**: Plain JSON and CSV raw payloads to inspect API responses and preserve provenance.
- **Tidy Lake (`data/processed/`)**:
  - `tidy_monthly.csv`: Human-readable, portable comma-separated tidy format for monthly aggregated metrics.
  - `indicators.json`: Nested key-value dictionary containing derived indicators (frost dates, heat-stress counts, climatological NDVI curves).
  - `ratings/strategies.json`: Human-auditable JSON schema storing base ratings, source citations, and confidence tiers.

---

### 4. Quality Assurance & Testing
- **Test Framework**: `pytest ^8.0.0`
- **Validation Scope**:
  - Unit tests for indicator math ($T_{\max} \ge 35^\circ\text{C}$ counting, frost window detection, dry spell calculation).
  - Scoring engine invariance tests (ensuring weights normalize to 1.0 and adjustment factors stay strictly in the $[0.70, 1.10]$ envelope).
  - Schema validation ensuring no NaN values or missing `source` / `is_proxy` flags in processed tidy outputs.
