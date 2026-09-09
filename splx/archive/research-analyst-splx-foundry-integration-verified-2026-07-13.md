# SPLX × Microsoft AI Foundry — Verification & Integration Deep Dive
**Date:** 2026-07-13
**Supersedes/updates:** research-analyst-splx-foundry-integration-2026-06-15.md
**Overall confidence:** Moderate-High (verification track is high confidence — primary sources fetched directly; auth/extension track is Moderate — some inference remains)
**Sources:** 15 (SPLX/Probe official docs, Microsoft Learn primary docs, Microsoft Q&A, Microsoft Tech Community, WebSearch aggregation)

---

## 1. Executive Summary

Nothing structurally broke since 2026-06-15 — `docs.probe.splx.ai` is alive, unmigrated, and last updated February 2026. The Azure OpenAI connector, its config fields, and the REST API fallback all check out as described in the prior report. **The one genuinely new and load-bearing finding**: the Foundry third-party guardrails partner page (`learn.microsoft.com/.../third-party-integrations`) now names exactly two partners — **Palo Alto Networks Prisma AIRS** and **Zenity** — with worked code examples for Prisma AIRS. SPLX/Zscaler is **confirmed absent**, closing the prior report's open question with a "no," not a "still pending." Runtime guardrail integration (Path B) is now a **dead path** on the native Foundry BYOL mechanism, not an unconfirmed one.

The user's actual goal — red-teaming Foundry with SPLX Probe — remains viable and is the stronger, faster path: **Go**. Point Probe's Azure OpenAI connector at the model deployment endpoint; this works today with a free 110-credit trial account, no infrastructure changes, no Microsoft approval required. The connector list has grown since June (now also lists Microsoft Teams, Amazon Bedrock AgentCore/Agents, Agentforce, Glean, Slack, WhatsApp — but still **no explicit "Azure AI Foundry" or "Foundry Agent" connector**), so targeting anything beyond the raw model deployment (a Prompt Agent, Hosted Agent, or Workflow Agent) still requires the REST API connector plus a thin proxy.

**Top blocker for anything beyond model-deployment-level scanning:** Foundry is actively steering agent auth toward Entra ID / Managed Identity (Foundry Agent Service Hosted Agents each get their own Entra identity by design), while every SPLX connector — Azure OpenAI, OpenAI Assistant, REST API — expects a static API key or bearer token in a header. There is no clean, officially documented bridge. The workaround is real but adds engineering: a token-refreshing proxy in front of the agent that SPLX's REST API connector calls.

**Second confirmed finding worth flagging for scan validity:** Microsoft's content-filter documentation states in its own words that full off / annotate-only mode "requires approval" via the Azure OpenAI Limited Access Review: Modified Content Filters form — and a Microsoft Q&A response states plainly that at this time it is not possible to become a managed customer for that program. This means a SPLX Probe scan run against a standard Foundry deployment will, by default, have Microsoft's own Prompt Shields / Content Safety filters sitting in front of the model and cannot be switched off through self-service. Severity threshold adjustment (Low/Medium/High) is self-service; full off/annotate-only is gated and — per current guidance — effectively unobtainable for most customers right now.

---

## 2. Verification Results — Prior Report Audit

