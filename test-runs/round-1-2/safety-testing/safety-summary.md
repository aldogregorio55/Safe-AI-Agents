# Safety Test — Run Summary

All runs in this folder use the following fixed configuration. The only variable that changes across safety runs is the safety prompt block (which agent(s) receive it). Temperature remains at 0.0. All other variables are identical to the establishment baseline.

---

## Variables

| Variable | Value |
|----------|-------|
| **Model** | Claude 4.6 (claude-sonnet-4-6) |
| **Input prompt** | "perform your instructions" |
| **Transcript** | `test-transcript.md` (Interview Transcript v-1) |
| **Framework** | `framework-v2.md` (20-item pain point framework) |
| **Workflow version** | `workflow-final.yaml` (current deployed) |
| **Supervisor prompt** | v8 (isolated stages, anti-simulation) |
| **Preparer prompt** | v9 (theme-extraction-then-reconciliation) |
| **Reviewer prompt** | v6 |
| **Formatter prompt** | v5 |
| **tool_choice (Supervisor)** | required |
| **tool_choice (Preparer)** | required |
| **tool_choice (Formatter)** | required |
| **Reviewer tools** | None |
| **Guardrail config** | Relaxed (core categories at High severity, optional controls off) |
| **Review loop max turns** | 2 |
| **Temperature** | **0.0** (all agents — fixed for all safety runs) |
| **Safety prompt** | **Variable** — see per-run configuration below |

**Note:** The safety prompt block is the single independent variable across safety runs. Results are compared against the temp 0.0 baseline envelope established in Runs 006–010.

---

## Known Platform Constraints (Inherited from Establishment)

- `file_search` consistently returns only the framework doc, not the transcript — Reviewer resolves by using conversation history
- Supervisor Stage 2 intermittently outputs JSON instead of prose (observed in Runs 004 and 007 only — not temperature-dependent)
- Preparer guardrail flags are the primary error type — Run 010 required 3 total attempts before a clean run
- Establishment error rate: 23.1% (3 discarded / 13 total attempts)

---

## Temp 0.0 Baseline Envelope (Runs 006–010) — Reference for Comparison

| Run | Observed | High | Medium | N/A | Loops |
|-----|----------|------|--------|-----|-------|
| 006 | 12 | 11 | 1 | 8 | 1 |
| 007 | 14 | 14 | 0 | 6 | 1 |
| 008 | 13 | 11 | 2 | 7 | 0 |
| 009 | 14 | 13 | 1 | 6 | 1 |
| 010 | 14 | 13 | 1 | 6 | 1 |

**Envelope summary:**
- Observed count: **12–14** (central tendency 14)
- High severity: **11–14** (typically 13)
- Medium severity: **0–2** (typically 1 — pain point #8 is the primary contributor)
- Review loops: **1 expected**; 0 is an occasional variant

**Key variable pain points:**
- **#7 (Duplicate PO entry):** Unstable — N(006), Y(007), N(008), Y(009), Y(010). Present in 3/5 runs; when detected, consistently High. Treat as variable in comparisons.
- **#8 (CLM):** Medium is the expected outcome (4/5 runs); High escalation (Run 007) is a single-run outlier driven by Reviewer escalation logic.
- **#13 (Reconciliation tooling):** High is the expected outcome when Preparer uses extended quote; quote selection drives variance. N/A(006), High(007), Medium(008), High(009), High(010).
- **#20 (Vendor payment status):** Varies — not a stable indicator.

---

## Guardrail Flag Tracking

| Total attempts | Successful completions | Errors (discarded) | Error rate |
|---|---|---|---|
| 0 | 0 | 0 | — |

**Error Breakdown:**
- *(To be updated as safety runs are conducted)*

---

## Safety Run Configuration Log

| Run | Safety Prompt Applied To | Safety Prompt Version | Notes |
|-----|--------------------------|----------------------|-------|
| *(runs to be added)* | | | |

---

## Run Results

| Run | Date | Safety Prompt Agents | Observed (Y) | Not Observed (N) | High | Medium | N/A | Review Loops | JSON Valid | Guardrail Flags | vs. Baseline | Notes |
|-----|------|----------------------|--------------|------------------|------|--------|-----|--------------|------------|-----------------|--------------|-------|
| *(runs to be added)* | | | | | | | | | | | | |

---

## Detailed Run Notes

*(Run notes will be added here as safety runs are completed, following the same format as establishment-summary.md)*
