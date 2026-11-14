# Security Policy
### Field Shift: Western Kansas — NASA International Space Apps Challenge

Security, privacy, and credential hygiene are foundational to the Field Shift platform.

---

## 1. Supported Versions

| Version | Supported | Status |
|---|---|---|
| 1.0.x | Yes | Current Release |

---

## 2. Security Protocols & Safeguards

The Field Shift application enforces the following security standards:

1. **Zero Client-Side Secrets**:
   * No API keys, tokens, or credentials exist in frontend code, client templates, or client-delivered JavaScript.
   * All API requests (e.g., optional Google GenAI queries) execute strictly server-side within the Python backend.
2. **Repository Sanitization**:
   * `.env` and local configuration files are explicitly blocked by `.gitignore`.
   * Git history is verified free of credentials, tokens, or sensitive endpoint keys.
3. **Graceful Exception Handling**:
   * Unhandled runtime exceptions and internal system traces are caught cleanly before reaching user interfaces.
   * In the event of network disruption or missing environment variables, the system gracefully shifts to pre-compiled local datasets.

---

## 3. Reporting a Vulnerability

If you discover a potential security vulnerability, credential exposure, or data flaw:

1. Do **NOT** open a public issue.
2. Email the maintainer directly at: `security@fieldshift.local` or contact the repository owner via GitHub private reporting.
3. Include detailed steps to reproduce the vulnerability. We will acknowledge receipt within 48 hours and work on an immediate patch.
