# Scientific Method — Running Tracker

> Personal side note. Not a deliverable. Tracks whether the testing approach stays scientifically sound.

---

## Current Position: Experiment Design (in progress)

| Step | Status | Note |
|---|---|---|
| **Observation** | ✅ Done | Prompt-level safety controls exist but are untested against real multi-agent workflows |
| **Question** | ✅ Done | Does the safety add-on actually reduce attack success in a multi-agent system? |
| **Hypothesis** | ✅ Done | Injecting the safety prompt into agent instructions will significantly reduce the rate of successful adversarial attacks (measured by improved recall) compared to the same system without it, without meaningfully degrading task performance |
| **Experiment Design** | 🟡 In progress | Conditions A/B/C/D, two test levels, controlled variables, binary classification, F1 scoring framework chosen (specifics deferred) |
| **Run Experiment** | ⏳ Blocked | Needs platform access + team approval of strategy |
| **Analysis** | Not started | |
| **Conclusion** | Not started | |

---

## Soundness Checks

Log anything that risks being scientifically unsound — confounds, premature conclusions, untested assumptions.

| Date | Flag | Resolution |
|---|---|---|
| 2026-04-13 | Need benign test cases (Condition A + D), not just attacks — otherwise no way to measure precision or false positive cost | Built into eval matrix as Conditions A and D |
| 2026-04-13 | Platform guardrails could confound prompt-level results if not kept neutral | Scope decision: platform guardrails intentionally neutral, prompt-only evaluation |
| 2026-04-13 | "Partial" outcomes would muddy binary classification — could introduce scorer bias | Decision: force binary (partial = fail), bring up for team discussion |
| | | |
