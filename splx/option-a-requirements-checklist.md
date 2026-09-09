# Option A — Requirements Checklist (SPLX REST + OAuth direct)

**Date:** 2026-07-14 · **Status (2026-07-16):** Option A is a *candidate*, not the decided path — the
overall decision is **undefined pending a team meeting** (see [options map](splx-integration-options-2026-07-14.md)
§0). This doc remains the tick-off list of everything needed to execute Option A *if it is chosen*; §8 of
the options map has the execution steps.
**Legend:** 🟢 = you can gather yourself · 🔴 = needs admin help
**Status marks:** ☐ = you still need to go get / confirm this value in your account · ✅ = the *value or
shape is now known from the docs* (nothing left to look up — you just plug it into SPLX). **Note:** ✅
does **not** mean live-verified. The research agent read Microsoft's public docs only — it never touched
your portal or environment. For the ☐ items you must still manually open the portal / run `az`; the
"Where to find it" column tells you the exact place. One smoke-test call (see bottom) verifies the ✅
items against your actual workflow.

**The one-line summary:** only **3 items need help** (a service principal + its RBAC role — really one
request). The other **11 you can gather yourself**, mostly by reading values from the Foundry portal.

---

## Group 1 — OAuth credentials (the login half)
*These fill SPLX's OAuth form.*

| ☐ | # | Requirement | Value / example | Where to find it (exact) | Captured value | Source link |
|---|---|---|---|---|---|---|
| ✅ | 1 | **Entra tenant ID** | a GUID | 🟢 **Azure Portal** → search "Microsoft Entra ID" → **Overview** → copy **Tenant ID**. Or run `az account show --query tenantId -o tsv`. | `f5b8eabf-97d1-4285-a259-ff8f7cab96b7` | [Entra ID Overview](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview) |
| ✅ | 2 | **Token endpoint URL** | `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token` | 🟢 **Nothing to look up** — paste your tenant ID from #1 into this template. | `https://login.microsoftonline.com/f5b8eabf-97d1-4285-a259-ff8f7cab96b7/oauth2/v2.0/token` | [OIDC discovery doc (live-verified)](https://login.microsoftonline.com/f5b8eabf-97d1-4285-a259-ff8f7cab96b7/v2.0/.well-known/openid-configuration) |
| ☐ | 3 | **Service principal — Client ID** | app registration identifier (GUID) | 🔴 **From admin.** (They read it: Entra ID → **App registrations** → the new app → **Overview** → Application (client) ID.) |  |  |
| ☐ | 4 | **Service principal — Client Secret** | confidential key paired with the Client ID | 🔴 **From admin.** (Generated once at Entra ID → App registrations → app → **Certificates & secrets**; only shown at creation.) |  |  |
| ☐ | 5 | **RBAC role assigned** to that SP | *Azure AI Developer* (or equivalent) on `tatum-safeagents` | 🔴 **From admin.** (They set it: the `tatum-safeagents` resource → **Access control (IAM)** → Add role assignment.) |  |  |
| ☐ | 6 | **Scope** | `https://ai.azure.com/.default` | 🟢 **Nothing to look up** — fixed constant, confirmed in Foundry auth docs. |  |  |

## Group 2 — Connector / routing values (the "reach the workflow" half)
*These fill SPLX's REST connector fields.*

| ☐ | # | Requirement | Value / example | Where to find it (exact) | Captured value | Source link |
|---|---|---|---|---|---|---|
| ✅ | 7 | **Foundry responses endpoint URL** | `POST https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents/openai/v1/responses` (no `api-version` needed) | 🟢 **Value known from docs** — it's your project endpoint (#12) + `/openai/v1/responses`. No lookup, but confirm the base against **Foundry portal → project Overview → Endpoint**. Source: [runtime-components docs](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components). |  |  |
| ☐ | 8 | **Workflow name** | `safe-agents` | 🟢 **Foundry portal** (ai.azure.com) → **Agents / workflows** list → the workflow's name. |  |  |
| ☐ | 9 | **Current workflow version** | captured as `41` — **confirm current** | 🟢 **Foundry portal** → open the `safe-agents` workflow in the visualizer → **Version dropdown**, immediately left of the **Save** button. Docs confirm this is the ground truth for workflow-type agents. |  |  |
| ✅ | 10 | **Payload shape** — `agent_reference` at **top level** (sibling to `input`): `{"input":"{message}","agent_reference":{"name":"safe-agents","type":"agent_reference"}}`. ⚠️ `version` field not in any official sample — test with/without. | 🟢 **Shape known from docs** — you build this in SPLX's body-template field; nothing to look up. Source: [runtime-components docs](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components), REST tab. |  |  |
| ✅ | 11 | **Response Path** → `output_text` (flat top-level string). Non-streaming is default — never send `"stream":true`. | 🟢 **Value known from docs** — enter `output_text` in SPLX's Response Path field. Confirm live via the smoke test. Source: [Responses API docs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses). |  |  |

