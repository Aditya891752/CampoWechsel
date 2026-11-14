# Agronomic and Technical Glossary
### Field Shift: Western Kansas — NASA International Space Apps Challenge

This glossary defines the empirical Earth Observation indicators, agronomic parameters, soil properties, and regional hydrological terms used throughout the Field Shift decision-support application.

---

## 1. NASA Earth Observation Telemetry

### Normalized Difference Vegetation Index (NDVI)
* **Sensor**: MODIS (Moderate Resolution Imaging Spectroradiometer) aboard Terra and Aqua satellites.
* **Product**: MOD13Q1 (250m spatial resolution, 16-day composite).
* **Physical Formula**:
  $$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
* **Application in Field Shift**: Measures photosynthetically active canopy density. Values above 0.40 represent vigorous crop growth (e.g., May wheat heading or July corn silking). Values below 0.20 indicate bare, unarmored soil.

### Bare-Field Window
* **Definition**: Consecutive monthly periods where mean parcel NDVI remains below 0.20.
* **Agronomic Significance**: In Western Kansas, bare fallow fields exposed to high temperatures (>= 35°C) experience severe topsoil desiccation and pulverization, leaving silt-loam particles vulnerable to detachment by 30 to 50 mph spring winds.

### Extreme Heat Days (Tmax >= 35°C)
* **Sensor/Model**: NASA POWER Agroclimatology (GMAO MERRA-2 assimilation).
* **Definition**: Annual count of days where maximum daily 2-meter air temperature equals or exceeds 35°C (95°F).
* **Agronomic Threshold**: Corn reproductive failure occurs when extreme heat coincides with pollination and silking, drastically reducing kernel set. C4 grain sorghum tolerates these temperatures through osmotic adjustment and waxy leaf coatings.

### Root-Zone Soil Wetness (GWETROOT)
* **Data Source**: NASA MERRA-2 Land Surface Model via NASA POWER.
* **Scale**: Dimensionless index from 0.0 (bone dry) to 1.0 (fully saturated).
* **Application**: Captures subsoil moisture availability accessible by deep crop roots (4 to 6 feet).

### Land Surface Temperature (LST) and Thermal Hotspots
* **Sensor**: ECOSTRESS on the International Space Station and MODIS MOD11A2.
* **Physical Principle**: Measures radiometric surface skin temperature.
* **Finding**: Bare fallow topsoil spikes to 120.6°F (49.2°C) under Western Kansas summer sunshine, while adjacent living canopies maintain a 19.4°F (10.8°C) cooling differential via transpiration.

---

## 2. Soil Physics & Topography

### Keith Silt Loam
* **Taxonomic Class**: Fine-silty, mixed, superactive, mesic Aridic Argiustolls.
* **Location**: Dominant soil series across the flat tablelands of Thomas County (Northwest Kansas).
* **Properties**: High available water capacity (~0.22 inches water per inch of soil), deep root penetration (60+ inches), and high fertility. Highly susceptible to wind erosion when residue armor is lost.

### Terrain Slope and Wind vs. Water Erosion
* **Sensor**: NASA SRTM (Shuttle Radar Topography Mission, 30m resolution).
* **Finding**: Western Kansas High Plains display slope gradients under 1.0%. Water runoff and rill erosion are negligible. Soil loss is driven almost entirely by wind detachment during dry spring weather.

---

## 3. Hydrology & Groundwater Management

### Ogallala Aquifer (High Plains Aquifer)
* **Description**: A vast unconfined regional aquifer underlying 174,000 square miles across 8 Great Plains states, supporting intensive irrigated agriculture in Southwest Kansas.
* **Status in Finney County**: Monitored by USGS Well 375713100511801. Water table depth has fallen by 97.3 feet since 1990 due to excessive center-pivot pumping exceeding natural recharge rates (< 0.5 inches/year).

### Groundwater Management District 3 (GMD 3)
* **Jurisdiction**: Southwest Kansas groundwater conservation authority administering Local Enhanced Management Areas (LEMA) to enforce mandatory pumping volume reductions.

### Evapotranspiration (ET) and OpenET
* **Concept**: Combined loss of water through soil evaporation and plant transpiration.
* **Benchmark**: Continuous irrigated corn requires 24 to 28 inches of water per season in Southwest Kansas. By contrast, grain sorghum requires only 16 to 19 inches, conserving over 23 million gallons per 125-acre center-pivot circle.
