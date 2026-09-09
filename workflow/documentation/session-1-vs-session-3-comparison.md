# Workflow Improvement — Session 1 vs Session 3 Comparison

**Project:** `safe-agents` — Pain Point Analysis Workflow
**Platform:** Azure AI Foundry
**Model:** Claude 4.6
**Date:** 2026-05-05

---

## Supervisor

| | Session 1 (original) | Session 3 (establishment) |
|---|---|---|
| **Output** | *"In a live multi-agent system, `transfer_to_preparer` would be invoked here with the full transcript. Since this is a sandbox simulation, please confirm: would you like me to simulate the Preparer agent's output, or are you testing the routing logic only?"* | "Transcript received." |
| **Behaviour** | Meta-commentary, asked clarifying question, referenced SDK tools, offered to simulate other agents | One-line acknowledgement, no commentary |
| **Orchestration bug** | ✅ Present | ❌ Eliminated |

---

## Preparer — Pain Point Identification

| # | Pain Point | Session 1 | Session 3 | Fixed? |
|---|---|---|---|---|
| 1 | Supplier master data manual sync | ❌ N/A | ✅ Y / High | ✅ |
| 2 | No supplier self-service portal | ❌ N/A | ✅ Y / High | ✅ |
| 3 | Supplier inquiries manual routing | ❌ N/A | ✅ Y / High | ✅ |
| 4 | Requisitions not enforced | ❌ N/A | ✅ Y / High | ✅ |
| 5 | POs created retrospectively | ❌ N/A | ✅ Y / High | ✅ |
| 6 | No-PO-no-pay lacks enforcement | ❌ N/A | ✅ Y / High | ✅ |
| 7 | Duplicate PO entry Nexus/Prism | ✅ Y / High | ✅ Y / High | — |
| 8 | Contract management offline | ✅ Y / Medium | ✅ Y / Medium | — |
| 9 | Bank statement manual upload | ❌ N/A | ✅ Y / High | ✅ |
| 10 | No host-to-host banking | ❌ N/A | ✅ Y / High | ✅ |
| 11 | SDM fragmented across teams | ❌ N/A | ✅ Y / High | ✅ |
| 12 | Reporting manual extraction | ❌ N/A | ✅ Y / High | ✅ |
| 13 | No reconciliation tooling | ❌ N/A | ✅ Y / High | ✅ |
| 14 | Clearing account Excel workbooks | ❌ N/A | ✅ Y / High | ✅ |
| 15–20 | (Not discussed in transcript) | ✅ N/A | ✅ N/A | — |

---

## Preparer — Quote Quality

| | Session 1 | Session 3 |
|---|---|---|
| **Quotes provided** | 2 (PP7 and PP8 only) | 14 (all observed items) |
| **Verbatim accuracy** | Unverifiable — Preparer didn't have transcript | All confirmed verbatim from transcript |
| **Grounding** | Likely training-data pattern matching (not grounded in source) | Every quote traceable to specific passage |

---

## Reviewer

| | Session 1 | Session 3 |
|---|---|---|
| **Validation quality** | Rubber-stamped 17 N/As with no per-item reasoning | Systematic per-item check against 3 criteria (quote, observed, score) |
| **Issues caught** | None — approved everything | 2 genuine issues (ellipsis-spliced quotes on PP#10, #11) |
| **Reasoning depth** | "Correct. ✅" for entire batch | Individual justification per pain point with framework rule citation |
| **SDK artefacts** | `transfer_to_preparer` language in prompt | Prompt unchanged but Reviewer operated correctly |

---

## Review Loop

| | Session 1 | Session 3 |
|---|---|---|
| **Loops executed** | 1 (single feedback on PP11, then approved) | 1 (FEEDBACK on #10/#11, then APPROVED) |
| **Feedback quality** | Identified Grace/Rocky attribution issue on PP11 — valid but Preparer couldn't fix (no transcript) | Identified non-contiguous quote splicing — Preparer fixed both |
| **Outcome** | Preparer dropped to N/A (only option without transcript) | Preparer replaced with contiguous verbatim quotes |
| **Loop functional?** | Technically yes, but pointless without data | Genuinely improved output quality |

---

## Formatter

| | Session 1 | Session 3 |
|---|---|---|
| **Produced?** | ❌ No — workflow didn't reach Formatter | ✅ Yes — valid JSON, all 20 items, correct schema |

---

## End-to-End Summary

| Metric | Session 1 | Session 3 | Delta |
|---|---|---|---|
| **Pain points correctly identified** | 2/14 | 14/14 | **+12** |
| **N/A assignments correct** | 6/6 | 6/6 | — |
| **Total observation accuracy** | 8/20 (40%) | 20/20 (100%) | **+60pp** |
| **Score accuracy** | 2/2 (only 2 scored) | 19/20 (PP#10 borderline) | **Full coverage** |
| **Quotes grounded** | No (no transcript access) | Yes (all verbatim) | **Fixed** |
| **Supervisor orchestration** | Broken — simulated pipeline | Clean — one-line ack | **Fixed** |
| **Review loop useful** | No (validating empty data) | Yes (caught real issues) | **Fixed** |
| **JSON output produced** | No | Yes | **Fixed** |
| **End-to-end complete** | No | Yes | **Fixed** |

---

## Root Causes Resolved

| Root Cause | Fix Applied |
|---|---|
| Preparer had no transcript (data delivery failure) | Transcript attached as named provided material in Preparer's vector store |
| Supervisor orchestrated the full pipeline in one response | Prompt rewritten (v2) — isolated stages, anti-simulation rules |
| SDK handoff language caused agents to simulate routing | Removed from Supervisor, pending on Reviewer/Formatter |
| Reviewer validated against empty data | Upstream fix — Preparer now produces real data for Reviewer to validate |

---

## Key Takeaway

**From a non-functional prototype to a fully working pipeline in 2 sessions.** The single biggest fix was infrastructure (transcript in vector store), not prompting — but the Supervisor orchestration bug required a fundamental prompt architecture change from sequential-plan framing to isolated-invocation framing.
