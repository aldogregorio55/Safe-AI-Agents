# SPLX × Foundry — Folder Guide

> **Note on naming:** this file is the orientation/context file for this folder (the equivalent of a
> `CLAUDE.md`). It is named `README.md` deliberately — this repo is used across multiple tools
> (Claude Code, GitHub Copilot, others), so all agent-context files in this project are called
> `README.md` rather than a tool-specific name.

**Last updated:** 2026-07-16 (decision reopened — no path chosen yet, pending team meeting; colleague's
React-page idea folded into Option B as sub-path B2)

---

## The Goal

Determine whether **SPLX Probe** (a commercial AI red-teaming / security scanner) can be used to
independently validate the safety of this project's Azure AI Foundry workflow — the 4-agent
**Supervisor → Preparer → Reviewer → Formatter** pain-point-analysis pipeline that is the sole test
harness for the AI Agent Safety project (see the top-level [`../README.md`](../README.md)).

The broader project measures how well the **v6 Safe AI Agents system message block** resists
prompt-injection attacks (DPI / IPI / IAI), scored by F1. SPLX is being evaluated as an external,
automated way to red-team that same workflow — complementary to the manual run-based testing already
completed across Rounds 1–3 (574 runs).

## The Situation (as of 2026-07-16)

> **⏳ Current plan: UNDEFINED — pending a full team meeting.** No path is chosen yet. All options (A–D)
> remain open until the meeting logs a decision. The earlier "Option A first" stance (2026-07-14) is
> reopened and now sits as just one candidate. A colleague's **React-page** idea (2026-07-16) has been
> folded into **Option B** as a sub-path: **B1 = headless proxy**, **B2 = the same proxy + a React
> front-end** that surfaces the workflow calls and drives the OAuth handshake with SPLX and Foundry
> (observability/UX only — it doesn't change what SPLX certifies). See the
> [options map](splx-integration-options-2026-07-14.md) §0 DECISION block for the authoritative status.

**Short version:** SPLX can scan the *model layer* today with zero engineering, but cannot reach the
*full workflow* without a hand-built proxy.

1. **Auth is the blocker (Confirmed, not inferred).** Microsoft's own Feature Support Matrix states
   the Foundry Agents service is **API key: No / Entra ID: Yes**. There is no API-key path into the
   Agents service. Our own captured SDK code confirms the only working invocation is
   `DefaultAzureCredential()` + `responses.create(extra_body={"agent_reference": {...}})`.

2. **SPLX has no fitting connector.** Re-confirmed three times across three dates — SPLX's connector
   list has no Foundry / Workflow Agent connector. Even the closest fit (Azure OpenAI) has no field
   to select a workflow (`agent_reference`), so it fails on two independent grounds: it can't carry
   Entra auth, and it can't route to a workflow.

3. **The same-day, zero-engineering option:** point SPLX's Azure OpenAI connector at the **Claude 4.6
   model deployment** directly. This tests model + system-prompt injection resistance only — **not**
   the orchestration, review loop, HITL approval gate, or JSON-schema enforcement, which is where our
   build sessions found the real failure modes. Any scan report must flag this scope gap explicitly.

4. **Reaching the full workflow** requires SPLX's REST API connector plus a proxy built to the spec
   in the synthesis (Section 4). New blocker identified: the workflow's **HITL Question node will
   stall an automated scan** unless the proxy auto-responds to it.

5. **SPLX's REST connector has a native OAuth form (field shape now confirmed).** The SPLX REST API
   docs (now captured as `.md`) show the OAuth option takes exactly **token URL + Client ID +
   Client Secret + Scope** — a client-credentials flow, matching the Layer-1 Entra auth the synthesis
   said we need (token scoped to `https://ai.azure.com/.default`). This makes the "test OAuth before
   building a proxy" step much more likely to succeed. **Caveat:** OAuth solves *auth* only — the
   workflow still needs the `agent_reference` routing parameter, streamed-event reconstruction, and
   HITL auto-response, which the flat REST payload template may not express. Realistic best case is
   **OAuth for auth + a thin proxy for routing**, not OAuth alone replacing everything.

## Open Operational Questions (resolve before building anything)

- **~~Is the environment live, and at which endpoint?~~ RESOLVED.** The correct target is
  **`tatum-safeagents-resource` / `tatum-safeagents`**. The other endpoint seen in an older capture file
  (`Aldo1` / `AI-Agent-Safety`) is a *separate, unrelated* Foundry project not used for this work — it
  is not a stale/renamed version of the same environment. Use the `tatum-safeagents` values for any
  proxy or scan config. (Liveness itself should still be sanity-checked via Azure Portal / `az` CLI
  immediately before a scan run, but the address ambiguity is closed.)
- **Can SPLX's REST connector OAuth option do a full client-credentials flow?** *Partially answered:*
  the SPLX REST API doc confirms the OAuth form has the right **fields** (token URL, Client ID, Client
  Secret, Scope). Still untested: whether SPLX sends the request in the exact form Entra expects
  (`grant_type=client_credentials`, form-encoded) and whether the flat REST payload can carry the
  `agent_reference` workflow-routing parameter. Cheap to test; do this before any proxy build.

## Files in This Folder

| File | What it is |
|---|---|
| [`research-synthesis-splx-foundry-workflow-agent-2026-07-14.md`](research-synthesis-splx-foundry-workflow-agent-2026-07-14.md) | ⭐ **Current** — gap-closure synthesis. Auth analysis (2 layers), concrete proxy spec (§4), model-only scope table (§5), open questions (§6), recommended path (§7). |
| [`splx-integration-options-2026-07-14.md`](splx-integration-options-2026-07-14.md) | ⭐ **Options map** — all four ways to connect SPLX to the workflow (A REST+OAuth direct, B thin proxy, C SPLX Proxy Interface, D SDK recreation), with the auth thread, fidelity lens, and the two decision questions. Start here when weighing options. |
| [`option-a-requirements-checklist.md`](option-a-requirements-checklist.md) | **Checklist for Option A** (one *candidate* path, not the decided one — decision is pending). Tick-off requirements to execute Option A if chosen: 14 items marked self 🟢 / help 🔴, the single admin ask, the SPLX OAuth field mapping, and the open risks to watch. |
| [`SPLX - REST API - AI Security Docs.md`](SPLX%20-%20REST%20API%20-%20AI%20Security%20Docs.md) | ⭐ **New** — SPLX's REST API connector docs as markdown (verbatim from the PDF). Documents the OAuth form (token URL / Client ID / Client Secret / Scope), payload placeholders (`{message}`, `{session_id}`), Response Path, session management, and the SPLX Proxy Interface. |
| `SPLX - REST API - AI Security Docs.pdf` | Original PDF of the above (primary source). |
| `archive/research-analyst-splx-foundry-integration-verified-2026-07-13.md` | Prior verification pass — still valid for the model-deployment layer; baseline for connector list and general auth framing. |
| `archive/splx-foundry-handoff-pack-2026-07-13.md` | Prior practitioner handoff pack — model-vs-agent two-surface framing. |

## Recommended Next Steps

> **First: hold the decision meeting.** The steps below assume Option A; they only apply if the meeting
> selects it. If Option B/C/D/E is chosen, the relevant build spec (options map §3, synthesis §4) governs
> instead. Steps 1–2 (endpoint liveness) are useful regardless of which option wins.

1. Confirm the target environment is live and pin the correct endpoint (open question 1).
2. Test the REST connector's OAuth option before hand-building the proxy — the OAuth field shape is
   now confirmed to fit an Entra client-credentials flow, so plug in the tenant token endpoint,
   service-principal Client ID/Secret, and scope `https://ai.azure.com/.default` and see if auth
   succeeds.
3. Only if needed (or if OAuth solves auth but not `agent_reference` routing / HITL), build the proxy
   to the synthesis §4 spec (including HITL auto-response handling).
