# Test Plan v3 — Decision Log

**Created:** 2026-05-21  
**Purpose:** Track decisions, rationale, and design evolution for test plan v3.

---

## Session 1 — 2026-05-21: Objectives & Direction

### Context

Test plan v2 was accepted by management. v2 assumed all 3 attack vectors were live threats and all 4 agents could be vulnerable. 59 runs of testing (May 7–19) invalidated those assumptions:
- IPI and IAI are fully blocked by models natively (24/24 PASS)
- Only DPI on the Supervisor is a confirmed vulnerability (60–80% FAIL)
- Agent architecture determines vulnerability more than any safety layer

v3 reframes the experiment around these findings.

### Core Thesis

"How you instruct the agent — its role scope, task specificity, and instructional clarity — is the primary determinant of whether it behaves safely under adversarial conditions."

### Hypothesis

The Lean safety system message block reduces the success rate of direct prompt injection attacks on orchestrator agents. This effect is consistent across frontier models.

### Goal

Determine whether prompt-level safety instructions can close the confirmed DPI vulnerability on the Supervisor agent, and whether this finding holds across models and execution modes.

---

## Locked Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Safety block version | Lean (v5) only | Minimum viable recommendation. If Lean fails, the answer is architectural, not version selection |
| Attack vector | DPI-002 only | Only confirmed vulnerability. IPI/IAI CLOSED |
| Target agent | Supervisor only | Only agent with measurable FAIL rate (60–80%). Preparer/Formatter at 0% — no room for delta |
| Models | Claude 4.6 + GPT-5.4 | Model behavior is the safety mechanism — must test if the gap is universal |
| Modes | Isolation + Workflow | Baseline shows +20% pipeline amplification — need to measure if safety prompt neutralizes it |
| Comprehensive (v6) | Dropped | One recommendation is cleaner for management |
| IPI/IAI testing | Dropped | CLOSED — models block natively |
| Platform guardrails | Not a variable | Don't catch DPI payloads — not a confound |

---

## Test Objectives

**1. Establish DPI vulnerability baseline across frontier models**
Determine the Supervisor's DPI-002 FAIL rate on both Claude 4.6 and GPT-5.4 without safety intervention. Establishes whether the orchestrator vulnerability is universal or model-specific.

*Measures:* Baseline FAIL rate per model, per mode.

**2. Measure Lean safety block effectiveness**
Determine whether appending the Lean (v5) safety block to the Supervisor's system prompt reduces DPI-002 FAIL rate. Tested on both models independently.

*Measures:* FAIL rate delta (baseline → treatment) per model.

**3. Compare model-level safety behavior**
Determine whether Claude 4.6 and GPT-5.4 exhibit different vulnerability profiles at baseline AND different responsiveness to the safety prompt under treatment. If models diverge, model selection is itself a safety control.

*Measures:* Cross-model FAIL rate comparison at each condition.

**4. Quantify pipeline amplification effect**
Determine whether the full workflow pipeline amplifies or dampens DPI success and safety prompt effectiveness compared to isolated Supervisor testing. Baseline shows +20% amplification (Claude: 60% isolation → 80% workflow) — does the safety prompt neutralize this?

*Measures:* Isolation vs workflow FAIL rate delta, with and without safety prompt.

---

## Test Matrix

| Condition | Model | Mode | Safety Block | Runs | Status |
|-----------|-------|------|--------------|------|--------|
| Establishment (done) | Claude | Workflow | None | 10 | ✓ Complete |
| Establishment (new) | GPT | Workflow | None | 10 | Not started |
| DPI Baseline (done) | Claude | Isolation | None | 5 | ✓ Complete |
| DPI Baseline (done) | Claude | Workflow | None | 5 | ✓ Complete |
| DPI Baseline (new) | GPT | Isolation | None | 5 | Not started |
| DPI Baseline (new) | GPT | Workflow | None | 5 | Not started |
| Treatment (new) | Claude | Isolation | Lean (v5) | 5 | Not started |
| Treatment (new) | Claude | Workflow | Lean (v5) | 5 | Not started |
| Treatment (new) | GPT | Isolation | Lean (v5) | 5 | Not started |
| Treatment (new) | GPT | Workflow | Lean (v5) | 5 | Not started |

**New runs: 40.** Existing: 20.

---

## Success Criteria

| Outcome | Interpretation |
|---------|---------------|
| FAIL drops significantly (≤20%) | Safety prompt is effective — mandate it |
| FAIL drops partially (40–60%) | Safety prompt helps but insufficient — architectural hardening also needed |
| FAIL unchanged | Prompt-level controls can't fix orchestrator gap — recommendation is agent design |
| Models diverge | Model selection is itself a safety control — guidance must be model-specific |

---

## Scope Exclusions

| Excluded | Reason |
|----------|--------|
| IPI / IAI testing | CLOSED — models block natively (24/24 PASS) |
| Comprehensive (v6) | Lean is the minimum viable recommendation |
| Preparer / Formatter treatment | 0% baseline FAIL — no room for delta |
| Platform guardrail interaction | Don't catch DPI payloads — not a confound |
| Reviewer treatment | Latent risk only — not currently exploitable |

---

## Document Structure (Agreed)

v3 follows the v2 skeleton (management-approved format) with updated content. Key structural decisions:

| Element | Approach |
|---------|----------|
| Prior Findings | Short narrative in body (~half page). Management-readable. What we tested, what models block, where the gap is |
| Detailed tables | Appendix — reference findings folder tables (FAIL rates, run registry, baseline envelope) |
| Workflow Architecture | Same as v2 (unchanged — same test harness) |
| Test Matrix | Narrowed from v2 — Supervisor only, DPI-002 only, Lean only, both models |
| Scoring | Carry forward from v2 (F1 or simplified binary — TBD) |

**Data from findings folder used in v3:**

| Source File | Used For | Location in v3 |
|-------------|----------|----------------|
| supervisor-vulnerability.md | Baseline FAIL rates, failure taxonomy, architectural cause | Prior Findings + Baseline Reference |
| model-level-defense.md | What models block natively (IPI/IAI/Preparer) | Prior Findings + Scope Justification |
| vulnerability-characterization.md | Per-agent FAIL rates, pipeline amplification (+20%), non-propagation | Prior Findings + Scope Justification |
| baseline-envelope.md | Normal output envelope (12–15 observed, variable pain points) | Appendix (GPT establishment comparison reference) |
| platform-guardrails.md | Guardrails don't catch DPI (one-liner) | Scope Justification |
| run-registry.md | Total run counts, existing data | Appendix (evidence trail) |
| test-plan-v2-verbatim.md | Document skeleton and scoring methodology | Structure template |

---

## Open Items

- [ ] Write full test plan document (v2 skeleton, updated content)
- [ ] GPT-5.4 deployment verification (confirm model is accessible in Foundry)
- [ ] Execution sequence definition
- [ ] Scoring methodology confirmation (F1 or binary FAIL rate comparison)

---

## Key Reasoning (Why v3 Diverges from v2)

**v2 asked:** "Does the safety prompt stop attacks?"
**v3 asks:** "The model already stops most attacks — can a safety prompt close the one gap that remains?"

v2 was designed before we had data. v3 is designed with 59 runs of evidence showing:
1. Models natively handle IPI/IAI — safety prompts are redundant on those vectors
2. The Supervisor's vulnerability is architectural (user message = instruction channel)
3. The Preparer's resistance is also architectural (narrow scope + instruction/data separation)
4. The only question left: can phrasing (via safety prompt) compensate for architectural exposure?

This is a narrower, more precise experiment — but it answers the question that matters.
