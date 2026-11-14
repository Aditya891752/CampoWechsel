"""
Command-Line Interface (CLI) for Field Shift: Western Kansas.
Allows headless execution of agronomic evaluations, reports, and data audits.
"""
import argparse
import json
import sys
from pathlib import Path

from fieldshift.config import COUNTIES, PERSONAS, PROCESSED_DATA_DIR
from fieldshift.engine.scoring import score_strategies, map_3_slider_to_criteria_weights
from fieldshift.engine.evidence import generate_evidence_cards
from fieldshift.engine.report_generator import generate_html_report
from fieldshift.engine.schema_validator import run_full_validation


def cmd_evaluate(args) -> int:
    """Evaluate crop rotation rankings for a specific county."""
    county = args.county.capitalize()
    if county not in COUNTIES:
        print(f"Error: Unknown county '{args.county}'. Supported: Thomas, Finney", file=sys.stderr)
        return 1

    weights = map_3_slider_to_criteria_weights(
        save_water=args.water,
        protect_soil=args.soil,
        earn_income=args.income,
    )

    with open(PROCESSED_DATA_DIR / "indicators.json", "r", encoding="utf-8") as f:
        indicators = json.load(f)[county]

    ranked = score_strategies(county, indicators, weights=weights)

    print("=" * 68)
    print(f"FIELD SHIFT: AGRONOMIC ROTATION EVALUATION — {county.upper()} COUNTY")
    print(f"Priority Sliders: Water={args.water:.2f}, Soil={args.soil:.2f}, Income={args.income:.2f}")
    print("=" * 68)
    print(f"{'Rank':<6} {'Score':<8} {'Existing':<10} {'Crop Rotation Strategy'}")
    print("-" * 68)
    for idx, strat in enumerate(ranked, start=1):
        existing_str = "[BASELINE]" if strat.get("is_existing_rotation") else ""
        print(f"#{idx:<5} {strat['score']:<8.2f} {existing_str:<10} {strat['name']}")
    print("=" * 68)
    return 0


def cmd_report(args) -> int:
    """Generate offline executive HTML strategy report."""
    county = args.county.capitalize()
    if county not in COUNTIES:
        print(f"Error: Unknown county '{args.county}'. Supported: Thomas, Finney", file=sys.stderr)
        return 1

    with open(PROCESSED_DATA_DIR / "indicators.json", "r", encoding="utf-8") as f:
        indicators = json.load(f)[county]

    with open(PROCESSED_DATA_DIR / "evidence.json", "r", encoding="utf-8") as f:
        cards = json.load(f)[county]

    persona_key = "dryland_wheat" if county == "Thomas" else "irrigated_corn"
    persona_title = PERSONAS[persona_key]["title"]

    weights = {"water": 0.5, "soil": 0.3, "income": 0.2}
    html = generate_html_report(county, persona_title, indicators, cards, weights)

    out_path = Path(args.output)
    out_path.write_text(html, encoding="utf-8")
    print(f"Executive HTML report written to: {out_path.resolve()}")
    return 0


def cmd_audit(args) -> int:
    """Run data integrity and schema validation checks."""
    res = run_full_validation()
    print(f"Data Schema Validation: {'PASS' if res['valid'] else 'FAIL'}")
    print(f"Details: {res['summary']}")
    return 0 if res["valid"] else 1


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI commands."""
    parser = argparse.ArgumentParser(
        prog="fieldshift",
        description="Field Shift CLI: Agronomic decision-support powered by NASA Earth Observations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Score and rank crop rotations for a county.")
    eval_parser.add_argument("--county", "-c", required=True, choices=["Thomas", "Finney", "thomas", "finney"])
    eval_parser.add_argument("--water", type=float, default=0.5, help="Water saving priority (0.0 to 1.0)")
    eval_parser.add_argument("--soil", type=float, default=0.5, help="Soil protection priority (0.0 to 1.0)")
    eval_parser.add_argument("--income", type=float, default=0.5, help="Income preservation priority (0.0 to 1.0)")

    # report command
    rep_parser = subparsers.add_parser("report", help="Generate executive HTML report for a county.")
    rep_parser.add_argument("--county", "-c", required=True, choices=["Thomas", "Finney", "thomas", "finney"])
    rep_parser.add_argument("--output", "-o", default="fieldshift_report.html", help="Output path for HTML report")

    # audit command
    subparsers.add_parser("audit", help="Run dataset schema and physical boundary integrity audit.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "evaluate":
        return cmd_evaluate(args)
    elif args.command == "report":
        return cmd_report(args)
    elif args.command == "audit":
        return cmd_audit(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
