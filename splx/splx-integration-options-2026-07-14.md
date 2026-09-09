# SPLX × Foundry — Integration Options Map

**Date:** 2026-07-14
**Purpose:** Capture *every* option discussed for connecting SPLX Probe to the `tatum-safeagents`
Foundry workflow, so we can study the situation with a complete picture before committing to a build.
**Status:** Companion to the
[research synthesis](research-synthesis-splx-foundry-workflow-agent-2026-07-14.md) (the "why" behind
the auth/connector constraints) and the [folder README](README.md) (the orientation).

> ## ⏳ DECISION (2026-07-16): UNDEFINED — pending meeting
> **No path is chosen yet.** The proper approach will be settled in a full team meeting that hasn't
> happened yet; until then all options (A–D, including B's B1/B2 sub-paths) remain open and none is committed.
>
> **Prior stance (2026-07-14, now reopened):** Option A first — try SPLX's native OAuth pointed straight
> at Foundry before building anything, with B/C/D banked as fallbacks. This was never executed and is no
> longer the standing decision; it is retained below only as one candidate to weigh in the meeting.
> Its execution checklist survives in §8 for reference (not as a committed plan).
>
> **New wrinkle on the table (from a colleague, 2026-07-16):** front the self-built proxy with a
> **React page** that surfaces the workflow calls and drives the OAuth handshake with SPLX and Foundry.
> This is *not* a separate architecture — it's a sub-path of **Option B**: **B1 = headless proxy**,
> **B2 = the same proxy + a React front-end**. The React layer is observability/UX only; it does not
> change what SPLX certifies. See §2/§3 (Option B).
>
> **Do not treat any option as decided until the meeting logs a choice here.**

---

## 0. Read this first — two framing corrections

Two things trip people up when reasoning about these options. Getting them straight makes the whole
map click.

**Correction 1 — OAuth is not the obstacle; it's a candidate solution.**
The obstacle is that Foundry's **Agents service demands Entra ID identity and refuses simple API keys**
(confirmed by Microsoft's Feature Support Matrix — see the synthesis, §3). "OAuth" (specifically the
client-credentials flow) is *one possible way* to satisfy Entra, not something we're trying to bypass.
So **auth is not a one-time branch you pick — it's a thread running through every option below**,
answered differently in each. A proxy doesn't "bypass OAuth"; it *handles the Entra login internally*
(via the SDK's `DefaultAzureCredential`) so SPLX only needs a trivial key to reach the proxy.

**Correction 2 — "build a proxy" and "recreate in the SDK" are one spectrum, not two species.**
Both are the same architecture: **an app in the middle, written with the SDK, sitting between SPLX and
Foundry.** A proxy *is* an SDK app. The only difference is how much that middle app **delegates vs.
contains**:

- **Thin (proxy):** the middle app forwards to the **real deployed workflow**; Foundry runs the
  orchestration. Highest fidelity to production.
- **Thick (SDK recreation):** the middle app **contains the orchestration itself**; you run it.
  Fidelity depends on how faithfully your code replicates production.
- **Hybrid** sits between: orchestrate in code, but call the **real deployed agents** — so you own the
  plumbing (auth, streaming, HITL) while keeping the agent definitions authentic.

Keep these two corrections in mind; the table in §2 is built on them.

---

## 1. Background concepts (plain-language, so the options make sense)

- **Connector** — SPLX's pre-built adapter for a type of target (like different plug shapes). SPLX has
  ~20; **none is shaped for Foundry workflows**. The generic **REST API connector** is the flexible,
  configure-it-yourself one.
- **REST API connector's worldview** — "I send **one flat POST** to **one URL** with a `{message}`
  placeholder, and I read **one text answer** back via a JSON path (Response Path)." This simplicity is
  why it struggles with Foundry (see next point).
- **Why Foundry is hard for that worldview** — invoking `tatum-safeagents` is a **multi-step SDK dance**,
  not one POST: create a conversation → send the attack *with* an `agent_reference` parameter naming the
  workflow → receive the answer as a **stream** of events (not one JSON blob) → possibly hit a **HITL
  (Human-in-the-Loop) pause** ("Is this acceptable?") → clean up. A flat connector can't natively do
  this.
- **Entra ID** — Microsoft's corporate identity system (formerly Azure AD). Instead of a static
  password, you prove identity and get a short-lived **token**. Foundry's Agents service requires this.
- **SDK (Software Development Kit)** — a toolkit of pre-written code so you don't hand-build the fiddly
  parts. It's a friendly wrapper over the same raw REST API. The three in play (all Python, all visible
  in our captured script):
  - `azure-identity` → `DefaultAzureCredential()` — does the Entra login / token fetch.
  - `azure-ai-projects` → `AIProjectClient` — connects to the `tatum-safeagents` project.
  - the OpenAI-compatible client → `responses.create(...)` — sends the message, streams the reply, and
    carries `agent_reference`. (Foundry deliberately speaks "OpenAI's language" even though the model is
    Claude 4.6.)
  - plus a **web framework** (FastAPI/Flask) for any option that must expose a URL SPLX can POST to.
- **HITL stall** — the workflow's Question node pauses for a human; an automated scan hangs forever
  unless something auto-answers it. A recurring blocker for any option that reaches the full workflow.
- **Fidelity** — how faithfully the thing SPLX attacks matches production. **You only ever certify the
  thing SPLX actually attacks.** This is the single most important lens for choosing.

---

## 2. The full options map

| # | Option | SPLX points at | Who does Entra auth | What it certifies | Build effort |
|---|---|---|---|---|---|
| **A** | **REST + OAuth direct** | Foundry endpoint | SPLX's own OAuth form | The workflow *if* streaming/routing/HITL can be expressed (doubtful) | Config only |
| **B** | **REST + proxy you build** (sub-paths **B1 headless** / **B2 + React UI**) | your proxy | proxy, internally (SDK) | **Real deployed workflow** — highest fidelity | Build a translator (B2 adds a front-end) |
| **C** | **REST + SPLX Proxy Interface** | SPLX-assisted proxy | proxy, internally | Real deployed workflow | Vendor coordination |
| **D** | **SDK recreation (thick / hybrid)** | your SDK app | app, internally (SDK) | **Your reimplementation** — fidelity risk, or clean v6 isolation | Build orchestration + endpoint |

**How they relate:** B, C, D are the "middle-app" spectrum (thin → vendor-built → thick). A is the
"maybe build nothing" hope. **The two paths to a *proxy* are C (SPLX builds it) and B (you build it);
B's React page (B2) is an optional front-end on top of the same back-end, not a different architecture.**

---

## 3. Each option in depth

### Option A — REST + OAuth pointed directly at Foundry (no proxy)
The cheap experiment where you potentially **build nothing**. The SPLX REST API doc confirms the OAuth
form has the exact client-credentials fields Layer-1 Entra auth needs (token URL, Client ID, Client
Secret, Scope → `https://ai.azure.com/.default`).
- **Likely dealbreakers (why it's a *test*, not a plan):** Foundry **streams** the reply (SPLX expects
  one static JSON to read via Response Path); the workflow needs the `agent_reference` routing parameter
  (may not fit a flat payload template); the **HITL pause** would hang the scan.
- **Still worth it because:** it's cheap, and its result tells you how much of B/C/D you'd even need. If
  OAuth authenticates but routing/streaming don't fit, you learn you need only a *thin* proxy, not a
  full one.
- **Open questions it resolves:** synthesis §6, Gap #2.

### Option B — REST + proxy you build
A small web app (SDK + a web framework) exposing **one simple URL** to SPLX. It receives the flat
`{message}`, does the full Foundry dance internally (token via `DefaultAzureCredential`, create
conversation, send with `agent_reference`, filter the stream for `RESPONSE_OUTPUT_TEXT_DONE`,
auto-answer HITL, clean up), and returns one clean JSON reply.
- **Fidelity:** highest — SPLX attacks the *real deployed workflow*.
- **Auth:** handled internally; SPLX only needs a trivial key to reach the proxy.
- **Concrete spec:** synthesis §4 (grounded in the captured working script).
- **Main risk to handle:** the HITL auto-answer choice can itself bias results (always "yes" may
  suppress a "no" path) — synthesis §6, Gap #3.

**Two sub-paths — same back-end, different amount of UI:**

- **B1 — Headless proxy (the core).** Just the back-end web service (e.g. Python + FastAPI). SPLX POSTs
  to its URL; it returns JSON. No user interface — it runs as a service. This is the *minimum* that makes
  a proxy work, and everything SPLX actually needs. Lowest build effort of the self-built path.
- **B2 — Proxy + React page (the colleague's proposal, 2026-07-16).** The **same B1 back-end**, plus a
  **React front-end** on top that *surfaces the workflow calls* (a live view of Supervisor → Preparer →
  Reviewer → Formatter, the streamed events, any HITL pause) and can drive the **OAuth handshake with
  SPLX and Foundry** visually. Key points to keep straight:
  - The React page is **not what SPLX talks to** — SPLX still POSTs to the B1 back-end server-to-server.
    React is an **observability / operator UI**, not the integration surface.
  - It **does not change fidelity or what gets certified** — SPLX attacks the same real deployed workflow
    either way. B2 buys *visibility and UX*, not a better security claim.
  - **Why do it anyway:** turning the proxy from a black box into something you can watch is a genuine
    debugging/demo aid, and it's a **good learning opportunity** (React + the two OAuth handshakes) even
    if not strictly required. Whether it's worth the extra front-end effort is an open call — decide
    deliberately, don't build it by default.
  - **Extra cost vs. B1:** a whole front-end app (React) plus wiring it to observe the back-end. The hard
    back-end problems (auth, `agent_reference`, streaming, HITL) are identical to B1 — B2 adds no new
    integration risk, only UI surface.

### Option C — SPLX's own Proxy Interface (vendor-assisted)
Same architecture as B, but **SPLX helps build it** — their REST API doc explicitly offers this
("we've developed the SPLX Proxy Interface… contact us and we'll assist you").
- **Best for:** avoiding hand-rolling the streaming/HITL translation if SPLX has already solved that
  shape. Worth a discovery conversation before spending your own engineering time.
- **Unknown:** whether their interface can accommodate Entra + `agent_reference` + HITL specifically.

### Option D — SDK recreation (thick / hybrid)
Write an app that **contains the orchestration** and exposes a simple URL to SPLX. Auth, streaming, and
HITL all become your program's *internal* business, so the SPLX-facing side is trivial.
- **Spectrum within D:**
  - *Thick (full recreation):* reimplement agents + orchestration in code, calling the raw model.
    Lowest fidelity to production; **likely bypasses the platform guardrail/content-filter layer.**
  - *Hybrid (recommended if going this route):* orchestrate in code, but invoke each of the four agents
    as its **real deployed Foundry agent** — preserves agent-prompt fidelity while giving you plumbing
    control. You re-implement only the *conductor*, not the *musicians*.
- **The catch — fidelity:** you certify your *reimplementation*, not production. The parts hardest to
  copy faithfully are exactly where this project keeps finding real risk: platform guardrails/content
  filters, the review-loop turn logic, the HITL behavior, JSON-schema enforcement, and the
  `tool_choice` failure mode.
- **The reframe — this can be a feature:** if the goal is to measure the **v6 system-message block in
  clean isolation** (stripped of platform guardrails), D is arguably the *best* tool. Bypassing the
  guardrail layer becomes a deliberate, documented scoping choice rather than an accident.

---

## 4. The auth thread, per option (quick reference)

| Option | Entra handled by | SPLX-facing auth |
|---|---|---|
| A | SPLX's OAuth form (untested against Entra) | OAuth client-credentials |
| B | your proxy (`DefaultAzureCredential`) — same for B1 and B2 | trivial key/header (B2's React only *surfaces* the handshake) |
| C | SPLX-assisted proxy | trivial key/header |
| D | your app (`DefaultAzureCredential`) | trivial key/header |

Recurring cross-option blockers regardless of auth: **streaming reply reconstruction**, **`agent_reference`
routing**, and the **HITL stall** — options B/C/D solve these inside the middle app; option A must solve
them inside SPLX's connector (probably can't).

---

## 5. The two questions that collapse the list

When it's time to decide, only two questions matter:

1. **What must you be able to claim?**
   - "The production workflow, exactly as it runs, resists these attacks" → **B** or **C** (real thing).
   - "Our v6 system-message defense resists these attacks, measured cleanly" → **D** is arguably best.
2. **How much do you want to build?**
   - Almost nothing, willing to test → **A**. A real thing you own → **B** or **D**.
   - Let the vendor carry it → **C**.

---

## 6. Cheapest next moves (regardless of eventual choice)

These inform *every* option and require little/no commitment:

1. **Test Option A** — fill SPLX's OAuth form with the tenant token endpoint, a service-principal
   Client ID/Secret, and scope `https://ai.azure.com/.default`; see if it authenticates and whether a
   payload template can carry `agent_reference`. The result tells you how much of B/C/D you actually
   need. (Resolves synthesis §6, Gap #2.)
2. **Quick liveness check** on `tatum-safeagents` (Azure Portal / `az`) before any scan run — endpoint
   is confirmed (synthesis §6, Gap #1 resolved), liveness is a fast sanity check.
3. **Ask SPLX about their Proxy Interface (Option C)** — a discovery call could remove the need to
   hand-build B.

---

## 7. Related open questions (from the synthesis §6)

- **Gap #2** — does SPLX's OAuth actually authenticate against Entra, and can the payload carry
  `agent_reference`? (Gates A, and how thin B/D can be.) *Partially resolved: fields confirmed, behavior
  untested.*
- **Gap #3** — will HITL stall the scan, and does auto-answering bias results? (Affects A/B/C.)
- **Gap #4** — does the content-filter masking risk transfer to Claude, which has no in-portal severity
  sliders? (Affects fidelity of D.)
- **Gap #5** — token TTL/refresh behavior for long scans. (Affects B/D proxy design.)
- **Gap #1** — endpoint: **resolved** (`tatum-safeagents-resource` / `tatum-safeagents`).

---

## 8. Execution checklist — Option A (chosen path)

**Goal:** get SPLX's REST connector to authenticate to Foundry via its native OAuth form and reach the
`safe-agents` workflow, building nothing.

### 8.1 Values to gather (see the requirements list for self-vs-help split)
- Project endpoint URL — `https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents` (verify live)
- Entra **tenant ID**
- **Service principal**: Client ID + Client Secret **with an RBAC role assigned** (e.g. *Azure AI Developer*) on the `tatum-safeagents` project — the single admin ask that unblocks B
- Workflow name (`safe-agents`) + **current** deployed version
- Confirmation the environment is live

### 8.2 SPLX OAuth form → Foundry/Entra mapping
| SPLX OAuth field | Value to enter |
|---|---|
| URL | `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token` |
| Client ID | service principal Client ID |
| Client Secret | service principal secret |
| Scope | `https://ai.azure.com/.default` |

### 8.3 SPLX REST connector (non-OAuth) fields
- **URL** — the Foundry responses endpoint
- **POST payload** — must carry the attack via `{message}`, `{session_id}`, **and** the `agent_reference`
  (name + version) routing parameter. *Open risk:* whether the flat payload template can express
  `agent_reference` at all (Gap #2).
- **Response Path** — JSON path to the reply text. *Open risk:* Foundry streams the reply; a flat
  Response Path may not reconstruct a stream.

### 8.4 What success / partial-success / failure tells us
- **Full success** (auth + routing + readable reply) → run the scan; no proxy needed.
- **Auth works, routing/streaming/HITL don't** → we need only a *thin* proxy (Option B) or SPLX's Proxy
  Interface (Option C) — not a full build. This is the most likely outcome.
- **Auth fails against Entra** → fall back to a proxy that handles Entra internally (B/C) or SDK
  recreation (D).

### 8.5 Known blockers to watch during the test (from §3–§4)
- The **HITL Question node** may stall the scan (Gap #3).
- Entra **token TTL** may expire mid-scan on long runs (Gap #5).
- Confirm current workflow **version** — the captured `41` is likely stale.
