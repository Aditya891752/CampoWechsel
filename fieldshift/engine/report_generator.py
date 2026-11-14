"""
One-Page Farmer Strategy Report Generator for Field Shift: Western Kansas.
Generates an executive, high-contrast, printable HTML/PDF summary report
for consultation with local agronomists and K-State Extension agents.
"""
from pathlib import Path
from typing import Dict, List, Any
import json

from fieldshift.config import COUNTIES, PROCESSED_DATA_DIR, CRITERIA

def generate_html_report(
    county_key: str,
    persona_title: str,
    indicators: Dict[str, Any],
    evidence_cards: List[Dict[str, Any]],
    user_weights: Dict[str, float],
) -> str:
    """Generate high-contrast, publication-grade, printable HTML report."""
    county = COUNTIES[county_key]
    heat_meta = indicators["heat_stress"]
    frost_meta = indicators["frost_risk"]
    rain_meta = indicators["rainfall"]
    soil_meta = indicators["soil_moisture"]
    bare_meta = indicators["ndvi_bare_field"]

    top_card = evidence_cards[0]
    existing_card = next((c for c in evidence_cards if c["is_existing"]), evidence_cards[-1])

    cards_html = ""
    for idx, c in enumerate(evidence_cards, start=1):
        tag = "CURRENT PRACTICE" if c["is_existing"] else f"RANK #{idx}"
        border_style = "border: 2px solid #64748B; background: #F8FAFC;" if c["is_existing"] else "border: 1px solid #CBD5E1; background: #FFFFFF;"
        badge_bg = "#475569" if c["is_existing"] else "#1B5E20"

        ev_list = "".join(f"<li><strong>{e['signal']}</strong> (Source: {e['source']})</li>" for e in c["evidence"])
        ben_list = "".join(f"<li>{b}</li>" for b in c["benefits"])
        gap_list = "".join(f"<li>{g}</li>" for g in c["information_gaps"])
        risk_list = "".join(f"<li>{r}</li>" for r in c["risks_needing_local_review"])

        cards_html += f"""
        <div style="page-break-inside: avoid; margin-bottom: 12px; padding: 12px; border-radius: 4px; {border_style}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 15px; font-weight: bold; color: #0F172A;">{idx}. {c['strategy']}</span>
                <span>
                    <span style="background: {badge_bg}; color: #FFFFFF; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 3px;">Score: {c['score']:.2f} / 5.0</span>
                    <span style="background: #E2E8F0; color: #1E293B; font-weight: 600; font-size: 11px; padding: 2px 6px; border-radius: 3px; margin-left: 6px;">{tag}</span>
                </span>
            </div>
            <p style="margin: 0 0 8px 0; font-size: 13px; color: #334155;">{c['why_suggested']}</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
                <div>
                    <strong style="color: #166534;">Satellite Evidence & Benefits:</strong>
                    <ul style="margin: 4px 0 0 16px; padding: 0;">{ev_list}{ben_list}</ul>
                </div>
                <div>
                    <strong style="color: #991B1B;">Gaps & Risks Needing Local Review:</strong>
                    <ul style="margin: 4px 0 0 16px; padding: 0;">{gap_list}{risk_list}</ul>
                </div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Field Shift Strategy Report — {county['name']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #0F172A;
            background: #FFFFFF;
            margin: 20px;
            padding: 0;
            line-height: 1.4;
        }}
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
        .header {{
            border-bottom: 2px solid #0F172A;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }}
        .banner {{
            background: #EFF6FF;
            border-left: 4px solid #0369A1;
            padding: 8px 12px;
            font-size: 11px;
            color: #1E3A8A;
            margin-bottom: 14px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-bottom: 14px;
        }}
        .metric-box {{
            border: 1px solid #CBD5E1;
            padding: 8px;
            border-radius: 4px;
            background: #F8FAFC;
        }}
        .metric-title {{
            font-size: 11px;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 16px;
            font-weight: bold;
            color: #0F172A;
            margin-top: 2px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div style="float: right; text-align: right; font-size: 12px; color: #64748B;">
            NASA Space Apps Challenge 2026<br>
            Anchor: {county['seat']}, KS ({county['lat']}° N, {county['lon']}° W)
        </div>
        <h1 style="margin: 0; font-size: 20px; color: #0F172A;">Field Shift: Executive Crop-Rotation Report</h1>
        <div style="font-size: 13px; color: #334155; margin-top: 2px;">
            Target System: <strong>{county['name']} — {county['system']}</strong> | Persona: {persona_title}
        </div>
    </div>

    <div class="banner">
        <strong>Mandatory Advisory:</strong> This report highlights satellite-observed patterns from NASA Earth observations 
        and starter K-State Extension trials. It is designed to facilitate informed discussions with local county extension agronomists 
        and certified crop advisers (CCAs); it never replaces on-farm operational judgment.
    </div>

    <div class="metrics-grid">
        <div class="metric-box">
            <div class="metric-title">Bare-Field Duration</div>
            <div class="metric-value">{bare_meta['bare_field_months_count']} Months / Yr</div>
            <div style="font-size: 10px; color: #64748B;">NDVI < {bare_meta['threshold']:.2f} ({', '.join(bare_meta['bare_field_months'][:3])}...)</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Extreme Heat (≥35°C)</div>
            <div class="metric-value">{heat_meta['annual_mean_heat_days']} Days / Yr</div>
            <div style="font-size: 10px; color: #64748B;">Worst year: {heat_meta['worst_heat_year']} ({heat_meta['max_annual_heat_days']} d)</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Frost-Free Window</div>
            <div class="metric-value">{frost_meta['median_frost_free_days']} Days</div>
            <div style="font-size: 10px; color: #64748B;">{frost_meta['median_last_spring_freeze_date']} – {frost_meta['median_first_fall_freeze_date']}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Mean Annual Rain</div>
            <div class="metric-value">{rain_meta['annual_mean_precip_inches']}" ({rain_meta['annual_mean_precip_mm']} mm)</div>
            <div style="font-size: 10px; color: #64748B;">Rainfall CV: {rain_meta['rainfall_variability_cv']} | Max Dry: {rain_meta['max_dry_spell_days']}d</div>
        </div>
    </div>

    <h2 style="font-size: 15px; margin: 0 0 8px 0; border-bottom: 1px solid #CBD5E1; padding-bottom: 4px;">
        Evaluated Crop-Rotation Strategies (Ranked by Multi-Criteria Score)
    </h2>

    {cards_html}

    <div style="margin-top: 14px; padding-top: 8px; border-top: 1px solid #CBD5E1; font-size: 10px; color: #64748B; display: flex; justify-content: space-between;">
        <span>Data Provenance: NASA POWER (Daily 2015–2024), MODIS MOD13Q1, NASA SMAP/MERRA-2, USDA CDL, NRCS SSURGO.</span>
        <span>Generated offline by Field Shift DSS</span>
    </div>
</body>
</html>"""
    return html