| Prior Claim | Status | What Changed | Source |
|---|---|---|---|
| `docs.probe.splx.ai` doc URLs resolve (Azure OpenAI, Azure ML, OpenAI Assistant, REST API, target index) | **CONFIRMED STILL TRUE** | Domain unmigrated; site last updated Feb 2026 per search index | docs.probe.splx.ai/ai-red-teaming/probe/target/index/azure-openai, /openai-assistant, /rest-api, /index (fetched directly) |
| AI Runtime Protection "getting-started" page at `docs.probe.splx.ai/ai-runtime-protection/getting-started` | **CHANGED — now 404** | Prior report's cited URL no longer resolves; docs restructured. Runtime Protection content likely moved/renamed under a different path not surfaced by sitemap.md search | docs.probe.splx.ai/sitemap.md (fetched — no runtime-protection getting-started listed) |
| Connector list = {Azure OpenAI, Azure ML, Copilot Studio, OpenAI Assistant, REST API} | **CHANGED — list expanded, core five unchanged** | Current full list: Azure OpenAI, Azure ML, Copilot Studio, OpenAI Assistant, REST API, Proxy SDK, OpenAI Compatible API, Microsoft Teams, Glean, Slack, WhatsApp, Agentforce, Amazon Bedrock AgentCore, Amazon Bedrock Agents, Anthropic, Databricks, Hugging Face, OpenAI, Mistral, Gemini, Bedrock, Dify AI. **No connector named "Azure AI Foundry" or "Foundry Agent" exists.** | docs.probe.splx.ai/ai-red-teaming/probe/target/index (fetched directly) |
| Azure OpenAI connector config fields: endpoint, API key, deployment name, system prompt, API protocol, API version | **CONFIRMED STILL TRUE (mostly)** | Fields confirmed: System Prompt, API Key, URL (`https://{resource}.openai.azure.com`), Deployment Name, API type (Chat Completions or Responses API). No distinct "API version" field surfaced in the fetched page text — likely embedded in the API-type/URL config rather than a standalone field. Not a material change. | docs.probe.splx.ai/ai-red-teaming/probe/target/index/azure-openai (fetched directly) |
| OpenAI Assistant connector requires API key + assistant ID; Foundry Agent targeting is inferred, not confirmed | **CONFIRMED STILL TRUE** | Page still requires exactly API Key + Assistant ID; no Azure, Entra, or Foundry references anywhere in the doc. The "maps to a Foundry Prompt Agent" claim remains pure structural inference, unchanged in status. | docs.probe.splx.ai/ai-red-teaming/probe/target/index/openai-assistant (fetched directly) |
| SPLX not confirmed as named partner on Foundry third-party guardrails page | **CHANGED — now resolved to NO** | Page now explicitly lists only **Palo Alto Networks Prisma AIRS** and **Zenity** as named partners, with a full worked code example and region-availability table for each. SPLX/Zscaler appears nowhere on the page. This is a definitive negative, not an unconfirmed absence. | learn.microsoft.com/en-us/azure/foundry/guardrails/third-party-integrations (fetched directly, full page content reviewed) |
| Zscaler acquired SPLX Nov 2025 (~$692M); docs continue under `docs.probe.splx.ai` branding | **CONFIRMED STILL TRUE** | No renaming of the docs domain or product observed. Self-serve trial signup still live at `probe.splx.ai/auth/sign-up`. Pricing tiers (Trial/Professional/Enterprise) also still listed, with Enterprise offering SaaS or on-prem. | WebSearch aggregation (AWS Marketplace listing, splx.ai, probe.splx.ai/auth/sign-up) |
| Foundry AI Red Teaming Agent (PyRIT-backed) — status | **CONFIRMED STILL TRUE, still preview** | Still explicitly described as "public preview" in current Microsoft Foundry devblog and Learn content as of research date; no GA announcement found. | learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent; devblogs.microsoft.com/foundry/ai-red-teaming-agent-preview/ |
| REST API connector payload format uses `{message}` / `{session_id}` placeholders | **CONFIRMED STILL TRUE, with added detail** | Confirmed placeholders exist; new detail captured: Authorization headers required for non-public APIs (or OAuth); a "Response Path" JSON-path field defines where the reply is parsed from the response body; optional separate Open Session / Close Session endpoints supported. | docs.probe.splx.ai/ai-red-teaming/probe/target/index/rest-api (fetched directly) |
| SPLX severity-threshold self-service vs. off/annotate-only requiring Microsoft Limited Access Review, and "not possible to become a managed customer" | **PARTIALLY CONFIRMED — via independent primary source, though not exactly the claim as framed** | This claim, as originally framed, conflated SPLX's own runtime severity settings with **Azure OpenAI/Foundry's native content filter** configurability. Verified independently: Microsoft's own content-filter-configurability doc states severity threshold (Low/Medium/High) is self-service and configurable by all customers; full "No filters" or "Annotate only" modes are gated behind Limited Access Review approval ("If approved" — footnoted, with an application form link). The "not possible to become a managed customer at this time" phrasing was not found verbatim on the primary Microsoft Learn page fetched, but a Microsoft Q&A community thread ("Managed customers - Azure Open AI Content Filter") corroborates this as current guidance. Treat the exact wording as **Reported** (community Q&A), not **Confirmed** (primary doc); the underlying mechanism (approval-gated full off/annotate) **is Confirmed** from the primary doc. | learn.microsoft.com/en-us/azure/foundry-classic/foundry-models/concepts/content-filter (fetched directly, full "Configurability" table); Microsoft Q&A thread via WebSearch |

