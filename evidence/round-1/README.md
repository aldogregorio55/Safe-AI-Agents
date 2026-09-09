# Evidence — Structured Test Results

**Created:** 2026-05-18  
**Last Updated:** 2026-05-27  
**Purpose:** Centralized, citable evidence from prompt injection testing — separated from session narratives and raw outputs.

---

## Why This Folder Exists

Testing ran from May 7–19 across 59 active runs (establishment v1 archived, DPI-001 discarded), 3 attack vectors, 2 models, and 5 session notes. The raw data lives in `test-runs/` and the chronological narrative lives in `session-notes/`. But when writing the test plan v3 or briefing stakeholders, you need **structured findings** — not session history.

This folder extracts the conclusions from the testing period into clean, standalone evidence files:

| File | What It Answers | Use It For |
|------|----------------|------------|
| [model-level-defense.md](model-level-defense.md) | What does the model block without a safety prompt? | Test plan v3 "what are we testing?" framing |
| [supervisor-vulnerability.md](supervisor-vulnerability.md) | Where does the model fail, how badly, and what does failure look like? | Safety prompt evaluation design, Supervisor hardening |
| [vulnerability-characterization.md](vulnerability-characterization.md) | How does each agent respond to DPI? Per-agent risk profile | Full attack surface analysis, Reviewer latent risk, measurement baseline decisions |
| [baseline-envelope.md](baseline-envelope.md) | What does the workflow produce normally? (ground truth + variance) | Comparison baseline for all test results |
| [platform-guardrails.md](platform-guardrails.md) | What do Azure guardrails actually do? (model block vs platform block) | Disambiguating test results, platform limitation documentation |
| [run-registry.md](run-registry.md) | What did we actually run? (every run, one table) | Evidence trail, run counts, coverage checks |

---

## Relationship to Other Folders

```
AI Agent Safety/
  evidence/              ← YOU ARE HERE — structured conclusions (citable)
  presentation/          ← engineering showcase materials (moved out of evidence/)
  test-runs/             ← Raw agent outputs per run (raw data) — root-level
    establishment-tests/   establishment baselines (v1, v2, gpt)
    safety-testing/        Round 2 safety prompt evaluation
    dpi/ ipi/ iai/         injection run outputs
  test-data-injections/  ← Payload sources + chronological session notes
    session-notes/         injection-testing session narratives
    ipi/ dpi/ iai/         payload source files
```

**Data flows up:**
- `test-runs/` (raw) → `test-data-injections/session-notes/` (interpreted) → `evidence/` (structured)

**Nothing is duplicated.** Evidence files reference session notes and raw outputs but don't repeat run-by-run detail. If you need the full narrative, go to `test-data-injections/session-notes/injection-testing-summary.md`. If you need a specific agent output, go to `test-runs/{vector}/{payload}/`.

---

## Status

| File | Status |
|------|--------|
| model-level-defense.md | Current (2026-05-21) |
| supervisor-vulnerability.md | Current (2026-05-21) |
| vulnerability-characterization.md | Current (2026-05-21) |
| baseline-envelope.md | Current (2026-05-21) |
| platform-guardrails.md | Current (2026-05-18) |
| run-registry.md | Current (2026-05-25) — 59 active runs |

---

## When to Update

Update these files when:
- New test runs are completed (add to run-registry, update evidence if conclusions change)
- Safety prompt evaluation runs begin (will need a new evidence file or section)
- v3 test plan objectives and design decisions live in `planning/v3/`
