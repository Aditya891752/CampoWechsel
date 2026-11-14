# Project Memory & Knowledge Context (memory.md)
## Project: Field Shift — Western Kansas

---

### 1. Problem History & Agro-Ecological Context
Western Kansas lies within the semi-arid High Plains of North America, characterized by:
- **Low & Variable Annual Precipitation**: Typically 16 to 20 inches (400–500 mm) per year, with high inter-annual variability and frequent multi-year drought cycles.
- **High Atmospheric Evaporative Demand (PET)**: Potential evapotranspiration averages 55 to 65 inches annually, meaning atmospheric demand far exceeds rainfall during the peak summer growing season.
- **Critical Water Resources**: The region depends heavily on the High Plains (Ogallala) Aquifer, which is being depleted rapidly because withdrawal rates for center-pivot irrigation drastically outpace natural recharge (< 0.5 inches/year).

---

### 2. The Two Focus Counties & Agronomic Personas

#### 2.1 Northwest Kansas: Thomas County (Colby, KS)
- **Anchor Point**: `39.39° N, 101.05° W`
- **FIPS Code**: `20193`
- **Dominant Production System**: Dryland (rainfed) winter wheat cropping.
- **Baseline Rotation**: **Wheat–Fallow (1 crop every 2 years)**
  - *The Dilemma*: After wheat harvest in July, fields are left fallow for approximately 14 months until planting the next winter wheat crop in September of the following year.
  - *The Failure Mode*: Precipitation storage efficiency during this long fallow is notoriously low (only 15% to 25% of rainfall is conserved; the rest evaporates). More dangerously, the soil remains completely bare or sparsely stubbled during the windy spring months (March–May), creating high wind erosion risks reminiscent of the Dust Bowl era.
- **Alternative Rotations Being Evaluated**:
  1. *Wheat–Sorghum–Fallow (2 crops in 3 years)*: Introduces grain sorghum (milo), a heat- and drought-tolerant C4 crop that sipped moisture and provides heavy residue to shield against spring wind erosion.
  2. *Wheat–Sunflower–Fallow*: Sunflower utilizes deep taproots to scavenge subsoil water, providing high cash value and breaking pest cycles, though residue is lighter.
  3. *Wheat with Legume Cover Crop in Fallow*: Replaces bare fallow with a multi-species or legume cover crop to fix atmospheric nitrogen and shield soil, though soil moisture drawdown must be carefully monitored.

#### 2.2 Southwest Kansas: Finney County (Garden City, KS)
- **Anchor Point**: `37.97° N, 100.87° W`
- **FIPS Code**: `20055`
- **Dominant Production System**: Center-pivot irrigated agriculture.
- **Baseline Rotation**: **Continuous Irrigated Corn**
  - *The Dilemma*: Corn is a high-water, high-input crop requiring 20 to 26 inches of seasonal water. With declining aquifer saturated thickness, wells are pumping decreased gallons-per-minute (GPM), and state-mandated Local Enhanced Management Areas (LEMAs) have imposed multi-year pumping caps.
  - *The Failure Mode*: Pumping costs are rising with deeper lifts, and continuous corn builds up severe disease and insect pressure (e.g., corn rootworm, spider mites), increasing chemical input costs.
- **Alternative Rotations Being Evaluated**:
  1. *Corn–Soybean*: Rotates a legume into the sequence to fix nitrogen, break rootworm cycles, and reduce peak summer irrigation pumping windows.
  2. *Corn–Wheat–Sorghum (3 crops in 3 years / partial irrigation)*: Spreads irrigation demand across different seasonal timing windows, drastically cutting total groundwater extraction while maintaining steady crop revenue.

---

### 3. NASA Earth Observations & Local Context Datasets

