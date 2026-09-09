# Workflow — Pain Point Analysis Pipeline

**Purpose:** Contains the complete Azure AI Foundry workflow build — definitions, agent prompts, platform documentation, build session records, and all test run data for the safety evaluation sandbox.  
**Owner:** Aldo Gregorio  
**Started:** 2026-04-22  
**Last Updated:** 2026-05-19  
**Status:** Establishment complete (v2, 10/10). Safety prompt evaluation not yet started.

---

## LLM Quick Start — What to Load

| Task | Load These Files |
|---|---|
| **Understand the workflow** | `definition/workflow-specification.md` (sequence + agent roles) |
| **Resume build sessions** | `documentation/foundry-build-notes.md` (session index) |
| **Check test results** | `../test-runs/ground-truth-and-validation.md` (ground truth + validation criteria) |
| **Current establishment baseline** | `../test-runs/establishment-tests/establishment-claude-v2/establishment-summary.md` |
| **Agent prompts (current)** | `definition/agents/supervisor.md`, `preparer.md`, `reviewer-v2.md`, `formatter.md` |
| **Platform constraints** | `platform/foundry-reference.md` (guardrails, node types, workflow patterns) |
| **Workflow YAML** | `definition/workflow-final.yaml` (deployed config with Power Fx logic) |

---

## Folder Structure

```
workflow/
  README.md                         ← this file
  foundry-capture.md                  environment capture checklist (anticipated May 15 wipe did not occur; environment remained live)
  test-transcript.md                  anonymised interview transcript (workflow input data)
  kodak_output.txt                    reference workflow output (from Adnan)

  definition/                       ← what the workflow IS
    workflow-specification.md           sequence diagram, agent roles, key rules
    workflow-final.yaml                 deployed YAML with branching + review loop
    framework-v2.md                     20-item pain point framework (ground truth source)
    sandbox-test-workflows.md           original workflow definitions + threat surfaces
    agents/                             agent system prompts (Foundry-deployed)
      supervisor.md                       v10 (current)
      preparer.md                         v10 (current)
      preparer-with-safety.md             treatment variant (safety block injected)
      reviewer-v2.md                      v8 (current)
      formatter.md                        v7 (current)
      archive/                            superseded prompt versions
    schemas/
      output-schema.json                  v1 JSON output schema
      output-schema-v2.json               v2 JSON output schema (current)

  documentation/                    ← how it was BUILT (session records)
    foundry-build-notes.md            ⭐ Session index (Sessions 1–3)
    run-diagnostics-2026-05-04.md       Session 1+2 full diagnostics
    trace-logs-2026-05-05.md            Session 2 trace analysis (guardrail root cause)
    session-1-vs-session-3-comparison.md  improvement delta
    raw-outputs-run-1.md                Session 1 raw agent output
    archive/
      update-status-2026-04-23.md         early status update (superseded)

  platform/                         ← Azure AI Foundry reference
    foundry-reference.md                workflow patterns, node types, agent config, guardrail docs (700 lines)

  src/                              ← local code
    workflow.py                          local workflow build script
```

> **Test run data was relocated to the root-level [test-runs/](../test-runs/) folder on 2026-06-17.** Establishment baselines, safety-testing runs, and injection outputs now live there alongside the DPI/IPI/IAI run outputs that previously lived under `test-data-injections/test-outputs/`.

---

## The Workflow Under Test

A 4-agent supervisor pipeline on Azure AI Foundry that reads an anonymized consultant/client interview transcript and identifies which pain points the client experienced.

```
User Input (transcript)
  │
  ▼
┌─────────────┐
│  Supervisor  │  Router — acknowledges transcript, presents analysis, returns final JSON
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Preparer  │  Analyst — scans transcript against 20-item framework, provides quotes + scores
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Reviewer  │  Validator — checks quote accuracy + score correctness (no transcript access)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Formatter  │  Transformer — converts validated output to JSON schema
└─────────────┘
       │
  Final JSON Output
```

**Review loop:** Reviewer can send FEEDBACK back to Preparer (max 2 turns). Foundry handles routing via `workflow-final.yaml` branching logic.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Reviewer has no transcript access | Scope is logic validation (quote format, scoring rules), not omission detection |
| Prompts reference "next stage" not agent names | Prevents orchestration simulation and injection amplification |
| `<output>` replaces `<handoffs>` | SDK terminology removed — Foundry handles all routing |
| `tool_choice: required` on tool-bearing agents | Ensures file_search is invoked (causes ~30% guardrail flag rate on Claude) |
| Baseline prompts have no `<safety>` section | Control condition — safety block is the independent variable |

---

## Current Agent Versions

| Agent | Version | File |
|---|---|---|
| Supervisor | v10 | `definition/agents/supervisor.md` |
| Preparer | v10 | `definition/agents/preparer.md` |
| Reviewer | v8 | `definition/agents/reviewer-v2.md` |
| Formatter | v7 | `definition/agents/formatter.md` |

---

## Test Run Status

| Batch | Runs | Status | Key Finding |
|---|---|---|---|
| Establishment Claude v1 | 15 | ✅ Archived | Baseline envelope: 12–14 observed, mode 14, temp 0.0 |
| Establishment Claude v2 | 10/10 | ✅ Complete | Re-baselined after major prompt rewrites (v10/v8/v7) |
| Establishment GPT | 0/10 | ❌ Not started | Phase 5 — GPT 5.4 baseline |
| Safety testing — Claude attack present | 0/10 | ❌ Not started | Phase 7 — Lean v5 on Claude Supervisor (isolation + workflow) |
| Safety testing — GPT attack present | 0/10 | ❌ Not started | Phase 8 — Lean v5 on GPT Supervisor (isolation + workflow) |
| Safety testing — False positive | 0/10 | ❌ Not started | Phase 9 — benign runs with Lean v5 (Claude + GPT) |

---

## Platform Constraints (Active)

- **Model:** Claude 4.6 (GPT-5.4 has network error on deployment)
- **Guardrails:** Claude has no configurable guardrails in Foundry — severity cannot be tuned
- **Flag rate:** ~30% on Preparer `file_search` with `tool_choice: required` — manual retry required
- **Azure guardrails:** Flagged benign output but did NOT flag direct prompt injections — unreliable for adversarial detection
- **Environment:** A wipe was anticipated for 15 May 2026 but did not occur — the environment remained live, not redeployed
