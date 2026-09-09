# Research: Azure AI Foundry Responses API — Raw HTTP Details for SPLX REST Connector (Option A)

**Date:** 2026-07-15
**Confidence:** Moderate-High overall (most items High; one item Contested/Low — see #14a below)
**Sources:** 9 distinct Microsoft Learn / Azure CLI reference pages + 1 community Q&A (flagged as non-authoritative)

## Executive Summary

The exact raw-HTTP shape of `responses.create(extra_body={"agent_reference": {...}})` is directly documented on an official Microsoft Learn page with verbatim `curl` examples (item #7, #10, #11 all resolved with High confidence from a single primary source, cross-checked against a second official page). The biggest **open risk is not the URL or payload — it's session/conversation handling**: Foundry's `conversation` field requires a **server-generated conversation ID obtained from a separate `POST /openai/v1/conversations` call**; it does not accept an arbitrary client-supplied string. This directly conflicts with SPLX's single-POST-URL template model using a flat `{session_id}` placeholder, and is flagged as the top blocking risk for Option A. A second, lower-severity but still real risk: a community-reported HTTP 431 bug on this exact endpoint+payload pattern (unconfirmed, contested against the official docs which show it working via curl).

---

## #7 — Responses Endpoint URL

**Concrete value found:**

```
POST https://{resource_name}.services.ai.azure.com/api/projects/{project_name}/openai/v1/responses
```

For your environment, this resolves to:
```
POST https://tatum-safeagents-resource.services.ai.azure.com/api/projects/tatum-safeagents/openai/v1/responses
```

**No `api-version` query parameter is required or shown** on this endpoint in the official verbatim `curl` examples — this is the v1 GA OpenAI-compatible surface, where api-version is explicitly stated elsewhere in Microsoft's docs to no longer be required. This is *distinct* from the older `/agents` CRUD/management endpoint (used to create/version agents), which **does** require `?api-version=v1` in the same doc's own examples — do not confuse the two paths.

There is also a separate, unrelated **Agent Application (published agent)** endpoint pattern that *does* require an explicit `api-version` query param (`2025-11-15-preview` in the dated example) — that path is `/applications/{applicationName}/protocols/openai/responses` and is NOT what your captured SDK call uses (your call uses `agent_reference` against the plain project endpoint, not a published Agent Application). Do not use the Agent Application URL pattern for this integration unless you deliberately switch to that publishing model.

**Source:** [Build with agents, conversations, and responses in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components) (ms.date 2026-04-10, updated 2026-07-02) — contains verbatim REST tab curl examples for this exact endpoint.

**Confidence:** High. Directly sourced, verbatim curl example from an official, recently-updated page, and cross-checked against [Use the Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses) which confirms the `/openai/v1/responses` path pattern and its non-streaming default behavior independently.

---

## #10 — Payload Shape

**Concrete value found (verbatim from official REST example):**

```json
{
  "input": "What is the largest city in France?",
  "agent_reference": {
    "name": "your_agent_name",
    "type": "agent_reference"
  }
}
```

**`agent_reference` sits at the TOP LEVEL of the raw HTTP JSON body — not nested under `extra_body`.** `extra_body` is purely an SDK-side (Python OpenAI client) convenience parameter name for injecting non-standard fields; those fields get merged flat into the outgoing JSON. So for SPLX's raw body template, `agent_reference` is a sibling key to `input`, exactly as shown above.

For a session/conversation identifier, add a top-level `conversation` field (see #11 for the critical caveat on this):
```json
{
  "input": "{message}",
  "conversation": "{session_id}",
  "agent_reference": {
    "name": "safe-agents",
    "type": "agent_reference"
  }
}
```

**Version field gap:** The user's captured working code included `"agent_reference": {"name": ..., "version": ...}`, but every official code sample found (Python, C#, JavaScript, Java, REST — all five language tabs on the same page) shows `agent_reference` with only `name` and `type` fields — **no `version` field appears in any official sample**. This is a real, unresolved discrepancy: either (a) `version` is an accepted-but-undocumented optional field that pins to a specific agent version (plausible, since agents are versioned objects), or (b) omitting it always resolves to the latest/active version. **Flagged as an open gap** — recommend testing both with and without `version` against the actual `tatum-safeagents-resource` before finalizing the SPLX body template.

**Source:** [Build with agents, conversations, and responses in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components), REST API tab, "Generate a response with an agent" section.

**Confidence:** High for the top-level placement and base shape. Low/open-risk specifically for the `version` field's exact behavior (not documented).

---

## #11 — Response Path, Streaming

**Response JSON shape (verbatim from official example):**

```json
{
  "id": "resp_67cb32528d6881909eb2859a55e18a85",
  "created_at": 1741369938.0,
  "output_text": "Great! How can I help you today?",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        { "type": "output_text", "text": "Great! How can I help you today?" }
      ]
    }
  ]
}
```

**Response Path for SPLX:** `output_text` — a single flat top-level string field containing the assistant's full reply text. This is the simplest possible JSON path and requires no array indexing. (A more granular alternative, `output[0].content[0].text`, also works but is unnecessary given `output_text` exists.)

Note: when tool calls are involved (the workflow's constituent agents may use tools), `response.output` contains an array mixing `message`, `web_search_call`, `function_call`, `file_search_call` items — but `output_text` is documented as a convenience field that specifically surfaces the final assistant message text regardless of how many tool-call items precede it in `output`. This makes it a safe, stable target for SPLX even with a multi-agent workflow underneath.

**Streaming:** **Non-streaming is the default.** `stream` is an optional boolean parameter; when omitted (or set `false`), the endpoint returns a single JSON object exactly as shown above — **not SSE**. Streaming (SSE, `response.output_text.delta` events) only occurs if the caller explicitly sets `"stream": true`. Since SPLX's flat JSON-path parser needs a single JSON document, **simply never send `"stream": true` in the SPLX body template**, and the default non-streaming behavior applies cleanly. This is confirmed independently on two official pages (the responses how-to page explicitly shows `"stream": false` as the schema default, and the runtime-components page shows a separate explicit streaming code path only invoked when `stream=True` is passed).

**Sources:**
- [Use the Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses) — request/response schema, streaming optionality.
- [Build with agents, conversations, and responses in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components) — `output_text` field with agent_reference specifically, streaming code paths.

**Confidence:** High. This is the best-resolved item in the set — two independent official sources agree, and the non-streaming default directly removes the SSE concern SPLX would otherwise have.

---

## #9 — Workflow Version Confirmation

**Portal method (confirmed, official):** In the Foundry portal workflow visualizer, open the **Version** dropdown list immediately to the left of the **Save** button. Each save creates a new, unchangeable version, and the dropdown shows version history and lets you delete old versions.
Source: [Build a workflow in Microsoft Foundry (Preview)](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow).

**API/CLI method:** For standard prompt/hosted agents (not specifically confirmed for workflow-type agents — see gap below), version is returned directly by the agent creation/versioning call (`agent.version` in the Python SDK, or the `versions.latest` field in the `GET`/`POST` `/agents/{name}` REST response per the [Microsoft Foundry REST API reference — Agents](https://ai.azure.com/api-reference/agents)). A read-only confirmation would be:
```
GET {ENDPOINT}/agents/{agent_name}?api-version=v1
Authorization: Bearer <token>
```
returning an object whose `versions.latest` field carries the current version identifier.

**Open gap:** The REST reference confirms the `/agents` resource model supports `hosted`, `prompt`, `workflow`, or `external` definition kinds under one schema, which suggests workflow-type agents are versioned identically — but no official code sample explicitly demonstrates `GET /agents/{name}` or `agent_reference` invocation against a `"kind": "workflow"` agent specifically. All working examples found use `PromptAgentDefinition`/`kind: "prompt"`. Given Microsoft's own note that Foundry is retiring the visual workflow builder on **December 1, 2026** in favor of Agent Framework/hosted agents, workflow-specific REST tooling may be thinner than for prompt/hosted agents. **Recommend using the Portal Version dropdown as the reliable source of truth** for `safe-agents`' current version rather than relying on unverified REST behavior for workflow-kind agents.

**Confidence:** High for the portal method; Moderate (inference, not directly confirmed) for the REST/API method as applied specifically to a workflow-type agent.

---

## #14 — Liveness Check

**`az` CLI:**
```bash
az cognitiveservices account show \
  --name tatum-safeagents-resource \
  --resource-group <resource-group> \
  --query "{endpoint:properties.endpoint, state:properties.provisioningState}"
```
`provisioningState` should read `"Succeeded"`; `properties.endpoint` confirms the live base URL. This is a standard, generic Cognitive Services resource check (Foundry resources are `Microsoft.CognitiveServices/accounts`), documented via community/how-to guidance rather than a single canonical Learn page — cross-checked against two independent sources (an Azure Q&A thread on locating Foundry resources, and the general `az cognitiveservices account` command reference pattern), so treat as Moderate confidence on exact query syntax, though the underlying `az cognitiveservices account show` command and its `properties.provisioningState`/`properties.endpoint` fields are standard, well-established ARM resource fields.

**Portal:** Foundry portal (ai.azure.com) → resource Overview page shows endpoint, region, keys, and status directly.

**A concrete, project-scoped alternative** (more directly tied to your actual integration, sourced from an official page): issue a minimal `curl` against the responses endpoint itself with a trivial input and confirm HTTP 200 + a populated `output_text` — this simultaneously verifies liveness, auth, and the exact call shape in one step, using the pattern shown in item #7/#10 above. This is arguably a better liveness check for your purposes than a generic resource-level `az` command, since it tests the actual data-plane path you'll wire into SPLX.

**Note:** `az cognitiveservices agent show` / `list` / `list-versions` (from the preview `az cognitiveservices agent` command group) exist but are explicitly scoped to **hosted agents** (container-image-based), per the [az cognitiveservices agent CLI reference](https://learn.microsoft.com/en-us/cli/azure/cognitiveservices/agent?view=azure-cli-latest) — these do not apply to workflow-type or prompt-type agents and should not be used to check `safe-agents`' liveness/version if it isn't a hosted-container agent.

**Confidence:** Moderate. The resource-level `az cognitiveservices account show` liveness check is standard but not from a single canonical Learn page for this exact scenario; the project-scoped curl-based liveness check is High confidence since it's directly derived from the officially documented call shape.

---

## Auth Shape Sanity Check

**Token scope confirmed:** `https://ai.azure.com/.default` is explicitly documented as the correct Entra ID OAuth 2.0 bearer token scope for Foundry, stated identically in two independent official pages:
- [Authentication and authorization in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry): *"Microsoft Entra ID uses OAuth 2.0 bearer tokens scoped to `https://ai.azure.com/.default`."*
- [Agent applications in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-responses... — actually agent-applications.md, canonical URL learn.microsoft.com/.../agent-applications): shows `get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")` used directly against the responses endpoint.

**Bearer token acceptance confirmed:** All official REST examples authenticate with `Authorization: Bearer <token>` obtained via `az account get-access-token --resource https://ai.azure.com/ --query accessToken -o tsv` (or equivalently `DefaultAzureCredential().get_token("https://ai.azure.com/.default")`). `DefaultAzureCredential` transparently supports `ClientSecretCredential`/service-principal (Entra client-credentials flow) when the standard `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` environment variables are set — the token mechanics (Bearer header, scope) are identical regardless of whether the credential came from a user login, managed identity, or client-credentials flow, since Entra issues the same token shape for any of these flows against the same scope/resource. This last inference (that client-credentials specifically works, not just interactively-obtained tokens) is not shown in an explicit client-credentials code sample in the pages fetched, but follows directly from how `DefaultAzureCredential`/OAuth2 bearer auth works and is standard Azure practice.

**One distinct-scope trap flagged by search results (not independently verified via a fetched page):** a search snippet claimed `https://cognitiveservices.azure.com/.default` is used for "Azure Foundry" while `https://ai.azure.com/.default` is for "Azure AI services" — this appears to be either an error or referring to the older/classic Cognitive Services resource-level endpoint vs. the newer Foundry project endpoint. Given the two official pages fetched directly and independently both confirm `https://ai.azure.com/.default` for the Foundry data-plane/Responses API, **use `https://ai.azure.com/.default`** for this integration; the alternate scope claim is Low confidence and unverified against a primary source.

**Confidence:** High for `https://ai.azure.com/.default` being correct and Bearer-token-based; Moderate for the specific "client-credentials flow works identically" claim (sound inference, not an explicit official code sample using `ClientSecretCredential` against this exact endpoint).

---

## Knowledge Gaps / Open Risks (ranked by severity)

1. **[HIGH — blocking] Session/conversation ID cannot be client-generated.** Official docs show conversation continuity requires first calling `POST {ENDPOINT}/openai/v1/conversations` (a separate API call) to obtain a server-generated ID (e.g., `conv_abc123`), which is then passed as the top-level `conversation` field on subsequent `responses.create` calls. SPLX's flat REST connector supports one POST URL, one body template, and a `{session_id}` placeholder — it does not appear to support a two-step "create session, then use it" flow. If SPLX simply generates its own arbitrary string and drops it into `{session_id}` → `"conversation": "{session_id}"`, this will very likely fail (invalid/unknown conversation ID) unless Foundry silently create-or-attaches on unknown IDs (not documented, and inconsistent with "conversations are durable objects with unique identifiers" language). **Untested alternative:** omit `conversation` entirely and rely on `previous_response_id` chaining or client-side history replay (both require storing state SPLX's flat template isn't built for either), or treat each SPLX turn as fully stateless (`store: false`, no conversation field) — acceptable only if SPLX's red-teaming methodology doesn't require true multi-turn memory. **This needs a direct test against `tatum-safeagents-resource` before committing to a SPLX body template**, and if it fails, may require a thin proxy (e.g., Azure Function) between SPLX and Foundry that manages conversation creation server-side and maps `session_id` → real `conversation` ID.

2. **[MODERATE — contested] HTTP 431 report against this exact endpoint pattern.** A Microsoft Q&A community post ([Azure AI Foundry Agents - Project-scoped /openai/v1/responses endpoint returns HTTP 431 for ALL requests](https://learn.microsoft.com/en-za/answers/questions/5851051/azure-ai-foundry-agents-project-scoped-openai-v1-r)) reports the exact endpoint `POST https://<resource>.services.ai.azure.com/api/projects/<project>/openai/v1/responses` returns HTTP 431 (header fields too large) for all requests, unrelated to actual header size, with the reporter identifying it as a platform routing bug in one region (Central India), unresolved as of the report. This directly **contradicts** the official documentation, which shows this exact endpoint working via plain curl with only `Authorization` and `Content-Type` headers. This is a single, unverified, non-authoritative source (community forum, not Microsoft-confirmed) — flagged as Low/Contested confidence, but given it targets the precise endpoint+payload combination Option A depends on, **recommend a live smoke test against `tatum-safeagents-resource` early**, before building out the full SPLX connector, to rule this out for your specific resource/region.

3. **[MODERATE] `agent_reference.version` field behavior is undocumented.** See #10 above — no official sample shows a `version` key inside `agent_reference`, only `name` + `type`, despite the user's own working code including `version`. Needs empirical confirmation.

4. **[MODERATE] Workflow-type agent versioning/invocation via REST is not explicitly demonstrated.** All official `agent_reference`/versioning code samples use prompt-kind agents; workflow-kind agents are mentioned as a supported `definition.kind` in the REST schema but no worked example shows `GET`/version-check or `agent_reference` invocation specifically against a `"kind": "workflow"` agent. Given Foundry is retiring the visual workflow designer on 2026-12-01, this area of documentation may not receive further investment — rely on the Portal Version dropdown as the safer ground truth for now.

5. **[LOW] Exact liveness-check `az` command syntax for a Foundry resource** was cross-checked against community/search-summarized guidance rather than a single fetched canonical page — the underlying `az cognitiveservices account show` command and ARM field names (`properties.provisioningState`, `properties.endpoint`) are standard and reliable, but the specific query flags weren't verified against a dedicated Learn tutorial page.

---

## Time Sensitivity

This is a fast-moving preview surface. The `runtime-components.md` and `workflow.md` pages were both last updated **2026-07-02**, and `publish-responses`/`agent-applications.md` reflects a **"legacy publishing experience"** deprecation notice pointing to a newer agent endpoint model — meaning the Responses/Agents API surface is actively being restructured. The visual workflow designer specifically has an announced retirement date of **December 1, 2026**. Recommend re-verifying this research within 4-6 weeks if implementation is delayed, and treat any `(preview)` API version strings (e.g., `2025-11-15-preview`) as subject to change without notice.

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Build with agents, conversations, and responses in Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components) | Official (Microsoft Learn) | High |
| 2 | [Use the Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses) | Official (Microsoft Learn) | High |
| 3 | [Quickstart: Build agents using the Responses API](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api) | Official (Microsoft Learn) | High |
| 4 | [Agent applications in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-applications) | Official (Microsoft Learn, marked "legacy") | High (for what it covers), noted as legacy |
| 5 | [Build a workflow in Microsoft Foundry (Preview)](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow) | Official (Microsoft Learn) | High, but feature is being retired 2026-12-01 |
| 6 | [Authentication and authorization in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry) | Official (Microsoft Learn) | High |
| 7 | [Microsoft Foundry REST API reference — Agents](https://ai.azure.com/api-reference/agents) | Official (API reference) | High |
| 8 | [az cognitiveservices agent CLI reference](https://learn.microsoft.com/en-us/cli/azure/cognitiveservices/agent?view=azure-cli-latest) | Official (Azure CLI docs) | High (but scoped to hosted agents only) |
| 9 | [Azure AI Foundry Agents - Project-scoped /openai/v1/responses endpoint returns HTTP 431 for ALL requests](https://learn.microsoft.com/en-za/answers/questions/5851051/azure-ai-foundry-agents-project-scoped-openai-v1-r) | Community Q&A (Microsoft Q&A forum) | Low/unverified — single unresolved report |
