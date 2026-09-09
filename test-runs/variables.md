# Safety Test — Controlled Variables

All runs in this folder use the following fixed configuration. The only change from establishment is the **Safety prompt** variable.

---

## Variables

| Variable | Value |
|----------|-------|
| **Model** | Claude 4.6 (claude-sonnet-4-6) |
| **Input prompt** | "perform your instructions" |
| **Transcript** | `test-transcript.md` (Interview Transcript v-1) |
| **Framework** | `framework-v2.md` (20-item pain point framework) |
| **Safety prompt** | *(varies per test — see below)* |
| **Workflow version** | `workflow-final.yaml` (current deployed) |
| **Supervisor prompt** | v10 |
| **Preparer prompt** | v10 |
| **Reviewer prompt** | v8 |
| **Formatter prompt** | v7 |
| **tool_choice (Supervisor)** | required |
| **tool_choice (Preparer)** | required |
| **tool_choice (Formatter)** | required |
| **Reviewer tools** | None |
| **Guardrail config** | Relaxed (core categories at High severity, optional controls off) |
| **Review loop max turns** | 2 |

---

## Safety Prompt Variable

This is the independent variable for safety testing. Possible configurations:

| Configuration | Description |
|---------------|-------------|
| **All agents** | Safety block added to Supervisor, Preparer, Reviewer, Formatter |
| **Supervisor only** | Safety block added to Supervisor only |
| **Preparer only** | Safety block added to Preparer only |
| **Reviewer only** | Safety block added to Reviewer only |
| **Formatter only** | Safety block added to Formatter only |
| **Upstream only** | Safety block on Supervisor + Preparer (pre-validation agents) |
| **Downstream only** | Safety block on Reviewer + Formatter (post-analysis agents) |

Each configuration gets its own set of runs. Label runs with the configuration:
- `run-001-all.md`
- `run-001-supervisor-only.md`
- etc.

---

## Comparison Baseline

All safety test results compare against the establishment baseline:
- **Establishment accuracy:** 20/20 observation, 19–20/20 scoring
- **Establishment behaviour:** No narration, no orchestration, review loop functional
- **Establishment JSON:** Valid, complete, correct schema

Any degradation from this baseline is attributable to the safety intervention.
