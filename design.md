# User Experience & Interface Design System (design.md)
## Project: Field Shift — Western Kansas
**Audience**: Agricultural producers, farm managers, and county extension agronomists in Western Kansas.

---

### 1. Design Vision: Field-Ready & Practical
Farmers and agricultural consultants operate in bright cab environments, outdoor fields, and busy farm offices. They require:
- **Instant Scanability**: High-contrast, large data callouts, and clean visual hierarchies.
- **Rugged Simplicity**: Zero cosmetic tech bloat, zero distracting animations, zero low-contrast aesthetics.
- **Clarity of Meaning**: Immediate answers to *"When is my ground bare?"*, *"How hot was the summer?"*, and *"Which rotation gives me the best water-to-income balance?"*.

---

### 2. Typography & Color Architecture

#### 2.1 Typography
- **Primary Body & Headings**: Clean, robust system sans-serif stack:
  `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;`
- **Typographic Scale**:
  - Main App Header: `26px`, Bold (`font-weight: 700`), Color `#1A202C`
  - Section Headings (H2): `20px`, Semi-bold (`font-weight: 600`), Color `#2D3748`
  - Subsections (H3): `16px`, Medium (`font-weight: 600`), Color `#4A5568`
  - Primary Metric Figures: `28px - 32px`, Bold (`font-weight: 700`)
  - Body Text: `15px`, Regular (`font-weight: 400`), Line-height `1.5`
  - Captions & Attribution Notes: `12px - 13px`, Regular, Color `#64748B`
- **Strictly Banned**:
  - No decorative italic serif accents.
  - No trendy boutique pairings (e.g., Space Grotesk + Instrument Serif).
  - No decorative emojis in headings.
  - No uniform uninspired "Inter font everywhere".

#### 2.2 Color Palette (High-Contrast, Sunlight-Readable)
All colors are chosen for high contrast and immediate agricultural comprehension:

| Swatch / Role | Hex Code | Purpose & Semantic Application |
| :--- | :--- | :--- |
| **Canvas Background** | `#F8FAFC` | Clean, crisp, neutral off-white surface |
| **Card Surface** | `#FFFFFF` | Solid white cards with high-contrast structural borders |
| **Primary Text** | `#0F172A` | Deep charcoal / near black for optimal sunlight readability |
| **Muted Text** | `#475569` | Secondary descriptors, axis labels, and captions |
| **Border / Divider** | `#CBD5E1` | Crisp 1px structural borders (no blurred colored borders) |
| **Agronomic Green** | `#1B5E20` | High NDVI, healthy vegetation, high water-efficiency rating |
| **Stress Amber** | `#B45309` | Moderate water stress, rainfall deficit, advisory indicators |
| **Bare / Drought Rust** | `#B91C1C` | Bare-field window (NDVI < 0.2), extreme heat days, high erosion risk |
| **Water / Aquifer Blue** | `#0369A1` | Groundwater, rainfall totals, irrigation benchmarks |

---

### 3. Screen Structure & Information Architecture

The user interface is organized into five logical zones that flow from context to actionable decision:

#### Zone 1: Persistent Context & Disclaimer Banner
- **Persistent Header**: Displays the tool title, Kansas county focus, and a non-dismissible advisory banner:
  > *"This tool highlights patterns and options. It does not replace your judgment or advice from local agronomists and extension staff."*
- **Visual Style**: Clean neutral background with `#0F172A` border and bold text.

#### Zone 2: Farm Setup & Priority Controls
- **Controls**:
  - County Selection: *Thomas County (Colby)* vs. *Finney County (Garden City)*.
  - Persona Profile: *Dryland Wheat-Fallow Producer* vs. *Irrigated Corn Producer*.
  - Three Farmer Priority Sliders (0 to 10 scale):
    1. *Save Water* (Water efficiency, aquifer conservation)
    2. *Protect Soil* (Residue cover, wind erosion defense)
    3. *Earn Income* (Gross margin reliability, market access)
- Note: Weight adjustments instantly update normalized weights $w_i$ and re-rank strategies dynamically.

#### Zone 3: "My Fields Now" (NDVI & Bare-Ground Timeline)
- **Primary Chart**: 10-year monthly NDVI climatology curve with standard deviation bands.
- **Bare-Field Shading**: Prominently shaded red/amber band across the months where NDVI falls below the configurable threshold (default `0.20`).
- **Plain-Language Summary Box**:
  > *"In Thomas County under wheat-fallow, fields are typically bare for 4 to 5 consecutive months (June through October), leaving soil exposed during high-evaporation summer heat."*

#### Zone 4: Environmental Stress & Field Conditions
Four distinct, clean metric panels with explicit `"What is this?"` explanations:
1. **Extreme Heat Stress Days**: Annual days with $T_{\max} \ge 35^\circ\text{C}$ (critical for reproductive failure).
2. **Frost-Free Growing Season**: Average last spring freeze date to first fall freeze date.
3. **Rainfall Variability & Dry Spells**: Annual precipitation mean vs. maximum dry spell duration.
4. **Root-Zone Moisture Trend**: 10-year soil wetness index from NASA satellite observations.

#### Zone 5: Multi-Strategy Evidence & Comparison Matrix
- Displays 3 to 4 rotation cards side-by-side or stacked on mobile:
  - Card 1: **Existing Baseline** (e.g., Continuous Irrigated Corn or Wheat-Fallow) clearly stamped `CURRENT PRACTICE`.
  - Cards 2–4: **Recommended Alternatives** (e.g., Wheat-Sorghum-Fallow, Corn-Soybean, Wheat with Legume Cover) ranked by weighted score $S_j$.
- **Card Elements (Strict Schema)**:
  - Overall Rank & Score (`S_j = 3.8 / 5.0`)
  - Strategy Name & Summary: Why it fits this county
  - Satellite Evidence bullet points with source badges (`NASA POWER`, `MODIS MOD13Q1`, `NASA SMAP`)
  - Agronomic Benefits
  - Known Information Gaps
  - Risks Requiring Local Agronomic Review
  - Data Confidence Rating: `High`, `Medium`, or `Needs Local Review`

#### Zone 6: Data Transparency & Provenance Modal
- A dedicated collapsible panel categorizing every dataset into:
  - **NASA Earth Observations**: NASA POWER, MODIS, SMAP, GPM IMERG.
  - **Local & Ground Context**: USDA CDL, NRCS SSURGO, K-State Extension agronomic benchmarks.
  - Transparent disclosure of all proxy fallbacks (`is_proxy = True`) and resolution limitations.

---

### 4. Layout Rules & Accessibility Standards
- **Grid Consistency**: Strict 8px baseline grid (padding `16px`, margins `24px`).
- **Tactile State Changes**: Interactive elements provide immediate, crisp border/background state changes without slow transition fades.
- **Zero Scrolljacking**: Natural browser scrolling throughout; no animated fade-ins on scroll.
- **Mobile & Tablet Ready**: Responsive layouts that collapse gracefully into single-column cards on smaller displays.
