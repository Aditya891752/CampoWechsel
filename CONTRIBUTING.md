# Contributing Guidelines
### Field Shift: Western Kansas — NASA International Space Apps Challenge

Thank you for your interest in contributing to **Field Shift: Western Kansas**. We welcome contributions from data scientists, software engineers, agronomists, and remote sensing specialists.

---

## 1. Engineering Principles & Directives

All contributions must strictly observe the following core principles:

1. **Offline-First Guarantee**:
   * The application must operate 100% offline from `fieldshift/data/processed/`.
   * Remote API calls must have local deterministic or calibrated proxy fallbacks.
2. **Honesty and Data Provenance**:
   * Every dataset row and indicator must carry transparent attribution (`source` and `is_proxy`).
   * Never invent fake numbers, miraculous biological fixes, or unverified claims.
3. **No Credential Leaks**:
   * API keys and credentials must NEVER be placed in client-side code, frontend JavaScript, or committed to git history.
   * Use `.env` or system environment variables with server-side SDKs only.
4. **Farmer-First High-Contrast UI**:
   * Strictly no emojis in headings.
   * Strictly no purple-to-blue gradients, glassmorphism, or low-contrast dark modes.
   * Standard system fonts and clear data visualizations suited for outdoor field tablets.

---

## 2. Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/Aditya891752/Field-Shift.git
cd Field-Shift

# 2. Install dependencies in virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Run the local Streamlit application
python run.py
```

---

## 3. Testing and Pre-Commit Checks

Before submitting a Pull Request, verify that all unit tests and submission criteria pass:

```bash
# 1. Run full test suite
pytest tests/ -v

# 2. Run NASA Space Apps submission audit
python -m fieldshift.verify_submission

# 3. Run data schema validator
python -m fieldshift.cli audit
```

Every PR must maintain a 100% PASS rate across all submission criteria.
