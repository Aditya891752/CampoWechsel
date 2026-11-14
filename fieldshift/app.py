"""
Field Shift: Western Kansas — Complete Decision-Support Web App (Phase 0, 1 & 2)
NASA International Space Apps Challenge
Farmer-friendly crop-rotation comparison powered by NASA Earth observations.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import streamlit as st

from fieldshift.config import (
    COUNTIES,
    PERSONAS,
    PROCESSED_DATA_DIR,
    DEFAULT_BARE_FIELD_NDVI,
    CRITERIA,
)
from fieldshift.engine.scoring import (
    map_3_slider_to_criteria_weights,
    score_strategies,
)
from fieldshift.engine.scenarios import perturb_indicators
from fieldshift.engine.evidence import generate_evidence_cards
from fieldshift.engine.report_generator import generate_html_report
from fieldshift.i18n import get_text

# 1. Page Configuration & Farmer-First High-Contrast Styling
st.set_page_config(
    page_title="Field Shift — Western Kansas",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Clean System Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
    }
    
    h1 {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    h2 {
        color: #1E293B;
        font-size: 1.25rem;
        font-weight: 600;
        border-bottom: 2px solid #CBD5E1;
        padding-bottom: 0.35rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    h3 {
        color: #334155;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.75rem;
        margin-bottom: 0.35rem;
    }

    /* Persistent Advisory Banner */
    .advisory-banner {
        background-color: #EFF6FF;
        border-left: 5px solid #0369A1;
        padding: 12px 16px;
        margin-bottom: 1.25rem;
        font-size: 0.92rem;
        color: #1E3A8A;
        font-weight: 500;
        line-height: 1.45;
    }

    /* Summary Callout Box */
    .summary-callout {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 4px solid #1B5E20;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.95rem;
        color: #0F172A;
        line-height: 1.5;
    }

    /* Strategy Card */
    .strategy-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .strategy-card-existing {
        background-color: #F8FAFC;
        border: 2px solid #64748B;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .strategy-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .score-badge {
        display: inline-block;
        background-color: #1B5E20;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 3px 8px;
        border-radius: 3px;
        margin-bottom: 8px;
    }
    .score-badge-existing {
        display: inline-block;
        background-color: #475569;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 3px 8px;
        border-radius: 3px;
        margin-bottom: 8px;
    }
    .practice-tag {
        display: inline-block;
        background-color: #E2E8F0;
        color: #1E293B;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 3px 7px;
        border-radius: 3px;
        margin-left: 6px;
        text-transform: uppercase;
    }

    .confidence-tag {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 2px;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .conf-high { background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    .conf-med { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .conf-low { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }

    .condition-metric-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        padding: 12px 14px;
        border-radius: 4px;
        height: 100%;
    }
    .condition-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0F172A;
    }
    .condition-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_all_datasets():
    """Load cached preprocessed datasets for offline operation."""
    with open(PROCESSED_DATA_DIR / "indicators.json", "r", encoding="utf-8") as f:
        indicators = json.load(f)
    with open(PROCESSED_DATA_DIR / "cdl_crop_history.json", "r", encoding="utf-8") as f:
        cdl = json.load(f)
    with open(PROCESSED_DATA_DIR / "ssurgo_soils.json", "r", encoding="utf-8") as f:
        soils = json.load(f)
    with open(PROCESSED_DATA_DIR / "srtm_terrain.json", "r", encoding="utf-8") as f:
        srtm = json.load(f)
    with open(PROCESSED_DATA_DIR / "spatial_grid.json", "r", encoding="utf-8") as f:
        spatial = json.load(f)
    with open(PROCESSED_DATA_DIR / "gpm_extreme_rain.json", "r", encoding="utf-8") as f:
        gpm = json.load(f)
    with open(PROCESSED_DATA_DIR / "groundwater_nwis.json", "r", encoding="utf-8") as f:
        gw = json.load(f)
    with open(PROCESSED_DATA_DIR / "openet_water_budget.json", "r", encoding="utf-8") as f:
        openet = json.load(f)
    with open(PROCESSED_DATA_DIR / "lst_thermal.json", "r", encoding="utf-8") as f:
        lst = json.load(f)
    with open(PROCESSED_DATA_DIR / "nass_and_market.json", "r", encoding="utf-8") as f:
        nass = json.load(f)

    tidy_df = pd.read_csv(PROCESSED_DATA_DIR / "tidy_monthly.csv")
    smap_df = pd.read_csv(PROCESSED_DATA_DIR / "smap_monthly_anomalies.csv")
    return indicators, cdl, soils, srtm, spatial, gpm, gw, openet, lst, nass, tidy_df, smap_df


(
    base_indicators,
    cdl_data,
    soils_data,
    srtm_data,
    spatial_data,
    gpm_data,
    gw_data,
    openet_data,
    lst_data,
    nass_data,
    tidy_df,
    smap_df,
) = load_all_datasets()

# 2. Sidebar Setup & Language Toggle (P2)
st.sidebar.markdown("### Language / भाषा")
lang = st.sidebar.radio(
    "Interface Language",
    options=["en", "hi"],
    format_func=lambda l: "English" if l == "en" else "हिंदी (Hindi)",
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

st.sidebar.markdown(f"### {get_text('farm_setup', lang)}")

county_choice = st.sidebar.selectbox(
    get_text("select_county", lang),
    options=list(COUNTIES.keys()),
    format_func=lambda c: f"{COUNTIES[c]['name']} ({COUNTIES[c]['system']})",
    index=0,
)
county_info = COUNTIES[county_choice]
persona_key = county_info["default_persona"]
persona_info = PERSONAS[persona_key]

st.sidebar.markdown(f"**Anchor Point:** {county_info['seat']}, KS (`{county_info['lat']}° N, {county_info['lon']}° W`)")
st.sidebar.markdown(f"**Primary Tension:** {county_info['main_tension']}")
st.sidebar.caption(persona_info["description"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {get_text('priority_sliders', lang)}")
st.sidebar.caption(get_text("priority_caption", lang))

save_water = st.sidebar.slider(get_text("save_water", lang), min_value=0, max_value=10, value=7)
protect_soil = st.sidebar.slider(get_text("protect_soil", lang), min_value=0, max_value=10, value=8)
earn_income = st.sidebar.slider(get_text("earn_income", lang), min_value=0, max_value=10, value=6)

computed_weights = map_3_slider_to_criteria_weights(save_water, protect_soil, earn_income)

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {get_text('climate_scenarios', lang)}")
st.sidebar.caption(get_text("climate_caption", lang))

rain_delta = st.sidebar.slider(get_text("rain_change", lang), min_value=-30, max_value=20, value=0, step=5, format="%d%%")
temp_delta = st.sidebar.slider(get_text("temp_increase", lang), min_value=0.0, max_value=3.0, value=0.0, step=0.5, format="+%.1f°C")

active_indicators = perturb_indicators(base_indicators[county_choice], temp_delta_c=temp_delta, rain_delta_pct=rain_delta)

# Header & Persistent Advisory Banner
st.title(get_text("title", lang))
st.markdown(f"**{get_text('subtitle', lang)}**")

st.markdown(
    f"""
    <div class="advisory-banner">
        {get_text('advisory', lang)}
    </div>
    """,
    unsafe_allow_html=True,
)

# SECTION 1: "My Fields Now" (NDVI Timeline)
st.markdown(f"## {get_text('sec_my_fields', lang)}")

col_thresh, col_stat = st.columns([1, 2])
with col_thresh:
    ndvi_threshold = st.slider(
        get_text("threshold_label", lang),
        min_value=0.10,
        max_value=0.35,
        value=DEFAULT_BARE_FIELD_NDVI,
        step=0.01,
        help="NDVI values below this threshold indicate bare dry ground or sparse stubble.",
    )

clim_data = active_indicators["ndvi_bare_field"]["monthly_climatology"]
months = [d["month_name"] for d in clim_data]
means = [d["mean"] for d in clim_data]
stds = [d["std"] for d in clim_data]
bare_months_active = [d["month_name"] for d in clim_data if d["mean"] < ndvi_threshold]

with col_stat:
    bare_count = len(bare_months_active)
    if county_choice == "Thomas":
        summary_text = (
            f"Under the traditional wheat–fallow system in Thomas County, your ground is typically bare "
            f"for <strong>{bare_count} months</strong> ({', '.join(bare_months_active)}) with NDVI below {ndvi_threshold:.2f}. "
            f"The post-harvest summer window (July–September) leaves pulverized topsoil exposed to high evaporative heat and intense spring winds."
        )
    else:
        summary_text = (
            f"In Finney County under continuous corn, your fields remain bare for <strong>{bare_count} months</strong> "
            f"({', '.join(bare_months_active)}) during the winter and early spring pre-planting window before canopy closure in June. "
            f"Summer water extraction peaks sharply in July and August under center pivots."
        )
    st.markdown(f'<div class="summary-callout">{summary_text}</div>', unsafe_allow_html=True)

fig_ndvi = go.Figure()
upper_band = [m + s for m, s in zip(means, stds)]
lower_band = [max(0.05, m - s) for m, s in zip(means, stds)]

fig_ndvi.add_trace(go.Scatter(
    x=months + months[::-1],
    y=upper_band + lower_band[::-1],
    fill="toself",
    fillcolor="rgba(27, 94, 32, 0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip",
    showlegend=True,
    name="±1 Std Dev (10-Yr Climatology)",
))

fig_ndvi.add_trace(go.Scatter(
    x=months,
    y=means,
    mode="lines+markers",
    line=dict(color="#1B5E20", width=3),
    marker=dict(size=7, color="#1B5E20"),
    name="10-Year Mean NDVI",
    hovertemplate="Month: %{x}<br>NDVI: %{y:.3f}<extra></extra>",
))

fig_ndvi.add_hline(
    y=ndvi_threshold,
    line_dash="dash",
    line_color="#B91C1C",
    line_width=2,
    annotation_text=f"Bare-Field Threshold ({ndvi_threshold:.2f})",
    annotation_position="bottom right",
    annotation_font_color="#B91C1C",
)

for idx, d in enumerate(clim_data):
    if d["mean"] < ndvi_threshold:
        fig_ndvi.add_vrect(x0=idx - 0.45, x1=idx + 0.45, fillcolor="#B91C1C", opacity=0.08, line_width=0)

fig_ndvi.update_layout(
    height=300,
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis_title="Calendar Month",
    yaxis_title="NDVI (Greenness Index)",
    yaxis=dict(range=[0.05, 0.85], gridcolor="#E2E8F0"),
    xaxis=dict(gridcolor="#E2E8F0"),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_ndvi, use_container_width=True)
st.caption("Data Source: MODIS MOD13Q1 (250m, 16-day composite) via calibrated AppEEARS point proxy modulated by NASA POWER daily observations. [is_proxy = True]")

# SECTION 2: Environmental Stress & Field Conditions
st.markdown(f"## {get_text('sec_conditions', lang)}")

m1, m2, m3, m4 = st.columns(4)
heat_meta = active_indicators["heat_stress"]
frost_meta = active_indicators["frost_risk"]
rain_meta = active_indicators["rainfall"]
soil_meta = active_indicators["soil_moisture"]
gpm_county = gpm_data[county_choice]

with m1:
    st.markdown(
        f"""
        <div class="condition-metric-card">
            <div class="condition-label">Extreme Heat Days (Tmax ≥ 35°C)</div>
            <div class="condition-value">{heat_meta['annual_mean_heat_days']} days/yr</div>
            <p style="font-size:0.80rem; color:#64748B; margin-top:4px;">Worst year: {heat_meta['worst_heat_year']} ({heat_meta['max_annual_heat_days']} days)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("What is this?"):
        st.write("Number of days where daytime temperatures exceed 35°C (95°F). High heat during July and August aborts corn pollination and rapidly evaporates topsoil moisture.")

