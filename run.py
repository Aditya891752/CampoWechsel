"""
Universal One-Command Launcher for Field Shift: Western Kansas.
NASA Space Apps Challenge 2026.
Usage: python run.py
"""
import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    print("=" * 65)
    print("  🌾 FIELD SHIFT: WESTERN KANSAS — LAUNCHER 🌾")
    print("  NASA Space Apps Challenge 2026")
    print("=" * 65)

    # 1. Check data cache
    tidy_file = root / "fieldshift" / "data" / "processed" / "tidy_monthly.csv"
    if not tidy_file.exists():
        print("[!] Preprocessed data cache not found. Running ingestion & harmonization...")
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_power"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_ndvi"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.harmonize"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.engine.indicators"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.engine.scoring"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.engine.evidence"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_smap"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_cdl"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_soils"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_srtm"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.engine.spatial_grid"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_groundwater"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_openet"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_lst"], cwd=str(root), check=True)
        subprocess.run([sys.executable, "-m", "fieldshift.pipeline.fetch_nass_yields"], cwd=str(root), check=True)
        print("[✓] Data lake fully compiled.")
    else:
        print("[✓] Processed offline data lake detected in fieldshift/data/processed/.")

    # 2. Run quick verification audit
    print("\nRunning quick system compliance check...")
    from fieldshift.verify_submission import run_audit
    if not run_audit():
        print("[!] Warning: Verification audit did not return 100%. Check logs.")

    # 3. Launch Streamlit
    print("\nLaunching Streamlit web application at http://localhost:8501...")
    app_path = root / "fieldshift" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], cwd=str(root))

if __name__ == "__main__":
    main()
