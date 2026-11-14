# Artificial Intelligence & Algorithmic Stack (AI Stack)
## Project: Field Shift — Western Kansas

---

### 1. Core Philosophy: Transparent Decision Intelligence vs. Black-Box ML
In agricultural decision-support systems, black-box machine learning models (e.g., deep neural networks or opaque regressors) present high adoption barriers because farmers and extension agronomists cannot audit the reasoning behind recommendations. A model suggesting a farmer plant expensive cover crops without clear empirical rationale risks livelihood and credibility.

**Field Shift implements an Empirical Multi-Criteria Decision Analysis (MCDA) Engine** combined with **deterministic climatological signal processing**. Every recommendation traces mathematically to satellite indicators and peer-reviewed agronomic benchmarks.

---

### 2. Algorithmic Formulation

#### 2.1 Multi-Criteria Scoring Formula
For each rotation strategy $j \in \{1, \dots, M\}$ across criteria $i \in \{1, \dots, 8\}$:

$$S_j = \sum_{i=1}^{8} w_i \cdot r_{ij} \cdot a_{ij}$$

Where:
- **$w_i$ (User & Persona Priority Weights)**:
  $$\sum_{i=1}^{8} w_i = 1.0, \quad w_i \ge 0$$
  Initialized by preset persona archetypes (Dryland Wheat Farmer vs. Irrigated Corn Grower) and adjusted interactively via farmer UI sliders.
- **$r_{ij}$ (Base Agronomic Rating)**:
  Discrete score $r_{ij} \in \{1, 2, 3, 4, 5\}$, established from published Kansas State University (K-State) Research and Extension field trials and documented in `ratings/strategies.json`. (5 is optimal for the farmer's objective).
- **$a_{ij}$ (Data-Driven Adjustment Factor)**:
  Bounded multiplier $a_{ij} \in [0.70, 1.10]$, computed dynamically from NASA Earth Observation indicators to reflect local environmental reality.

---

### 3. Data-Driven Adjustment Derivation Rules ($a_{ij}$)

All adjustment logic is strictly implemented in `engine/scoring.py` and auditable by competition judges and farmers:

#### Rule 1: Bare-Field Duration & Wind Erosion Protection ($a_{\text{cover}}, a_{\text{erosion}}$)
- **Signal**: Number of consecutive months where climatological MODIS NDVI $< 0.20$ ($M_{\text{bare}}$).
- **Baseline**: A healthy rotation in western Kansas should minimize fallow exposure during the high-wind spring period (March–May).
- **Adjustment**:
  $$\text{If } M_{\text{bare}} \ge 4 \text{ months}: \begin{cases} a_{\text{erosion}, j} = 0.75 & \text{for strategies with bare summer fallow} \\ a_{\text{erosion}, j} = 1.10 & \text{for strategies with cover crops or continuous residue} \\ a_{\text{cover}, j} = 1.10 & \text{for strategies maintaining winter ground cover} \end{cases}$$

#### Rule 2: Heat-Stress Frequency ($a_{\text{drought}}, a_{\text{water}}$)
- **Signal**: Annual frequency of extreme heat days ($T_{\max} \ge 35^\circ\text{C}$) during critical reproductive windows (July–August).
- **Adjustment**:
  - If 10-year mean heat-stress days $> 25 \text{ days/year}$:
    - Penalize high-ET crops with sensitive pollination windows (e.g., continuous corn): $a_{\text{drought}} = 0.80$, $a_{\text{water}} = 0.75$.
    - Reward heat-resilient C4 crops (e.g., grain sorghum/milo): $a_{\text{drought}} = 1.10$, $a_{\text{water}} = 1.05$.

#### Rule 3: Rainfall Variability & Extended Dry Spells ($a_{\text{drought}}, a_{\text{income}}$)
- **Signal**: Coefficient of Variation ($\text{CV}$) of growing-season precipitation and maximum dry-spell duration ($D_{\max}$, consecutive days $< 1.0\text{ mm}$).
- **Adjustment**:
  - When $D_{\max} > 21 \text{ days}$ during vegetative development:
    - Increase the value of deep-rooted or moisture-sipping crops: $a_{\text{drought}} = 1.10$.
    - Lower the income stability rating of high-input, moisture-dependent regimes: $a_{\text{income}} = 0.85$.

#### Rule 4: Soil Moisture Anomaly & Aquifer Drawdown Context
- **Signal**: Root-zone soil wetness percentile anomaly (NASA POWER / SMAP).
- **Adjustment**:
  - In negative anomaly states (drier than 10-year historical 20th percentile):
    - Escalate water-efficiency weight in the overall matrix and adjust water-intensive crops downward: $a_{\text{water}} = 0.70$.

---

### 4. Interactive Climate Scenario Perturbation Engine
To answer the farmer question *"What if next year is hotter and drier?"*, the system includes a perturbation engine in `engine/scenarios.py`:
- **Inputs**:
  - $\Delta \text{Rainfall} \in [-30\%, +20\%]$
  - $\Delta \text{Temperature} \in [0^\circ\text{C}, +3.0^\circ\text{C}]$
- **Perturbation Mechanism**:
  1. Base temperature series shifted: $T_{\text{daily}}' = T_{\text{daily}} + \Delta T$.
  2. Precipitation scaled: $P_{\text{daily}}' = P_{\text{daily}} \times (1 + \Delta P / 100)$.
  3. Indicators recomputed dynamically (e.g., recount $T_{\max}' \ge 35^\circ\text{C}$, adjust dry spell lengths).
  4. Dynamic multipliers $a_{ij}'$ recalculated and strategy rankings live-updated.

---

### 5. Uncertainty & Data Quality Confidence Scoring
Every criterion score is assigned an empirical confidence level based on source pedigree:
- **`High Confidence`**: Derived from direct, calibrated satellite observations or official ground data (e.g., NASA POWER daily meteorological series, MODIS NDVI composite).
- **`Medium Confidence`**: Derived from validated satellite models or downscaled estimates (e.g., NASA POWER root-zone wetness proxy for SMAP).
- **`Low Confidence` / `Needs Local Review`**: Starter agronomic heuristic ratings or coarse regional estimations that require site-specific soil testing or local extension agronomist verification.

---

### 6. Role & Guardrails for Generative AI / LLMs (If Extended)
If GenAI is utilized for narrative explanation or query translation:
1. **Strict Context Grounding**: The LLM prompt receives strictly structured JSON containing the computed evidence card, verified indicators, and exact numerical ratings.
2. **Zero Hallucination Tolerance**: Prompts enforce negative constraints: *"Never invent numeric yields, profit margins, or chemical recommendations. Only explain the provided satellite evidence in plain agricultural language."*
3. **No Direct Execution**: The LLM never calculates scores or adjustments; it only translates structured JSON evidence cards into accessible farmer summaries.