---

## 3. Foundry Surface → SPLX Connector Map

| Foundry Surface | Endpoint Shape | SPLX Connector | Auth Required | Viability | Confidence |
|---|---|---|---|---|---|
| Model deployment (Azure OpenAI Chat Completions / Responses API) | `https://{resource}.openai.azure.com` + deployment name | **Azure OpenAI** (named) | API key (native fit) or Entra token (connector docs don't confirm Entra support) | **High** — direct, documented, zero extra engineering | Confirmed |
| Model deployment via Azure ML / model catalog serverless endpoint | Azure ML Target URI | **Azure ML** (named) | API key / endpoint-scoped key | **High** — direct, documented | Confirmed |
| Copilot Studio agent published to Foundry/Teams/M365 Copilot | Copilot Studio-managed endpoint | **Copilot Studio** (named) | Handled by connector's own auth flow (not detailed in fetched docs) | **Moderate** — named connector exists but exact auth model for a Foundry-published agent not independently verified this pass | Reported (unchanged from prior) |
| Foundry Prompt Agent (OpenAI Assistants-compatible thread/run/message) | Foundry project endpoint `https://<resource>.services.ai.azure.com/api/projects/<project>` + agent ID | **OpenAI Assistant** (named, but built for plain OpenAI) | Connector requires only "OpenAI API key" + Assistant ID — no Azure/Entra fields exist in the connector config | **Low-Moderate** — structural compatibility (Assistants-style API) but connector has no field for Azure resource/project routing or Entra bearer tokens; likely fails without a proxy that rewrites requests | Inferred / Moderate |
| Foundry Hosted Agent | Deployed with dedicated per-agent Entra ID identity; REST-deployable per Microsoft Tech Community | No named connector | **Entra ID managed identity by design** — Microsoft's stated pattern eliminates static credentials entirely | **Low** — no clean path; requires REST API connector + auth-bridging proxy | Inferred |
| Foundry Workflow Agent | Not independently characterized this pass | No named connector | Unknown — likely Entra-first per platform trend | **Low** — same fallback as Hosted Agent | Inferred, low confidence |
| Foundry Agent published via Microsoft Teams | Teams-integrated endpoint | **Microsoft Teams** (newly observed connector, not in prior report) | Not detailed in fetched docs | **Moderate** — new connector option worth testing directly; not evaluated in depth this pass | Reported, new finding |
| Any custom/unlisted Foundry endpoint (Hosted/Workflow Agent fallback) | Any HTTP endpoint | **REST API** (named, universal fallback) | Configurable headers, incl. Authorization; supports OAuth per docs | **High as a fallback** — works for anything reachable over HTTP, but requires building the request/response mapping and any token-refresh logic yourself | Confirmed (connector mechanics), Inferred (that it solves the Entra problem without a proxy) |

---

## 4. The Auth Problem

**Confirmed direction of travel:** Microsoft's current authentication guidance for Foundry (`learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry`, corroborated by a third-party engineering writeup) is explicit: default to Entra ID for anything beyond quick evaluation; API keys are positioned as convenient-but-coarse, appropriate for prototyping only. For **Hosted Agents** specifically, Microsoft's design gives *each agent its own Entra identity* and explicitly discourages hardcoded credentials — "no hardcoded credentials, no manual token management, no certificate rotation" is the stated design goal (Confirmed, per Microsoft Learn Hosted Agents docs and a third-party engineering blog corroborating the same pattern).

**SPLX's connectors are API-key/bearer-token shaped, not Entra-shaped.** None of the three most relevant connectors (Azure OpenAI, OpenAI Assistant, REST API) have a documented OAuth2/Entra client-credentials flow field. The REST API connector's own docs mention "Authorization headers... or OAuth can also be used" — this is the one connector with headroom to carry a bearer token, but SPLX's docs don't describe a token-refresh mechanism, and Probe scan runs (which fire thousands of attack requests over an extended run) will likely outlast a short-lived Entra token's TTL if the token isn't refreshed mid-scan.

**Is there a clean, documented path?** No. **Confirmed absence**, not just an unconfirmed gap: no SPLX doc page fetched in this pass mentions Entra ID, managed identity, or OAuth2 client-credentials flow by name. The workaround is a small proxy service that:
1. Holds a service-principal credential and refreshes an Entra token on a schedule (or per-request)
2. Exposes a static HTTP endpoint + a fixed API key that SPLX's REST API connector authenticates against
3. Translates SPLX's `{message}`/`{session_id}` payload into whatever the Foundry Hosted/Workflow Agent's actual invocation contract requires
4. Extracts the model's reply and returns it at the JSON path SPLX's "Response Path" field expects

**Cost of the workaround:** Not large (a few hundred lines, standard token-refresh pattern), but it is unavoidable engineering work, not configuration — this is the primary reason "point-and-click" scanning only cleanly covers the model-deployment layer (Azure OpenAI connector) and not the agent orchestration layer.

---

## 5. REST API Connector — Proxy Build Spec

Confirmed directly from `docs.probe.splx.ai/ai-red-teaming/probe/target/index/rest-api`:

- **Payload template**: You supply the HTTP request body as a template containing exactly two required placeholders — `{message}` (Probe substitutes each attack prompt here) and `{session_id}` (Probe substitutes a unique per-conversation identifier here). Additional static/fixed fields can be added to the payload alongside these.
- **Headers**: Configured as key/value pairs in the connector UI. Authorization headers are required for non-public APIs; OAuth is stated as an alternative option (mechanism/flow not detailed on this page). **UI quirk documented**: after filling a header's Key and Value fields, you must click "Add Header +" — it does not auto-save on blur.
- **Response parsing**: A **Response Path** field takes a JSON path pointing to where the chatbot's reply lives inside the response body — this is how Probe extracts the model's answer from whatever wrapper/envelope your endpoint returns.
- **Session lifecycle (optional)**: Separate **Open Session** and **Close Session** endpoint configs are supported for apps that manage session state via distinct calls rather than folding it into every message call.

**What a proxy needs to do to satisfy this contract:**
1. Accept a POST with a body matching whatever template you configure in SPLX (containing the literal placeholder text SPLX will substitute)
2. Read the message and session_id from that body, re-package into the Foundry agent's actual API shape (thread/run/message or whatever the Hosted/Workflow Agent expects)
3. Attach a fresh Entra bearer token (or the agent's Managed Identity-scoped credential) to the outbound call to Foundry
4. Return a JSON response with the model's reply at a stable, documented path (so the Response Path field in SPLX can be set once and left alone)
5. Optionally implement Open/Close Session endpoints if the Foundry agent surface requires explicit session start/teardown

This is a standard reverse-proxy/adapter pattern — not novel, but not zero-effort either.

---

## 6. Content Filter Interference — Test Validity Risk

**Confirmed mechanism (from Microsoft's own content-filter-configurability doc, fetched directly):**
- Default Foundry model deployments ship with content filtering **on by default** across four harm categories (hate, sexual, violence, self-harm) plus optional Prompt Shields (user-prompt attacks) and Indirect Attack (XPIA) detection.
- Severity threshold (which of Low/Medium/High triggers a block) **is self-service** — any customer can loosen or tighten it via sliders in the Foundry portal, no approval needed.
- **Full "No filters" or "Annotate only" modes require Limited Access Review approval** ("If approved" is explicitly footnoted in Microsoft's own configurability table, with a link to the "Azure OpenAI Limited Access Review: Modified Content Filters" application form).
- A Microsoft Q&A community thread (secondary, not primary-doc-confirmed) states that becoming an approved "managed customer" for that review is **not currently possible** — treat this specific claim as **Reported**, not Confirmed, since it wasn't found verbatim on the primary Learn page.

**Practical implication for SPLX Probe scans:** If a scan targets a standard Foundry model deployment with default filters active, some attack payloads will be blocked at the platform layer (HTTP 400 with `content_filter` error, or `finish_reason: content_filter`) before the underlying model ever "sees" or responds to them. A naive read of Probe's results could then misattribute platform-layer blocking to model-layer robustness — a false "secure" result, exactly as the task brief anticipated.

**How to handle this — no confirmed SPLX-specific guidance found.** No SPLX doc or practitioner account fetched in this pass discusses how Probe scan results distinguish "blocked by Azure Content Safety" vs. "model refused" vs. "model complied." This is an **open question**, not resolved this pass. The generically-available Microsoft-side workaround is:
- Loosen severity thresholds to their maximum permissiveness (self-service, no approval) on a **dedicated test deployment** — do not touch the production deployment's filter config.
- Full off/annotate-only would give the cleanest signal but is gated behind an approval process that, per current guidance, is not realistically obtainable right now for most organizations — so this option should be treated as **effectively unavailable** for planning purposes.
- Practitioner accounts specifically describing "red-teaming Azure OpenAI with filters on vs off" were **not found** in this search pass despite a dedicated search attempt — this remains a genuine coverage gap, not just an assumption.

---

## 7. SPLX Probe vs. Foundry AI Red Teaming Agent (PyRIT)

| Dimension | SPLX Probe | Foundry AI Red Teaming Agent (PyRIT) | Verdict |
|---|---|---|---|
| Status | GA, commercial, self-serve trial live (110 credits) | **Still public preview** as of this research date — Confirmed, no GA date found | SPLX is production-ready today; Microsoft's native tool is not GA |
| Attack library | 5,000+ purpose-built, domain-specific attack simulations per current SPLX marketing copy (up from "25+ probe categories, thousands of attempts" framing in prior report — figures likely refer to different counting units, treat both as vendor-stated) | 20+ reusable attacker strategies via PyRIT orchestration | SPLX claims broader library; PyRIT is open-source and extensible by engineering effort |
| Native Foundry integration | None — external tool, connects via API/endpoint | Native — runs inside Foundry, integrates directly with Foundry Evaluations and tracing | PyRIT wins on native integration and observability |
| Cost | Free trial (110 credits, 2 probes); Professional/Enterprise tiers, contact sales for pricing | Free, open-source, included with Foundry | PyRIT wins on cost; SPLX requires a paid tier beyond a small trial for real coverage |
| Test-to-policy pipeline | Policy Generator auto-converts findings to guardrail policy (unique to SPLX) | No automatic policy generation from red-team findings | SPLX unique differentiator, unchanged from prior report |
| Runtime enforcement tie-in | Via Zscaler AI Guard (requires Zscaler infrastructure) or SPLX's own Runtime Protection API | None natively — pairs with Foundry's native Guardrails | SPLX's story only completes with Zscaler infrastructure in the loop |
| Agentic/multi-step workflow coverage | Not independently verified this pass | Explicitly extended to cover "agentic risks" per Microsoft Foundry Blog (Confirmed via devblog title) | Both claim agentic coverage; depth not compared this pass |

**Sharpened buy-vs-native take:** PyRIT is free, native, and now explicitly agent-aware, but is still preview-stage and requires more hands-on engineering to run and interpret. SPLX is commercially mature, has the unique test→policy automation, but its clean integration story stops at the model-deployment layer for Foundry specifically — going further (agents) costs proxy-building effort on both tools, so the "SPLX is turnkey" pitch weakens once you're past raw model endpoints.

---

## 8. Runtime Guardrail Path — Current Status

**Resolved, not open anymore.** The Foundry third-party guardrails BYOL page names exactly two partners as of this research date: **Palo Alto Networks Prisma AIRS** (with a full worked Python code example showing a blocked response tagged `"provider_name": "Palo Alto Networks Prisma AIRS"`) and **Zenity**. SPLX/Zscaler does not appear anywhere on the page, in the region-availability table, or in the onboarding-steps table. This is a **Confirmed negative** — the prior report's "not confirmed as a named partner" now reads as "confirmed not a named partner." There is no indication in the fetched page of a roadmap or pending-partner note for SPLX/Zscaler.

The only remaining native-Foundry runtime path for SPLX-originated policy is via **Zscaler AI Guard** — a separate Zscaler product, external to Foundry's own guardrail UI — which requires Zscaler infrastructure sitting in front of traffic (confirmed unchanged from prior report; Zscaler AI Guard integration doc confirmed to describe tenant-UUID mapping between SPLX Platform and Zscaler AI Guard, with no Azure/Foundry-specific mention in the doc itself).

---

## 9. Recommended Pilot Path

1. **Model-deployment scan (same-day, near-zero cost)** — Create a free SPLX trial account (110 credits, 2 probes) at `probe.splx.ai/auth/sign-up`. Configure the Azure OpenAI connector against a Foundry model deployment's endpoint, API key, and deployment name. Run 2 probes (recommend prompt injection + system prompt leakage, since these are SPLX-unique relative to Foundry's native stack per the gap table in the prior report). This validates the one connector path that is fully documented, requires zero engineering, and has no auth ambiguity.

2. **Set up a dedicated test deployment with loosened (not off) content filters** — Before or alongside step 1, create a separate Foundry model deployment (not your production one) and use the self-service severity sliders to set thresholds to their most permissive setting. Do not attempt to pursue full off/annotate-only mode — per current guidance this requires Limited Access Review approval that is reportedly not obtainable right now; budget zero time against that path unless you independently confirm otherwise with Microsoft.

3. **Compare scan results between default-filtered and loosened-filter deployments** — Run the same probe set against both. Any attack that "fails" against the default deployment but "succeeds" against the loosened one is evidence of platform-layer masking, not model robustness. This directly tests the content-filter-interference risk flagged in Section 6 with your own data, since no external practitioner account confirming this pattern was found.

4. **Attempt the OpenAI Assistant connector against a Foundry Prompt Agent as a quick falsifiable test (1-2 hours)** — Low expected success given the connector's lack of Azure/Entra fields (Section 3), but cheap to disprove. If it fails, this confirms the proxy requirement rather than leaving it as pure inference.

5. **Build the REST API proxy only if step 4 fails and agent-level (not just model-level) coverage is required** — Use the exact contract in Section 5. This is the highest-effort, highest-payoff step; sequence it last so it's only built if genuinely needed.

6. **Fallback if the whole SPLX path stalls on auth**: pilot the Foundry AI Red Teaming Agent (PyRIT) instead, since it is free, native, avoids the auth-bridging problem entirely (it runs inside the Foundry trust boundary), and is explicitly agent-aware — at the cost of being preview-stage and more manual to operate. This is a legitimate parallel or fallback track, not just a consolation prize, particularly for testing surfaces (Hosted/Workflow Agents) where SPLX has no clean auth path today.

---

## 10. Open Questions

| # | Gap | Why It Matters | How to Resolve |
|---|---|---|---|
| 1 | Where did SPLX's AI Runtime Protection "getting started" documentation move to (prior URL now 404s)? | Needed to independently re-verify the Runtime Protection architecture claims from the prior report — this pass could not re-confirm them | Query the docs site's own search/ask interface directly, or contact SPLX support/sales |
| 2 | Does the OpenAI Assistant connector actually work against a live Foundry Prompt Agent, or does it fail outright on auth/routing? | Determines whether any SPLX connector reaches the agent layer without custom proxy work | Hands-on test (Section 9, Step 4) — no vendor doc will resolve this, must be empirically tested |
| 3 | Exact TTL behavior and whether SPLX's REST API connector's "OAuth" option supports a full client-credentials refresh flow suitable for a long-running scan | Determines whether a hand-built proxy is unavoidable or whether SPLX's OAuth support already solves it | Direct test against SPLX support, or trial-account experimentation with the REST connector's OAuth config |
| 4 | Do practitioners report false "secure" scan results caused by native content filters, and how do they typically detect/correct for it? | This was explicitly flagged as a risk but no practitioner accounts were found in this pass despite targeted searching | Search AI security practitioner communities directly (LinkedIn AI security groups, r/cybersecurity, OWASP LLM Top 10 community channels) — general web search did not surface first-hand accounts |
| 5 | Exact current auth model for the Copilot Studio connector when the target agent is one published to/through Foundry rather than through Copilot Studio's own runtime | Copilot Studio is one of the few named connectors and could be a cleaner path than the REST proxy for that specific agent type | Direct test with a Copilot Studio agent published to Foundry; docs page for this specific connector was not fetched this pass |
| 6 | Whether the exact "not possible to become a managed customer" wording appears verbatim in any current primary Microsoft document (only found via community Q&A this pass) | Affects how firmly this claim can be represented to stakeholders as an official Microsoft position vs. community-reported | Search Microsoft Learn / Azure docs directly for the Limited Access Review application form's own eligibility page, if one exists beyond the linked form |

---

## 11. Sources

| # | Source | Type | Credibility | What It Established |
|---|---|---|---|---|
| 1 | docs.probe.splx.ai/ai-red-teaming/probe/target/index | SPLX official docs | High | Current full connector list — resolved the connector-list verification question directly |
| 2 | docs.probe.splx.ai/ai-red-teaming/probe/target/index/azure-openai | SPLX official docs | High | Azure OpenAI connector config fields — re-confirmed prior report |
| 3 | docs.probe.splx.ai/ai-red-teaming/probe/target/index/openai-assistant | SPLX official docs | High | OpenAI Assistant connector fields; confirmed no Azure/Entra/Foundry references |
| 4 | docs.probe.splx.ai/ai-red-teaming/probe/target/index/rest-api | SPLX official docs | High | Full REST connector payload/header/response-parsing spec — basis for Section 5 |
| 5 | docs.probe.splx.ai/ai-runtime-protection/getting-started | SPLX official docs | N/A — 404 | Confirmed URL no longer resolves; flagged as open question |
| 6 | docs.probe.splx.ai/sitemap.md | SPLX official docs | High | Site structure check for Runtime Protection docs — did not locate current location |
| 7 | docs.probe.splx.ai/ai-red-teaming/remediation/policy-generator/zscaler-ai-guard | SPLX official docs | High | Zscaler AI Guard integration mechanism — confirmed no Foundry-specific mention |
| 8 | learn.microsoft.com/en-us/azure/foundry/guardrails/third-party-integrations | Microsoft Learn official | High | **Resolved the highest-value open question** — current named partner list (Prisma AIRS, Zenity only) |
| 9 | learn.microsoft.com/en-us/azure/foundry-classic/foundry-models/concepts/content-filter | Microsoft Learn official | High | Full content-filter configurability table — basis for Section 6 and the Limited Access Review verification |
| 10 | Microsoft Q&A: "Managed customers - Azure Open AI Content Filter" (via WebSearch aggregation) | Microsoft community Q&A | Moderate (secondary, community-authored but MS-hosted) | Source for "not currently possible to become a managed customer" — labeled Reported, not Confirmed |
| 11 | probe.splx.ai/auth/sign-up; AWS Marketplace SplxAI Probe listing (via WebSearch) | Vendor self-serve signup / marketplace listing | Moderate | Confirmed trial tier (110 credits) and tiered pricing structure still live post-acquisition |
| 12 | learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry; team400.ai blog (via WebSearch) | Microsoft Learn + third-party engineering blog | High (Learn) / Moderate (blog) | Confirmed Entra-first direction of Foundry auth guidance |
| 13 | learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents (via WebSearch summary) | Microsoft Learn official | High | Confirmed per-agent Entra identity design for Hosted Agents — basis for Section 4's auth-problem claim |
| 14 | devblogs.microsoft.com/foundry/ai-red-teaming-agent-preview/; learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent (via WebSearch) | Microsoft Foundry Blog + Learn | High | Confirmed AI Red Teaming Agent (PyRIT) still in public preview, not GA |
| 15 | techcommunity.microsoft.com/.../deploying-foundry-hosted-agents-via-rest-api (attempted fetch, page text unavailable) | Microsoft Tech Community | N/A — fetch failed | Attempted but did not yield usable content; flagged as an unresolved gap, not used as a source of claims |