## Group 3 — Environment / liveness

| ☐ | # | Requirement | Value / example | Where to find it (exact) | Captured value | Source link |
|---|---|---|---|---|---|---|
| ☐ | 12 | **Project endpoint URL** | `https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents` | 🟢 **Foundry portal** → project **Overview** page → **Endpoint** field. Confirm it matches the value shown here. |  |  |
| ☐ | 13 | **Resource / project name** | `tatum-safeagents-resource` / `tatum-safeagents` (confirmed) | 🟢 **Foundry portal** → **Overview** (top of page shows resource + project name). Already confirmed. |  |  |
| ☐ | 14 | **Confirm environment is live** | `provisioningState = Succeeded`, or a `200` from a test call | 🟢 **Three ways:** (a) **Portal** → resource Overview shows status; (b) `az cognitiveservices account show --name tatum-safeagents-resource --resource-group <rg> --query "{state:properties.provisioningState,endpoint:properties.endpoint}"`; (c) **best** — the smoke-test curl below (proves liveness + auth + call shape at once). |  |  |

---

## The single admin ask (unblocks items 3, 4, 5)

> "Please create a service principal for the SPLX/Foundry testing, and assign it the **Azure AI
> Developer** role (or the equivalent) on the `tatum-safeagents` project. I need the **Client ID** and a
> **Client Secret** returned."

Ask for the identity **and** the role in the same request — a service principal that authenticates but
has no role produces a silent **"authenticated but denied"** failure, the most common trap.

---

## SPLX OAuth form → value mapping (quick reference)

| SPLX OAuth field | Value to enter |
|---|---|
| URL | `https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token` |
| Client ID | service principal Client ID (item 3) |
| Client Secret | service principal secret (item 4) |
| Scope | `https://ai.azure.com/.default` (item 6) |

---

## Open risks to watch (where we may learn we need a thin proxy)

*Updated 2026-07-15 after Foundry-docs research ([findings](foundry-docs-option-a-findings-2026-07-15.md)).*

- **~~Item 10 — flat payload can't express `agent_reference`?~~ RESOLVED.** `agent_reference` is a top-level
  body key; SPLX's flat template can carry it. See item 10 above.
- **~~Item 11 — flat Response Path vs. streamed reply?~~ RESOLVED.** Non-streaming is the default;
  `output_text` is a flat path. No SSE problem as long as `"stream":true` is never sent.
- **🔴 NEW [HIGH — blocking] Session/conversation ID.** Foundry's `conversation` field needs a
  **server-generated ID** from a separate `POST /openai/v1/conversations` call — it rejects an arbitrary
  client string. SPLX's flat `{session_id}` placeholder can't do the two-step flow. Untested workaround:
  run stateless (`store:false`, omit `conversation`) if SPLX doesn't need true multi-turn memory. **If it
  fails, this is what forces a thin proxy (Option B).** Test against `tatum-safeagents-resource` first.
- **🟡 NEW [MODERATE] `agent_reference.version` undocumented.** Our captured code has `version`; no official
  sample does. Test the call with and without it.
- **🟡 NEW [MODERATE — contested] HTTP 431 report.** One unconfirmed community report of HTTP 431 on this
  exact endpoint pattern (one region). Rule it out with an early smoke test before full connector build.
- **HITL Question node** — may stall the automated scan (options map §3, Gap #3).
- **Token TTL** — Entra tokens (~60–90 min) may expire mid-scan on long runs (Gap #5).

If auth (Group 1) succeeds but any of the above blocks routing/response, the result is *not* failure —
it tells us we need only a **thin proxy** (Option B) or SPLX's Proxy Interface (Option C), not a full
build.

---

## Minimum subset to prove "can we make one call?"

Items **1, 3, 4, 5, 8, 9, 12, 14** — i.e. the tenant + the service principal (with role) + the workflow
name/version + a live endpoint. Everything else refines the scan once a single call succeeds.
