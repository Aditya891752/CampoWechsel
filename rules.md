# AI Engineering & Security Governance Rules (rules.md)
## Project: Field Shift — Western Kansas
**Scope**: Binding rules, constraints, and security directives for all AI models, agents, and contributors working on this codebase.

---

### 1. Fundamental Behavioral Directives
1. **Never Fabricate Data**: Under no circumstances should any synthetic or hallucinated scientific values be introduced. If an API is inaccessible, use the documented proxy fallback and explicitly tag it in the UI and data tables (`is_proxy = True`).
2. **Offline-First Integrity**: The web interface must run entirely from local cached tables in `data/processed/`. Never introduce runtime network calls from UI rendering components.
3. **Transparent Scientific Scoring**: No black-box or unexplained scoring weights. Every score calculation must be traced back to `ratings/strategies.json` and explicit formulas in `engine/scoring.py`.
4. **Humility & Local Validation**: Always present the persistent disclaimer: *"This tool highlights patterns and options. It does not replace your judgment or advice from local agronomists and extension staff."*

---

### 2. Strictly Prohibited Visual & UX Anti-Patterns
To ensure the application feels like a rugged, practical, accessible agricultural decision-support tool rather than a generic tech-startup template, the following styling and interaction patterns are **strictly prohibited**:

1. **NO Purple-to-Blue Gradients**: Never use cliché tech-startup gradient backgrounds or fills.
2. **NO Gradient Hero Text**: All typography must use solid, high-contrast colors.
3. **NO Emojis in Headings**: Keep headings clean, semantic, and professional.
4. **NO Inter Font Everywhere**: Avoid generic default typography stacks; use clear, readable, standard system typography optimized for high legibility in bright sunlight.
5. **NO Colored Border Cards**: Do not use neon or arbitrary colorful borders around cards. Use clean, subtle, high-contrast borders or structural contrast.
6. **NO Glassmorphism**: No semi-transparent frosted-glass effects (`backdrop-blur`) that degrade readability.
7. **NO Low-Contrast Dark Mode**: Avoid washed-out grays and unreadable dark themes. Prioritize high-contrast, sunlight-readable clarity.
8. **NO Three Icon Boxes in a Row**: Avoid generic landing page feature triplets. Use purposeful data tables, metric summaries, and structured cards.
9. **NO Badges Above Headlines**: Do not use decorative "pill" badges floating above main section titles.
10. **NO Lucide/Generic Icons Everywhere**: Restrict icons to clear, intuitive functional utilities. Never decorate every label with an icon.
11. **NO Untouched Shadcn UI Clones**: No lazy, default copy-pasted component styling without purpose.
12. **NO Fade-in on Scroll / Scrolljacking**: Present all critical data immediately without sluggish scroll triggers.
13. **NO Cursor-Following Beams / Particles**: Zero superfluous visual animations or pointer effects.
14. **NO Button Fades on Hover**: Buttons must provide instant, crisp, deterministic feedback (e.g., standard color change or tactile border).
15. **NO Inconsistent Spacing**: Adhere to a strict 4px / 8px grid system for margins and padding.
16. **NO Em Dashes Everywhere**: Avoid excessive prose ornamentation; write direct, punchy, clear agricultural English.
17. **NO Generic Passwords / Placeholders**: Never leave mock credentials like `admin/admin` or `password123`.
18. **NO Serif Italic Accents**: Keep technical and agricultural data clean and unpretentious; avoid decorative italicized serif styling.
19. **NO Space Grotesk + Instrument Serif Typography Pairs**: Avoid pretentious boutique font pairings that impair quick field scanning.
20. **NO Grain Over Gradients**: No simulated noise or grainy overlays.

---

### 3. Comprehensive Security Directives
All code contributions must strictly adhere to the following twelve security mandates:

1. **No API Keys or Secrets in Frontend or Client JS**: Never expose API keys, Bearer tokens, or credentials in client bundles, Streamlit session states rendered client-side, or static JS.
2. **No .env or Config Files Exposed Publicly or Committed**: All `.env`, local credential caches, and secret files must be explicitly ignored in `.gitignore`.
3. **No Secrets Anywhere in Git History**: Ensure Git history is scrubbed and pre-commit hooks verify that no private keys or tokens enter commits.
4. **No Overly Permissive Database Rules**: If using Supabase, Firebase, or external stores, Row-Level Security (RLS) must be strictly enforced. World-readable or world-writable tables are forbidden.
5. **No Public Storage Buckets**: S3, GCS, or Firebase storage buckets holding project data must not allow anonymous public read/write access.
6. **Mandatory Rate Limiting on External Ingestion APIs**: Implement client-side throttling and exponential backoff to avoid IP bans or exhausting NASA Earthdata and USGS quotas.
7. **No Debug Mode or Developer Tools Enabled in Production**: Disable development debug panels, verbose traceback exposure, and unsafe reload flags in deployment configs.
8. **No Unauthenticated Admin / Data Mutation Routes**: Any pipeline triggers or data reload endpoints must be secured behind authentication.
9. **Zero SQL or Injection Vulnerabilities**: All database queries and file lookups must use parameterized statements or sanitized paths. Never interpolate user strings into queries.
10. **No Plaintext or Weakly Hashed Passwords**: If user authentication is added, utilize modern salted password hashing (Argon2id or bcrypt with appropriate cost factor).
11. **No Stack Traces or Internal Errors Shown to End Users**: Intercept runtime exceptions gracefully; display friendly, actionable error messages and log stack traces internally to secure logs.
12. **No Client-Side-Only Auth or Validation**: Security checks, input sanitization, and permission validation must always execute server-side.

---

### 4. The Three Highest-Risk Fixes (Addressed First)

In accordance with priority risk management, the following three highest-risk security and operational vulnerabilities must be addressed before any production deployment:

#### 1. Risk #1: Credential Exposure in Code & Git History (Direct Breach Vector)
- **Threat**: Hardcoding NASA Earthdata credentials, API tokens, or local paths into scripts like `config.py` or `.env` and committing them to version control.
- **Immediate Fix**:
  - Add `.env`, `credentials.json`, `*.pem`, `data/raw/` secrets, and temporary cache directories to `.gitignore` immediately.
  - Load environment variables exclusively through `os.getenv()` or a secure configuration loader.
  - Implement a pre-commit verification script to scan for key patterns (`AKIA...`, Bearer tokens, passwords).

#### 2. Risk #2: Unsanitized File Path Manipulation & Injection (Remote File Disclosure / Overwrite)
- **Threat**: Accepting county names, dataset identifiers, or filenames from user inputs or query parameters and concatenating them directly into filesystem paths (e.g., `open(f"data/{user_input}.csv")`).
- **Immediate Fix**:
  - Restrict county names and variables to a strict, hardcoded whitelist defined in `config.py`.
  - Validate all path resolution using `pathlib.Path.resolve()` and verify that the target path remains strictly within the intended `data/processed/` directory.

#### 3. Risk #3: Internal Stack Trace & Server Information Disclosure (Reconnaissance Risk)
- **Threat**: Allowing unhandled exceptions during API failures or data parsing to output raw Python tracebacks, internal file directories, and library versions directly onto the user-facing Streamlit UI.
- **Immediate Fix**:
  - Wrap all data loaders and scoring routines in explicit `try/except` blocks.
  - Display standardized user-friendly error banners (e.g., *"Data temporarily unavailable for this selection. Displaying verified regional fallback."*).
  - Pipe raw tracebacks to local internal logging files (`sys.stderr` or local log files) rather than `st.exception()`.