| Dataset | Provider | Spatial / Temporal Resolution | Project Role | Access URL / Mechanism | Verified Fallback |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NASA POWER** | NASA Langley | 0.5° × 0.5° / Daily | Precipitation, 2m temps ($T_{\max}, T_{\min}$), humidity, solar radiation, soil wetness | `https://power.larc.nasa.gov/api/temporal/daily/point` (REST, no auth) | None needed (reliable endpoint) |
| **MODIS NDVI (MOD13Q1)** | NASA LP DAAC / ORNL DAAC | 250m / 16-day | Vegetation greenness dynamics, bare-field window identification | `https://modis.ornl.gov/rst/api/v1/` (REST subset service) | Pre-cached AppEEARS point time-series |
| **NASA SMAP L3** | NASA JPL / NSIDC | 9km–36km / Daily–3-day | Root-zone and surface soil moisture anomaly tracking | NASA Earthdata via `earthaccess` | NASA POWER root-zone wetness (`GWETROOT`) labeled as model proxy |
| **GPM IMERG** | NASA GSFC | 0.1° × 0.1° / Daily–Monthly | High-resolution precipitation & extreme storm event tracking | NASA Earthdata via `earthaccess` | NASA POWER precipitation labeled as proxy |
| **SRTM DEM** | NASA JPL | 30m / Static | Terrain slope & topography (context for wind vs. slope erosion) | OpenTopography / public elevation REST | Regional elevation averages from USGS |
| **USDA CropScape (CDL)** | USDA NASS | 30m / Annual | Ground truth historical crop rotations (5–10 year sequence) | USDA CropScape REST API | Hardcoded county historical acreage baselines (K-State) |
| **USDA NRCS SSURGO** | USDA NRCS | Polygon / Static | Soil texture, available water capacity (AWC), wind erodibility group | NRCS Soil Data Access REST | Typical county soil profiles (e.g., Keith silt loam) |
| **USGS NWIS** | USGS | Point / Periodic | Ogallala Aquifer groundwater monitoring well hydrographs | `https://waterservices.usgs.gov/` | Published KGS (Kansas Geological Survey) hydrographs |

---

### 4. Agronomic Starter Ratings Matrix (ratings/strategies.json)

Scores from 1 (poor) to 5 (optimal) established from K-State Extension agronomic benchmarks:

#### Thomas County (Dryland)
| Strategy | Water | Cover | Org Matter | Nitrogen | Wind Erosion | Pest Break | Income | Drought |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Wheat–Fallow (Existing)** | 2 | 1 | 2 | 1 | 1 | 2 | 3 | 2 |
| **Wheat–Sorghum–Fallow** | 3 | 3 | 3 | 1 | 3 | 4 | 4 | 3 |
| **Wheat–Sunflower–Fallow** | 3 | 3 | 3 | 1 | 3 | 4 | 3 | 3 |
| **Wheat w/ Legume Cover** | 2 | 5 | 4 | 4 | 4 | 3 | 2 | 2 |

#### Finney County (Irrigated)
| Strategy | Water | Cover | Org Matter | Nitrogen | Wind Erosion | Pest Break | Income | Drought |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Continuous Irrigated Corn (Existing)** | 1 | 3 | 3 | 1 | 3 | 1 | 4 | 2 |
| **Corn–Soybean** | 2 | 3 | 3 | 3 | 3 | 3 | 4 | 2 |
| **Corn–Wheat–Sorghum** | 4 | 4 | 4 | 1 | 4 | 5 | 3 | 4 |

---

### 5. Architectural & Design Decisions Log
1. **Decision**: Keep application runtime 100% offline-ready by separating data fetching into `pipeline/` and consuming preprocessed files in `data/processed/`.
   - *Rationale*: Guarantees zero failures during live demonstration or judging caused by external API throttling or lack of conference Wi-Fi.
2. **Decision**: Explicitly separate NASA Earth Observation data from non-NASA data in the user interface and data tables.
   - *Rationale*: Core to the Space Apps Challenge requirements to showcase NASA EO value while acknowledging local ground-truth sources.
3. **Decision**: Enforce high-contrast, rugged, sunlight-readable UI aesthetics free of tech-startup decorative cliches (no gradients, no glassmorphism, no emojis in headings, no low-contrast grays).
   - *Rationale*: The tool is built for farmers in tractor cabs and extension agents in rural offices.
