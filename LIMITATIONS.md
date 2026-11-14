# Scientific & Technical Limitations (LIMITATIONS.md)
## Project: Field Shift — Western Kansas

Transparency is a fundamental tenet of the Field Shift project. To ensure responsible decision support and prevent misinterpretation by producers or agronomists, the following limitations and scientific boundaries are openly stated:

---

### 1. Spatial Resolution Limitations
- **NASA POWER Grid Cell Scale (~50 km / 0.5°)**:
  NASA POWER provides regional meteorological estimates derived from Goddard Earth Observing System (GEOS) atmospheric assimilation models. While excellent for regional climatology and 10-year trend detection, it **cannot resolve intra-field microclimates**, rain-shadows, localized thunderstorm cells, or elevation nuances within a single county.
- **MODIS 250m Pixel Footprint**:
  A 250-meter pixel encompasses approximately 15 acres. While suitable for analyzing large quarter-section center pivots (125–130 acres) and dryland half-sections in Western Kansas, it blends edge effects, shelterbelts, access roads, and field borders into composite spectral signatures.
- **SMAP & GRACE-FO Regional Coarseness**:
  NASA SMAP (9–36 km) and GRACE-FO (regional terrestrial water storage) are designed for macro-hydrological monitoring. They cannot measure field-level soil moisture differences between tilled and no-till strips.

---

### 2. Temporal & Agronomic Timing Caveats
- **Stored Soil Moisture at Planting**:
  Real-world rotation success in Western Kansas dryland systems depends decisively on the actual depth of moist soil (measured via soil probe to 3–4 feet) during the specific planting week. Satellite indicators reflect historical climatology and regional averages, not site-specific soil probe readings.
- **Cover Crop Moisture Penalty**:
  While cover crops provide critical armor against spring wind erosion and build organic carbon, in dry years they can transpire valuable subsoil moisture needed for the following cash crop. The decision to plant and when to terminate cover crops requires strict local monitoring.

---

### 3. Proxy Fallback Disclosures
- **Root-Zone Soil Wetness Proxy (`GWETROOT`)**:
  Used as a model-based proxy for SMAP root-zone soil moisture. Derived from MERRA-2 land surface models within NASA POWER. Labeled explicitly with `is_proxy = True`.
- **MODIS NDVI AppEEARS Reference Proxy**:
  When external ORNL DAAC web services experience network timeouts, the system falls back to calibrated 16-day AppEEARS reference climatology modulated by observed NASA POWER daily weather anomalies. Labeled explicitly with `is_proxy = True`.

---

### 4. Non-Topographic Wind Erosion
- **Slope vs. Soil Armor**:
  Topographic slope (from SRTM DEM) is nearly flat across the High Plains tablelands of Thomas and Finney counties (< 2% slope). In this geography, soil erosion is driven by **wind velocity, surface residue cover, and soil aggregate stability**, not water runoff slope. Therefore, wind erosion risk is modeled from vegetative cover duration and residue persistence rather than topographic terrain gradients.

---

### 5. Economic & Operational Scope
- **Starter Agronomic Ratings**:
  All base ratings in `ratings/strategies.json` represent starter benchmarks derived from published K-State Extension literature. They are marked with `"confidence": "estimate, needs local review"` in the application to emphasize that local fertilizer prices, custom harvesting rates, and individual farm equipment fleets will alter real-world farm margins.
