# Option B Technical Execution Map — SPLX × `tatum-safeagents` Proxy

**Date:** 2026-07-16
**Scope:** Option B only (**B1 headless proxy** + what **B2 React front-end** adds). Options A, C, D are
out of scope for this document.
**Status of the underlying decision:** UNDEFINED, pending a full team meeting. Nothing here is a build
authorization — this is a map to study *if/when* Option B is chosen. See
[`splx/README.md`](../splx/README.md) and
[`splx/splx-integration-options-2026-07-14.md`](../splx/splx-integration-options-2026-07-14.md) §0 for
the authoritative decision status.
**Grounded in:** [research synthesis §4](../splx/research-synthesis-splx-foundry-workflow-agent-2026-07-14.md#4-concrete-proxy-spec-for-scanning-safe-agents-specifically),
[option-a-requirements-checklist.md](../splx/option-a-requirements-checklist.md),
[foundry-docs-option-a-findings-2026-07-15.md](../splx/foundry-docs-option-a-findings-2026-07-15.md),
[SPLX REST API docs](../splx/SPLX%20-%20REST%20API%20-%20AI%20Security%20Docs.md). Values not directly
sourced from these are labeled **[unverified]**.

---

## 1. What gets built

### 1.1 B1 — headless proxy (the core)

A single small web service, written with the Azure SDK, sitting between SPLX and the real deployed
`tatum-safeagents` / `safe-agents` workflow. It exposes a handful of plain HTTP endpoints; SPLX's REST
API connector talks to it exactly as it would talk to any chatbot backend. Internally, the proxy does
the entire Foundry "dance" (Section 2) and hides it behind flat JSON in/out.

**Components:**

| Component | Responsibility |
|---|---|
| **Auth module** | Acquires and refreshes an Entra token via `DefaultAzureCredential` (backed by a service-principal `ClientSecretCredential` in non-interactive/server contexts). Scope: `https://ai.azure.com/.default`. |
| **Foundry client wrapper** | Wraps `AIProjectClient` + the OpenAI-compatible client (`conversations.create`, `responses.create`, `conversations.delete`) against the `tatum-safeagents` project endpoint. |
| **Session map** | In-memory (or Redis, if the proxy is multi-instance) mapping a proxy-issued `session_id` → the real Foundry `conversation.id`. This is the piece that resolves the Option A blocker (Section 3.3). |
| **HITL auto-responder** | Detects the workflow's Question-node pause in the reply stream and injects a configured auto-answer before returning control to SPLX. |
| **HTTP surface** | 2–3 endpoints SPLX's connector calls: open-session, message, close-session (Section 1.3). |

**Data flow (SPLX → proxy → Foundry → back):**

```
SPLX Probe                        Proxy (B1)                         Foundry (tatum-safeagents)
-----------                       ----------                         --------------------------
1. POST /session/open  ---------> create conversation  --------------> POST /openai/v1/conversations
                                   store conv.id under a
                                   proxy session_id
                        <--------- return {"session_id": "..."}

2. POST /message              --> look up conv.id                     POST /openai/v1/responses
   {message, session_id}          responses.create(                   (agent_reference: safe-agents,
                                     conversation=conv.id,               conversation=conv.id)
                                     agent_reference=..., input=msg)
                                   [stream / poll for reply]
                                   if HITL Question node pauses:
                                     auto-answer, re-invoke
                        <--------- {"reply": "<final text>"}

3. POST /session/close -------->  conversations.delete(conv.id) ----> DELETE (or equivalent) cleanup
                        <--------- 200 OK
```

### 1.2 What B2 adds

B2 is **the same B1 back-end**, unmodified in its integration surface, plus:

- A **React front-end** that subscribes to (or polls) the proxy for a live view of each scan turn:
  Supervisor → Preparer → Reviewer → Formatter step transitions, the raw streamed events, and any HITL
  pause with the auto-answer that was injected.
- A UI-driven way to **initiate and watch** the two OAuth-adjacent handshakes (SPLX ↔ proxy trivial key,
  proxy ↔ Entra token acquisition) — useful for demos and debugging, not required for SPLX to function.

**What B2 does *not* change:** SPLX still POSTs to the B1 back-end server-to-server; the React page never
sits in that request path. It does not change fidelity or what gets certified — same real workflow either
way. Treat B2 as a separate, optional milestone after B1 is proven (Section 5), not a parallel build.

---

## 2. The Foundry "dance" the back-end must implement

Grounded in the synthesis §4 spec and the captured working script, refined by the two later research
passes (checklist + findings doc). Steps 1, 2, and 6 are settled; steps 3–5 carry the open risks detailed
in Section 3.

1. **Acquire a token.** `DefaultAzureCredential().get_token("https://ai.azure.com/.default")`, backed by a
   service-principal client secret (or certificate) with the **Azure AI Developer** RBAC role (or
   equivalent) on `tatum-safeagents`. This is the single admin ask from the requirements checklist — it
   is shared infrastructure regardless of which SPLX-facing session pattern (Section 3.3) is used.
   Refresh on a schedule; Entra tokens run ~60–90 min TTL and a scan can outlast one (Section 3.6).

2. **Construct the client.**
   `AIProjectClient(endpoint="https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents", credential=<token-provider>)`.

3. **Open a session (proxy's `/session/open`, called once per SPLX scan or per conversation).**
   `openai_client.conversations.create()` → Foundry returns a server-generated conversation ID
   (`conv_...`). Store it under a proxy-issued `session_id` and return that to SPLX. This step is what
   resolves the Option A blocker — see Section 3.3.

4. **Send the attack (proxy's `/message`, called once per turn).**
   `openai_client.responses.create(conversation=<real conv.id>, extra_body={"agent_reference": {"name": "safe-agents", "type": "agent_reference", "version": "<current-live-version, e.g. 41 — CONFIRM>"}}, input=<attack prompt>, stream=True)`.
   `agent_reference` is a **top-level sibling of `input`** in the raw JSON body, not nested under
   `extra_body` (that's an SDK-only convenience name). **`version` is undocumented** in any official
   sample — test with and without it against the live resource before finalizing (Section 3.2).

5. **Reconstruct a single reply.** The captured production script consumes the event stream and filters
   for `RESPONSE_OUTPUT_TEXT_DONE`, ignoring intermediate `workflow_action` events (internal
   Supervisor/Preparer/Reviewer/Formatter transitions). This is the proven pattern for a workflow-kind
   agent with HITL, and is what B should default to (Section 3.4 explains why the alternative
   "non-streaming, read `output_text`" approach found in the Option A docs research is not yet confirmed
   safe for HITL detection).

6. **Detect and auto-answer the HITL Question node.** If the workflow pauses mid-turn waiting for a human
   answer, the proxy must inject a configured response (e.g., always "yes" or a blank/affirmative default)
   and continue the turn before returning to SPLX. This is a **new finding from the synthesis**, specific
   to this workflow's sequential + review-loop + HITL design — it will not appear in a simpler agent
   target. The auto-answer choice is itself a risk (Section 3.5).

7. **Return JSON at a stable path**, e.g. `{"reply": "<extracted text>"}`, so SPLX's Response Path field
   (`reply`, or `output_text` if the proxy mirrors Foundry's own field name) is set once and never changes.

8. **Close the session (proxy's `/session/close`, called once per SPLX scan or conversation).**
   `openai_client.conversations.delete(conversation_id=<real conv.id>)`, matching the captured script's
   own cleanup behavior, so scan runs don't leave orphaned conversation objects in the project.

### 2.1 Endpoints the proxy exposes to SPLX (B1)

| Proxy endpoint | Foundry call inside | SPLX connector feature used |
|---|---|---|
| `POST /session/open` | `conversations.create()` | SPLX's native **Open Session** toggle (REST API docs, "Session Management") |
| `POST /message` (`{message}`, `{session_id}`) | `responses.create(conversation=..., agent_reference=..., input=...)` | Standard REST connector POST + `{message}`/`{session_id}` placeholders + Response Path |
| `POST /session/close` | `conversations.delete(...)` | SPLX's native **Close Session** toggle |
| `GET /healthz` **[unverified — not in any source, standard practice]** | liveness ping to Foundry or a cached-token check | Not SPLX-facing; ops/monitoring only |

This is the single most concrete design payoff of building B rather than trying A: SPLX's REST connector
already has a first-class **Open Session / Close Session** feature built for exactly this "manage a
session out-of-band from the message endpoint" shape (per the SPLX REST API docs). Wiring the proxy to
that feature turns the server-generated-conversation-ID problem — which is the confirmed, HIGH-severity
blocker for Option A (findings doc, risk #1) — into a non-issue for Option B: the proxy, not SPLX, ever
touches the real Foundry conversation ID.

---

## 3. Hard parts / risks, and how B handles each

| # | Risk | Severity | How B handles it |
|---|---|---|---|
| 3.1 | **Entra auth** — Foundry Agents service accepts Entra ID only, no API key (Microsoft's own Feature Support Matrix). | Structural, not really a "risk" for B | Solved once, inside the proxy, via `DefaultAzureCredential`/service-principal. SPLX only ever sees a trivial key/header to reach the proxy. This is the auth problem Option A cannot cleanly solve and Option B was chosen specifically to absorb. |
| 3.2 | **`agent_reference` routing + undocumented `version` field.** No official sample shows `version` inside `agent_reference`; the captured working script includes it. | Moderate | Test both with and without `version` against `tatum-safeagents-resource` during Milestone 1 (Section 5). Since the proxy fully controls the outgoing payload, this is a one-line config flag, not an architectural risk. |
| 3.3 | **Server-generated conversation/session ID.** Foundry's `conversation` field requires an ID from a prior `POST /openai/v1/conversations` call — it does not accept an arbitrary client string. This is the confirmed HIGH/blocking risk for Option A. | High for A, **low for B** | B's whole purpose is to own this two-step flow: `/session/open` creates the real conversation server-side; SPLX's `{session_id}` maps to a proxy-issued token, never the real Foundry ID directly (Section 2.1). This is the single clearest reason B is more robust than A for this specific workflow. |
| 3.4 | **Streaming vs. flat Response Path.** Two sources disagree on the safest approach: the captured production script uses `stream=True` + filters `RESPONSE_OUTPUT_TEXT_DONE` (proven, but built for a workflow-kind agent with HITL); the Option A docs-research pass found `output_text` non-streaming is the documented default and simpler. **Neither source has directly tested whether non-streaming still surfaces the HITL pause equivalently — this is an open gap, not resolved by either document.** | Moderate | Because SPLX never talks to Foundry directly under B, this choice is entirely internal and swappable without touching the SPLX-facing contract. Recommendation: **default to the proven `stream=True` + event-filter pattern** for the first build (Milestone 2), since it's the only one empirically confirmed to work against this exact workflow including HITL; revisit non-streaming only if latency/complexity becomes a problem, and only after confirming empirically that it still surfaces the Question-node pause. |
| 3.5 | **HITL auto-answer and its result-biasing risk.** Always answering "yes" (or blank) to unblock a scan may suppress a "no" branch with different, untested Formatter behavior — meaning the scan quietly never exercises part of the workflow's logic. | High (methodological, not technical) | B can implement the auto-answer as a **configurable policy**, not a hardcoded constant: e.g., alternate yes/no across turns, or run two passes (all-yes, all-no) and diff the Formatter output. This doesn't eliminate the bias risk but makes it visible and tunable rather than silent. **This is a decision the team meeting should make explicitly** (Section 6), not something to default silently in code. |
| 3.6 | **Entra token TTL on long scans.** Tokens run roughly 60–90 minutes; a Probe scan firing thousands of requests over an extended run can outlast one token. | Moderate | The auth module (Section 1.1) refreshes proactively on a timer (e.g., re-acquire at 75% of TTL) rather than reactively on 401 — standard token-refresh pattern, low engineering cost, but must not be skipped for a scan expected to run multiple hours. |
| 3.7 | **[unverified, lower priority] HTTP 431 report** — a single, unconfirmed community report of "header fields too large" against this exact endpoint pattern in one region, contradicted by Microsoft's own working curl examples. | Low/contested | Smoke-test the raw endpoint early (Milestone 1) before assuming this is a non-issue; if it recurs, it's a proxy-side header-size/region concern to route around, not a redesign. |
| 3.8 | **Workflow-type agent versioning via REST is thinly documented** — all official `agent_reference` samples use prompt-kind agents; no worked example targets a `"kind": "workflow"` agent specifically, and Foundry is retiring the visual workflow designer 2026-12-01. | Low now, worth flagging | Use the Foundry portal's Version dropdown as ground truth for the current `safe-agents` version rather than relying on unverified REST version-discovery behavior. Re-verify this doc gap if the build is delayed past a few weeks, given the retirement timeline. |

---

## 4. Recommended tech stack

| Layer | Recommendation | Rationale |
|---|---|---|
| **B1 back-end language/framework** | **Python + FastAPI** | Matches the synthesis §4 spec directly — the captured working script and all three SDKs in play (`azure-identity`, `azure-ai-projects`, the OpenAI-compatible client) are Python-native. FastAPI gives async request handling (useful for streaming reconstruction) and trivial OpenAPI docs for the SPLX-facing contract. |
| **Session store** | In-memory dict for a single-instance proxy; Redis (or equivalent) **[unverified — sizing decision, not sourced]** only if the proxy needs to scale horizontally or survive restarts mid-scan. | Keeps Milestone 1–2 simple; defer infra complexity until a real need (e.g., a long multi-instance scan) appears. |
| **Auth** | `azure-identity`'s `DefaultAzureCredential`, backed in production by `ClientSecretCredential` (env vars `AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_TENANT_ID`) | Directly matches the captured script and the Feature Support Matrix requirement; `DefaultAzureCredential` transparently supports the client-credentials flow without extra code. |
| **Deployment target** | **[unverified — not sourced from these documents]** Azure App Service / Azure Container Apps / Azure Function, any of which can run a FastAPI app and reach `tatum-safeagents-resource` over the standard Azure network path. | Not specified in the source material; pick based on existing Azure hosting conventions this project already uses. Flag as an open item if none exists yet. |
| **B2 front-end** | **React**, calling the same B1 back-end's endpoints (plus a lightweight event/log endpoint the back-end would need to add for live visibility) | Matches the colleague's proposal as folded into the options map; no new integration surface, purely additive. |

---

## 5. Phased build breakdown

**Milestone 0 — Preconditions (shared with Option A, do first regardless of final choice)**
- Confirm `tatum-safeagents-resource` liveness (portal or `az cognitiveservices account show`).
- Obtain the service-principal Client ID/Secret + RBAC role (the single admin ask).
- Confirm the current `safe-agents` workflow version via the portal's Version dropdown (do not trust the captured `41`).

**Milestone 1 — "Prove one call" (minimum viable subset)**
- A script (not yet a service) that: acquires a token, creates one conversation, sends one
  `responses.create` call with `agent_reference`, and prints the raw reply.
- Resolves in this pass: the `version` field test (3.2), the HTTP 431 smoke test (3.7), and confirms the
  endpoint/payload shape end-to-end.
- **This milestone alone answers most of the "will B work at all" question** before any web framework is
  written.

**Milestone 2 — Headless proxy, single-turn (B1 core, no HITL yet)**
- Wrap Milestone 1's logic in a FastAPI service with `/session/open`, `/message`, `/session/close`.
- Point SPLX's REST connector at it using the Open Session/Close Session toggles; run a small manual scan
  against a workflow path known not to trigger HITL, if one exists **[unverified whether such a path
  exists — needs empirical check against the workflow definition]**.
- This is the earliest point at which SPLX is actually attacking the real workflow, even if narrowly.

**Milestone 3 — HITL handling**
- Add Question-node detection + configurable auto-answer policy (3.5).
- Decide and implement the streaming-reconstruction approach (default: `stream=True` + event filter, per
  3.4) robustly enough to detect the pause mid-stream.
- This milestone is what turns Milestone 2's narrow scan into a scan that can traverse the full
  Supervisor→Preparer→Reviewer→Formatter path, including the review loop.

**Milestone 4 — Hardening for a real scan**
- Token refresh-on-schedule (3.6), cleanup guarantees (session close even on error paths), basic logging
  for debuggability, and a documented scope note (mirroring the synthesis §5 table) for whoever reads the
  scan report about what is and isn't covered.
- **This is the point at which B1 is scan-ready.**

**Milestone 5 (optional, separate decision) — B2 React front-end**
- Add an event/log endpoint to B1 exposing per-turn workflow-step data.
- Build the React view over it; wire up the observability of both OAuth handshakes.
- No new integration risk versus B1 — purely additive UI work. Do not start this before B1 is proven
  through Milestone 4, since it depends on B1's shape being stable.

---

## 6. Open decisions the meeting must settle (Option B specific)

1. **Is B2 (React) in scope at all, or is B1 sufficient for now?** The options map explicitly flags this
   as "decide deliberately, don't build it by default" — it's a genuine scope call, not a technical
   blocker.
2. **What is the HITL auto-answer policy?** Always-yes, always-no, alternating, or dual-pass (Section
   3.5) — this changes what the scan can be said to have tested, so it needs a decision, not a default
   buried in code.
3. **Streaming vs. non-streaming reconstruction (3.4)** — confirm empirically whether non-streaming
   (`output_text`) still surfaces the HITL pause before treating it as a viable simplification; until
   then, treat `stream=True` as the default plan.
4. **Where does the proxy get hosted?** Not addressed in any source document — needs an infra decision
   before Milestone 2 can be deployed anywhere beyond a developer's machine.
5. **Session store durability** — is an in-memory map acceptable for the expected scan duration/scale, or
   does Milestone 2 need Redis (or similar) from the start?
6. **Relationship to Option A's cheap test.** The options map recommends testing Option A's OAuth-only
   path first regardless of eventual choice, since a full Option A success would make B unnecessary and a
   partial success narrows exactly how thin B needs to be. Confirm whether that test happens before or in
   parallel with any Option B build work.

---

## 7. Biggest single execution risk

Of everything above, the risk most likely to derail a build is **3.5 — the HITL auto-answer's
result-biasing effect**, not any of the auth/routing/streaming plumbing (which are all solvable, bounded
engineering problems with a proven reference script to copy). The plumbing risks have known shapes and
known fixes; the HITL policy question doesn't have a "correct" technical answer — it's a methodological
choice that determines what the eventual SPLX scan can honestly be said to have tested, and getting it
wrong silently (e.g., defaulting to always-yes without discussion) could produce a scan report that
looks complete but never actually exercised the workflow's "no" branch.
