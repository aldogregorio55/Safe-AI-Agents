# DPI — Test Outputs

Outputs from direct prompt injection tests (payload sent as user message).

---

## Folder Structure

```
dpi/
  workflow/      → Full workflow runs (Supervisor → Preparer → Reviewer → Formatter)
  supervisor/    → Supervisor agent isolation runs
  preparer/      → Preparer agent isolation runs
  reviewer/      → Reviewer agent isolation runs
  formatter/     → Formatter agent isolation runs
```

---

## Naming Convention

**Pattern:** `run{NN}-{payload-id}-{target}-{date}.md`  
Add `-safety` suffix for runs with safety prompt active.

Examples:
- `run05-dpi-001-workflow-2026-05-08.md` — workflow run, no safety
- `run01-dpi-001-workflow-safety-2026-05-09.md` — workflow run, safety block active
- `run01-dpi-001-supervisor-2026-05-08.md` — Supervisor isolation run

---

## Prompt Version History

| Runs | Supervisor | Preparer | Reviewer | Formatter | Notes |
|------|-----------|----------|----------|-----------|-------|
| 1–4 (workflow/) | v8 | v9 | v6 | v5 | Non-deterministic — rigid output anchoring competed with jailbreak |
| 5+ (workflow/) | v9 | v9 | v6 | v5 | v9 removes rigid anchoring; expected consistent FAIL |
