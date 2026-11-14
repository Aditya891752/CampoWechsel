"""
Unit tests for data schema and physical boundary validator.
"""
from fieldshift.engine.schema_validator import (
    validate_tidy_table,
    validate_indicators,
    validate_gemini_dossiers,
    run_full_validation,
)
from fieldshift.config import PROCESSED_DATA_DIR


def test_processed_tidy_table_schema():
    errs = validate_tidy_table(PROCESSED_DATA_DIR / "tidy_monthly.csv")
    assert len(errs) == 0, f"Tidy table schema errors: {errs}"


def test_processed_indicators_schema():
    errs = validate_indicators(PROCESSED_DATA_DIR / "indicators.json")
    assert len(errs) == 0, f"Indicators schema errors: {errs}"


def test_processed_gemini_dossiers_schema():
    errs = validate_gemini_dossiers(PROCESSED_DATA_DIR / "gemini_cell_dossiers.json")
    assert len(errs) == 0, f"Gemini dossiers schema errors: {errs}"


def test_run_full_validation_pass():
    report = run_full_validation()
    assert report["valid"] is True
    assert len(report["errors"]) == 0