with m2:
    st.markdown(
        f"""
        <div class="condition-metric-card">
            <div class="condition-label">Frost-Free Window</div>
            <div class="condition-value">{frost_meta['median_frost_free_days']} days</div>
            <p style="font-size:0.80rem; color:#64748B; margin-top:4px;">{frost_meta['median_last_spring_freeze_date']} to {frost_meta['median_first_fall_freeze_date']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("What is this?"):
        st.write("The typical number of days between the last spring freeze (0°C) and the first autumn freeze. Sets maturity limits for summer crops.")

with m3:
    st.markdown(
        f"""
        <div class="condition-metric-card">
            <div class="condition-label">Rainfall & Storm Deluges</div>
            <div class="condition-value">{rain_meta['annual_mean_precip_inches']}" ({rain_meta['annual_mean_precip_mm']} mm)</div>
            <p style="font-size:0.80rem; color:#64748B; margin-top:4px;">GPM Heavy Storms (≥1"): {gpm_county['annual_avg_storms_over_1in']}/yr | Max: {rain_meta['max_dry_spell_days']}d dry</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("What is this?"):
        st.write("10-year mean annual precipitation and storm intensity. Heavy rains (≥1\") create rapid runoff risks if fields lack vegetative armor.")

with m4:
    st.markdown(
        f"""
        <div class="condition-metric-card">
            <div class="condition-label">Root-Zone Wetness Index</div>
            <div class="condition-value">{soil_meta['mean_root_zone_wetness']} (0 to 1)</div>
            <p style="font-size:0.80rem; color:#64748B; margin-top:4px;">NASA MERRA-2 Proxy [is_proxy: True]</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("What is this?"):
        st.write("Root-zone soil wetness index (top 1 meter). Values below 0.35 indicate that root-zone moisture is severely depleted, requiring deep-root scavenging or irrigation buffering.")

# SECTION 3: Compare Rotation Strategies
st.markdown(f"## {get_text('sec_strategies', lang)}")
st.markdown("Strategies are scored and ranked using the formula: $S_j = \\sum w_i \\cdot r_{ij} \\cdot a_{ij}$, where base agronomic ratings ($r_{ij}$) are dynamically adjusted by NASA satellite indicators ($a_{ij}$).")

evidence_cards = generate_evidence_cards(county_choice, active_indicators, custom_weights=computed_weights)

cols = st.columns(len(evidence_cards))
for idx, card in enumerate(evidence_cards):
    with cols[idx]:
        is_exist = card["is_existing"]
        card_class = "strategy-card-existing" if is_exist else "strategy-card"
        badge_class = "score-badge-existing" if is_exist else "score-badge"
        practice_tag = f'<span class="practice-tag">{get_text("current_practice", lang)}</span>' if is_exist else f'<span class="practice-tag">{get_text("rank", lang)} #{idx+1}</span>'

        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="{badge_class}">Score: {card['score']:.2f} / 5.0</div>{practice_tag}
                <div class="strategy-title">{card['strategy']}</div>
                <p style="font-size:0.88rem; color:#334155; margin-top:6px; margin-bottom:10px;">{card['why_suggested']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Satellite Evidence", expanded=True):
            for ev in card["evidence"]:
                proxy_label = " [Proxy]" if ev.get("is_proxy") else ""
                st.markdown(f"• **{ev['signal']}**")
                st.caption(f"Source: {ev['source']}{proxy_label}")

        with st.expander("Agronomic Benefits", expanded=False):
            for b in card["benefits"]:
                st.markdown(f"✓ {b}")

        with st.expander("Information Gaps", expanded=False):
            for g in card["information_gaps"]:
                st.markdown(f"⚠ {g}")

        with st.expander("Risks Needing Local Review", expanded=False):
            for r in card["risks_needing_local_review"]:
                st.markdown(f"❗ {r}")

        with st.expander("Confidence & Adjustments", expanded=False):
            conf_html = ""
            for crit, level in card["confidence"].items():
                cls_name = "conf-high" if level == "high" else ("conf-med" if level == "medium" else "conf-low")
                conf_html += f'<span class="confidence-tag {cls_name}">{crit.title()}: {level.upper()}</span>'
            st.markdown(conf_html, unsafe_allow_html=True)

            breakdown_df = pd.DataFrame([
                {
                    "Criterion": CRITERIA[c_idx]["name"],
                    "Base (r)": v["base_rating"],
                    "NASA Mod (a)": f"{v['adjustment_a']:.2f}",
                    "Weight (w)": f"{v['weight_w']:.2f}",
                    "Points": f"{v['effective_contribution']:.2f}",
                }
                for c_idx, (k, v) in enumerate(card["criteria_breakdown"].items())
            ])
            st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

# Report Generation & Download Button (P2)
report_html = generate_html_report(county_choice, persona_info["title"], active_indicators, evidence_cards, computed_weights)
st.sidebar.markdown("---")
st.sidebar.markdown("### Export Strategy Report (P2)")
st.sidebar.download_button(
    label=get_text("download_report_btn", lang),
    data=report_html,
    file_name=f"FieldShift_Report_{county_choice}.html",
    mime="text/html",
    help="Download clean, publication-grade HTML report suitable for printing directly to PDF (Ctrl+P).",
)

# SECTION 4: Side-by-Side Comparison Tool
st.markdown(f"## {get_text('sec_comparison', lang)}")

existing_card = next((c for c in evidence_cards if c["is_existing"]), evidence_cards[0])
alt_options = [c for c in evidence_cards if not c["is_existing"]]

if alt_options:
    chosen_alt = st.selectbox(
        "Select an Alternative Strategy to Compare Against Current Practice:",
        options=alt_options,
        format_func=lambda c: f"{c['strategy']} (Score: {c['score']:.2f} / 5.0)",
    )

    diff_col1, diff_col2 = st.columns([1, 1])
    with diff_col1:
        st.markdown(f"### Current Practice: {existing_card['strategy']}")
        st.markdown(f"**Overall Score:** `{existing_card['score']:.2f} / 5.0`")
        st.write(existing_card["why_suggested"])

    with diff_col2:
        score_diff = chosen_alt["score"] - existing_card["score"]
        diff_str = f"+{score_diff:.2f}" if score_diff > 0 else f"{score_diff:.2f}"
        st.markdown(f"### Alternative: {chosen_alt['strategy']}")
        st.markdown(f"**Overall Score:** `{chosen_alt['score']:.2f} / 5.0` (Net: **{diff_str} points**)")
        st.write(chosen_alt["why_suggested"])

    criteria_comparison = []
    for c_idx, crit in enumerate(CRITERIA):
        k = crit["key"]
        curr_b = existing_card["criteria_breakdown"][k]["base_rating"]
        alt_b = chosen_alt["criteria_breakdown"][k]["base_rating"]
        diff = alt_b - curr_b
        diff_sign = f"+{int(diff)}" if diff > 0 else (str(int(diff)) if diff < 0 else "0")
        criteria_comparison.append({
            "Criterion": crit["name"],
            "Current Rating (1-5)": int(curr_b),
            "Alternative Rating (1-5)": int(alt_b),
            "Rating Difference": diff_sign,
            "Agronomic Meaning": crit["desc"],
        })
    st.dataframe(pd.DataFrame(criteria_comparison), hide_index=True, use_container_width=True)

# SECTION 5: Annual Crop Year Timeline View
st.markdown(f"## {get_text('sec_timeline', lang)}")

timeline_data = {
    "Thomas": [
        {"Strategy": "Wheat–fallow (existing)", "Jan": "Bare", "Feb": "Bare", "Mar": "Crop", "Apr": "Crop", "May": "Crop Peak", "Jun": "Harvest", "Jul": "BARE FALLOW", "Aug": "BARE FALLOW", "Sep": "BARE FALLOW", "Oct": "Emergence", "Nov": "Dormant", "Dec": "Bare"},
        {"Strategy": "Wheat–sorghum–fallow", "Jan": "Residue", "Feb": "Residue", "Mar": "Residue", "Apr": "Residue", "May": "Planting", "Jun": "Emergence", "Jul": "Crop", "Aug": "Crop Peak", "Sep": "Maturity", "Oct": "Harvest", "Nov": "Residue", "Dec": "Residue"},
        {"Strategy": "Wheat w/ legume cover", "Jan": "Dormant", "Feb": "Dormant", "Mar": "Crop", "Apr": "Crop", "May": "Crop Peak", "Jun": "Harvest", "Jul": "Cover Planted", "Aug": "Cover Canopy", "Sep": "Cover Canopy", "Oct": "Terminated", "Nov": "Residue", "Dec": "Residue"},
    ],
    "Finney": [
        {"Strategy": "Continuous corn (existing)", "Jan": "Bare Stubble", "Feb": "Bare Stubble", "Mar": "Bare", "Apr": "Planting", "May": "Emergence", "Jun": "Canopy", "Jul": "PEAK PUMPING", "Aug": "PEAK PUMPING", "Sep": "Maturity", "Oct": "Harvest", "Nov": "Stubble", "Dec": "Stubble"},
        {"Strategy": "Corn–soybean", "Jan": "Stubble", "Feb": "Stubble", "Mar": "Bare", "Apr": "Corn Plant", "May": "Soy Plant", "Jun": "Emergence", "Jul": "Staggered Water", "Aug": "Staggered Water", "Sep": "Harvest", "Oct": "Harvest", "Nov": "Residue", "Dec": "Residue"},
        {"Strategy": "Corn–wheat–sorghum", "Jan": "Wheat Dormant", "Feb": "Wheat Green", "Mar": "Wheat Head", "Apr": "Corn Plant", "May": "Sorghum Plant", "Jun": "Wheat Harvest", "Jul": "Corn Water", "Aug": "Sorghum Water", "Sep": "Corn Harvest", "Oct": "Sorghum Harvest", "Nov": "Wheat Plant", "Dec": "Residue"},
    ]
}
st.dataframe(pd.DataFrame(timeline_data[county_choice]), hide_index=True, use_container_width=True)

# SECTION 6: Interactive Spatial Map & Vulnerability Grid
st.markdown(f"## {get_text('sec_map', lang)}")

c_spatial = spatial_data[county_choice]
cells = c_spatial["cells"]

m = folium.Map(
    location=[c_spatial["anchor_lat"], c_spatial["anchor_lon"]],
    zoom_start=11,
    tiles="CartoDB positron",
    control_scale=True,
)

folium.Marker(
    location=[c_spatial["anchor_lat"], c_spatial["anchor_lon"]],
    popup=f"<b>Anchor Hub: {COUNTIES[county_choice]['seat']}</b><br>Elevation: {COUNTIES[county_choice]['elevation_m']}m",
    icon=folium.Icon(color="green", icon="info-sign"),
).add_to(m)

for cell in cells:
    if "Severe Wind" in cell["vulnerability_classification"] or "Critical Ogallala" in cell["vulnerability_classification"]:
        color = "#B91C1C"
        fill_color = "#FCA5A5"
    else:
        color = "#0369A1"
        fill_color = "#BAE6FD"

    popup_html = f"""
    <div style="font-family:sans-serif; font-size:12px; width:220px;">
        <h4 style="margin:0 0 6px 0; color:#0F172A;">{cell['cell_id']}: {cell['label']}</h4>
        <b>Coordinates:</b> {cell['lat']}° N, {cell['lon']}° W<br>
        <b>Peak NDVI:</b> {cell['peak_ndvi']}<br>
        <b>Annual Heat Days (≥35°C):</b> {cell['annual_heat_days']} d<br>
        <b>Root-Zone Moisture:</b> {cell['root_zone_moisture']}<br>
        <b>Bare Window:</b> {cell['bare_months_count']} months<br>
        <hr style="margin:6px 0;">
        <b>Vulnerability:</b> <span style="color:{color}; font-weight:bold;">{cell['vulnerability_classification']}</span><br>
        <b>Top Recommendation:</b> {cell['recommended_strategy']}
    </div>
    """
    folium.CircleMarker(
        location=[cell["lat"], cell["lon"]],
        radius=14,
        color=color,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.7,
        weight=2,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{cell['cell_id']} ({cell['label']}) — Click for details",
    ).add_to(m)

st_folium(m, height=380, use_container_width=True)
st.caption("Interactive Leaflet map showing 3×3 grid tiles around anchor point. High-vulnerability zones (wind detachment or severe aquifer decline) highlighted in red.")

# SECTION 7: Groundwater Trends & NASA GRACE-FO (P2)
st.markdown(f"## {get_text('sec_groundwater', lang)}")

c_gw = gw_data[county_choice]
gw_col1, gw_col2 = st.columns([1, 1])

with gw_col1:
    st.markdown(f"**USGS Monitoring Well:** `{c_gw['usgs_well_id']}` ({c_gw['well_name']})")
    st.markdown(f"**Total Water Table Decline (1990–2024):** `{c_gw['total_decline_ft_since_1990']} feet` (Rate: `{c_gw['annual_decline_rate_ft_yr']} ft/yr`)")
    st.markdown(f"**Estimated Usable Lifespan:** `{c_gw['estimated_usable_years_remaining']}`")
    st.info(f"**NASA GRACE-FO Context:** {c_gw['grace_fo_context']}")

with gw_col2:
    gw_df = pd.DataFrame(c_gw["hydrograph"])
    fig_gw = go.Figure()
    fig_gw.add_trace(go.Scatter(
        x=gw_df["year"],
        y=gw_df["depth_to_water_ft"],
        mode="lines+markers",
        line=dict(color="#B91C1C" if county_choice == "Finney" else "#0369A1", width=2.5),
        marker=dict(size=6),
        name="Depth to Water (ft)",
    ))
    fig_gw.update_layout(
        height=260,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis_title="Monitoring Year",
        yaxis_title="Depth to Groundwater (ft)",
        yaxis=dict(autorange="reversed", gridcolor="#E2E8F0"),  # Deeper water plotted downward
        xaxis=dict(gridcolor="#E2E8F0"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig_gw, use_container_width=True)

# SECTION 8: OpenET Crop Water Demand & Center-Pivot Savings (P2)
if county_choice == "Finney":
    st.markdown(f"## {get_text('sec_openet', lang)}")
    c_openet = openet_data["Finney"]
    st.markdown(f'<div class="summary-callout"><strong>Center-Pivot Groundwater Conservation:</strong> {c_openet["key_takeaway"]}</div>', unsafe_allow_html=True)

    et_table = pd.DataFrame([
        {
            "Cropping Strategy": s["strategy"],
            "Seasonal ET (in)": s["seasonal_etc_inches"],
            "Net Irrigation Need (in)": s["net_irrigation_demand_inches"],
            "Pumping Volume / Pivot (gal)": f"{s['pumping_volume_gallons_per_pivot']:,}",
            "Annual Water Saved (gal)": f"{s['gallons_saved_per_pivot']:,}",
            "Pumping Energy Cost ($)": f"${s['energy_pumping_cost_per_pivot']:,}",
            "Water Reduction (%)": f"{s['water_savings_vs_existing_pct']}%",
        }
        for s in c_openet["strategies_water_budget"]
    ])
    st.dataframe(et_table, hide_index=True, use_container_width=True)

# SECTION 9: ECOSTRESS & MODIS LST Thermal Hotspots (P2)
st.markdown(f"## {get_text('sec_lst', lang)}")

c_lst = lst_data[county_choice]
lst_col1, lst_col2 = st.columns([1, 1])

with lst_col1:
    st.markdown(
        f"""
        <div class="condition-metric-card">
            <div class="condition-label">Midsummer Surface Temperature Differential</div>
            <div class="condition-value" style="color:#B91C1C;">{c_lst['bare_fallow_surface_temp_f']}°F ({c_lst['bare_fallow_surface_temp_c']}°C)</div>
            <p style="font-size:0.85rem; color:#475569; margin-top:4px;">
                Bare fallow reaches <strong>{c_lst['bare_fallow_surface_temp_f']}°F</strong> at midday, while living canopies stay at 
                <strong>{c_lst['vegetated_canopy_surface_temp_f']}°F</strong> — a cooling advantage of 
                <strong>{abs(c_lst['canopy_cooling_differential_f'])}°F ({abs(c_lst['canopy_cooling_differential_c'])}°C)</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with lst_col2:
    st.info(f"**Agronomic Impact on Soil:** {c_lst['agronomic_consequence']}")

# SECTION 10: USDA NASS Historical Yields & PRISM Comparison (P2)
st.markdown("## 10. USDA NASS Yield History & Satellite vs. Ground Calibration")

c_nass = nass_data[county_choice]
nass_col1, nass_col2 = st.columns([1, 1])

with nass_col1:
    st.markdown("### Historical Yield Benchmarks (USDA NASS 2015–2024)")
    yields_display = []
    for crop_k, y_vals in c_nass["yields"].items():
        crop_clean = crop_k.replace("_", " ").title()
        yields_display.append({
            "Crop": crop_clean,
            "10-Year County Mean": y_vals["10yr_mean"],
            "Severe Drought (2022)": y_vals["drought_year_2022"],
            "Favorable Season": y_vals[list(y_vals.keys())[2]],
        })
    st.dataframe(pd.DataFrame(yields_display), hide_index=True, use_container_width=True)

with nass_col2:
    st.markdown("### Satellite (POWER) vs. Ground (PRISM) Rainfall")
    sat_ground = c_nass["satellite_vs_ground"]
    st.markdown(f"• **NASA POWER 10-Yr Mean:** `{sat_ground['nasa_power_10yr_mean_inches']} inches`")
    st.markdown(f"• **PRISM Ground Station Mean:** `{sat_ground['prism_ground_10yr_mean_inches']} inches` (Diff: `{sat_ground['difference_inches']} in`, $r = {sat_ground['correlation_coefficient']}$)")
    st.caption(sat_ground["plain_explanation"])

    st.markdown("### Local Indicative Market Pricing")
    st.dataframe(pd.DataFrame(c_nass["market_fit"]), hide_index=True, use_container_width=True)

# SECTION 11: Data Provenance & Scientific Transparency
st.markdown(f"## {get_text('sec_provenance', lang)}")

tab_nasa, tab_non_nasa, tab_limits = st.tabs(["NASA Earth Observations", "Non-NASA Ground Context", "Known Scientific Limitations"])

with tab_nasa:
    st.markdown(
        """
        | Dataset Name | Mission / Platform | Spatial Resolution | Temporal Extent | Parameter Utilized | Proxy Status |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **NASA POWER Daily** | MERRA-2 / GEOS | 0.5° × 0.5° (~50 km) | 2015–2024 (Daily) | T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M | Direct NASA observation (`is_proxy = False`) |
        | **NASA POWER MERRA-2** | Modern-Era Retrospective Analysis | 0.5° × 0.5° | 2015–2024 (Daily) | Root-Zone Soil Wetness (`GWETROOT`, 0–1) | Model-based proxy for SMAP (`is_proxy = True`) |
        | **MODIS MOD13Q1** | Terra / LP DAAC | 250m | 2015–2024 (16-day) | Normalized Difference Vegetation Index (NDVI) | Calibrated AppEEARS point proxy (`is_proxy = True`) |
        | **NASA GPM IMERG** | Global Precipitation Measurement | 0.1° × 0.1° (~10 km)| 2015–2024 | Extreme rain event frequency (≥1" & ≥2") | Labeled POWER precipitation proxy (`is_proxy = True`) |
        | **NASA SMAP L3** | Soil Moisture Active Passive | 9 km / 36 km | 2015–2024 | Standardized monthly soil moisture anomaly | Labeled POWER root-zone proxy (`is_proxy = True`) |
        | **NASA SRTM 30m** | Space Shuttle Endeavour | 30m | Static Global | Topographic slope & elevation profile | Direct observation (`is_proxy = False`) |
        | **NASA ECOSTRESS / MODIS LST**| Space Station & Terra | 70m / 1km | 2015–2024 | Land Surface Temperature (LST) thermal contrast | Model-calibrated thermal proxy (`is_proxy = True`) |
        | **NASA GRACE-FO** | Twin Satellite Gravimetry | Regional Basin | 2018–2024 | High Plains Terrestrial Water Storage anomaly | Regional gravitational trend analysis |
        """
    )

with tab_non_nasa:
    st.markdown(
        """
        | Source | Institution | Role in Field Shift | Attribution & Citation |
        | :--- | :--- | :--- | :--- |
        | **K-State Research & Extension** | Kansas State University | Baseline 1–5 agronomic suitability ratings | Extension Bulletins MF-2573, SRL-138, C-560, MF-573, MF-3244 |
        | **USDA NRCS SSURGO** | USDA Natural Resources Conservation Service | County soil textures, available water capacity, wind erodibility | NRCS Soil Data Access REST |
        | **USDA CropScape CDL** | USDA National Agricultural Statistics Service | Historical crop rotation sequences (2015–2024) | CropScape API GetCDLStat |
        | **USGS NWIS** | US Geological Survey & KGS | Ogallala Aquifer monitoring well hydrographs (1990–2024) | USGS NWIS Water Services REST |
        | **OpenET Multi-Model Ensemble** | OpenET Consortium & Desert Research Inst. | Field-scale crop evapotranspiration & pumping budgets | OpenET satellite ensemble model |
        | **PRISM Climate Group** | Oregon State University | 4km gridded ground precipitation station calibration | PRISM 30-Year Climate Normals |
        """
    )

with tab_limits:
    st.markdown(
        """
        ### What This Tool Cannot Do:
        1. **Spatial Resolution Limits**: Satellite products like NASA POWER (0.5°) and SMAP (9–36 km) capture regional weather and moisture trends. They **cannot resolve intra-field soil differences**, terrace microclimates, or individual center-pivot nozzles.
        2. **Stored Soil Moisture Timing**: Real-world rotation decisions in Western Kansas depend decisively on moisture depth (probing to 3–4 feet) at the exact week of planting. Satellite indicators show historical climatology and regional trends, not daily subsoil depth.
        3. **Wind Erosion vs. Slope**: In flat Western Kansas terrain, wind erosion is driven by soil texture, surface roughness, and residue cover, not topography slope.
        4. **Local Economic Fluctuations**: Market basis, haul distances to grain elevators or feedlots, and individual equipment configurations are operation-specific.
        """
    )

with st.expander("Plain-Language Agronomic Glossary"):
    st.markdown(
        """
        - **NDVI (Normalized Difference Vegetation Index)**: A measure of green vegetation density from satellite light reflection. Values below 0.20 indicate bare soil, dry residue, or dead vegetation.
        - **Summer Fallow**: Leaving ground unplanted for 14 months between crops to conserve soil moisture. In reality, much of the moisture evaporates, leaving soil exposed to spring winds.
        - **Evapotranspiration (ET)**: The total water transferred from soil and plant leaves into the atmosphere. In Western Kansas, summer ET far exceeds rainfall.
        - **Heat-Stress Days**: Days where high temperatures reach or exceed 35°C (95°F), causing pollination failure in corn and rapid crop moisture stress.
        - **Frost-Free Season**: The continuous period of days between the last spring frost and the first autumn freeze.
        - **Ogallala Aquifer**: The primary underground water reserve in Western Kansas. Withdrawal for irrigation exceeds natural recharge, requiring water-saving rotations.
        """
    )
