"""
Unit tests for Field Shift Command-Line Interface (CLI).
"""
import pytest
from fieldshift.cli import build_parser, cmd_evaluate, cmd_report, cmd_audit


def test_cli_parser_build():
    parser = build_parser()
    assert parser.prog == "fieldshift"


def test_cli_evaluate_thomas(capsys):
    parser = build_parser()
    args = parser.parse_args(["evaluate", "--county", "Thomas", "--water", "0.7"])
    code = cmd_evaluate(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "THOMAS COUNTY" in captured.out
    assert "Wheat w/ legume cover" in captured.out or "Wheat" in captured.out


def test_cli_evaluate_finney(capsys):
    parser = build_parser()
    args = parser.parse_args(["evaluate", "--county", "Finney", "--water", "0.9"])
    code = cmd_evaluate(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "FINNEY COUNTY" in captured.out
    assert "Corn–wheat–sorghum" in captured.out or "Corn" in captured.out


def test_cli_audit(capsys):
    parser = build_parser()
    args = parser.parse_args(["audit"])
    code = cmd_audit(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "PASS" in captured.out


def test_cli_report(tmp_path):
    parser = build_parser()
    out_file = tmp_path / "test_report.html"
    args = parser.parse_args(["report", "--county", "Thomas", "--output", str(out_file)])
    code = cmd_report(args)
    assert code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
