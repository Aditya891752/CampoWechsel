# Scientific Methodology and Multi-Criteria Scoring Framework
### Field Shift: Western Kansas — NASA International Space Apps Challenge

This document provides the mathematical framework, data harmonization procedures, and decision-tree logic governing the Field Shift application.

---

## 1. Decision Analysis Formula

Field Shift calculates an empirical rotation score for each candidate cropping sequence:

$$S_j = \sum_{i=1}^{8} w_i \cdot r_{ij} \cdot a_{ij}$$

Where:
* **$j$**: Candidate crop-rotation strategy index.
* **$i$**: Evaluation criterion index ($i \in \{1, \dots, 8\}$).
* **$w_i$**: Normalized user priority weight ($\sum_{i=1}^{8} w_i = 1.0$), dynamically modulated by three farmer-facing sliders: *Save Water*, *Protect Soil*, and *Earn Income*.
* **$r_{ij}$**: Baseline agronomic suitability rating ($1.0$ to $5.0$) derived from long-term Kansas State University Research & Extension agronomic field trials.
* **$a_{ij}$**: Empirical satellite adjustment factor ($0.70 \le a_{ij} \le 1.10$) computed from 10-year NASA Earth Observation telemetry.

---

## 2. Dynamic Satellite Adjustment Factor Derivations

### Bare-Field Window Adjustment ($a_{\text{bare}}$)
* Evaluated against Criterion 2 (*Residue Cover & Erosion Resistance*).
* Let $B$ be the number of consecutive months where mean parcel NDVI falls below the selected bare-field threshold (default: $0.20$):
  $$a_{\text{bare}} = \begin{cases} 
  1.10 & \text{if } B \le 1 \text{ (Continuous Living Cover / Armor)} \\ 
  1.00 & \text{if } B = 2 \\ 
  0.85 & \text{if } B = 3 \\ 
  0.70 & \text{if } B \ge 4 \text{ (Severe Extended Fallow Exposure)} 
  \end{cases}$$

### Extreme Heat Stress Adjustment ($a_{\text{heat}}$)
* Evaluated against Criterion 1 (*Crop Water Productivity*) and Criterion 8 (*Climate Resilience*).
* Based on annual frequency of days with maximum air temperature $T_{\max} \ge 35^\circ\text{C}$:
  * For heat-sensitive crops (e.g., Continuous Corn): penalized down to $0.75$ when heat days exceed 35 days/year.
  * For heat-tolerant C4 crops (e.g., Grain Sorghum / Milo): rewarded up to $1.10$ due to superior water-use efficiency under thermal stress.

### Drought and Moisture Variability Adjustment ($a_{\text{moisture}}$)
* Evaluated using SMAP / MERRA-2 standardized root-zone soil wetness anomalies and 10-year coefficient of variation ($CV$) in growing-season precipitation:
  * High rainfall variability ($CV > 0.20$) penalizes single-crop monocultures and rewards diversified, split-season rotations.

---

## 3. Data Ingestion and Quality Controls

1. **Daily to Monthly Tidy Resampling**:
   * Raw NASA POWER daily meteorological observations (3,653 daily records per county) are resampled into standardized monthly means, totals, and extreme counts.
2. **Provenance and Quality Attribution**:
   * All processed data rows in `tidy_monthly.csv` carry explicit metadata columns:
     * `source`: Data origin identifier (e.g., `NASA_POWER`, `MODIS_MOD13Q1_AppEEARS_Proxy`).
     * `is_proxy`: Boolean flag indicating whether the measurement is an exact physical satellite query or a calibrated climatological proxy.
3. **Graceful Offline Fallbacks**:
   * Remote API requests implement exponential backoff with calibrated local offline fallbacks, guaranteeing 100% offline uptime for producers in rural areas with poor connectivity.
