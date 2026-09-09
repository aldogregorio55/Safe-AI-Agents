# SPLX → Foundry — Handoff Pack for the Enterprise-Access Holder

**Date:** 2026-07-13
**Purpose:** You do not hold SPLX enterprise access. A colleague does. This pack gives you (a) a depth understanding of how SPLX points at Foundry so you can direct the work, and (b) a fill-in intake sheet you hand the colleague so they configure the scan without coming back to you for missing details.
**Sources:** `research-analyst-splx-foundry-integration-verified-2026-07-13.md` (verification pass) + `research-analyst-splx-foundry-integration-2026-06-15.md` (original).

---

## Part 0 — The one-paragraph mental model

SPLX does not "integrate" with Foundry. SPLX is a scanner that sends thousands of attack prompts at an **endpoint** and reads the replies. "Pointing SPLX to Foundry" = giving SPLX an endpoint URL, a credential, and a model/agent identifier, then telling it which attacks to run. The entire difficulty is in *which* Foundry surface you point at and *what credential that surface accepts*. Everything below is about getting those inputs exactly right so the colleague's configuration is a copy-paste job, not a debugging session.

---

# PART 1 — How the Pointing Actually Works (depth)

## 1.1 The two surfaces you can point at, and why it matters

Foundry is not one endpoint. It has layers, and SPLX reaches them differently:

| Layer | What it is | SPLX connector | Credential it accepts | Difficulty |
|---|---|---|---|---|
| **Model deployment** | The raw model (GPT-4o etc.) deployed in Foundry, exposed as an Azure OpenAI endpoint | **Azure OpenAI** (native, documented) | **API key** — native fit | **Easy. This is the whole win.** Point-and-click. |
| **Agent** (Prompt / Hosted / Workflow Agent) | Your actual built agent — system prompt + tools + orchestration | No clean native connector | **Entra ID token** — SPLX has no field for this | **Hard.** Requires a custom proxy. Do not attempt in v1. |

**The single most important thing to understand:** the clean, documented, same-day path only reaches the **model deployment layer**. It tests the model + your system prompt against attacks. It does **not** test your agent's tools, memory, or orchestration. That's a real limitation, not a technicality — but it's still a genuinely useful test, because prompt injection and system-prompt-leakage happen at the model+prompt layer.

## 1.2 Why the agent layer is blocked (so you can explain it)

Microsoft designed Foundry Agents to authenticate with **Entra ID / Managed Identity** — each Hosted Agent gets its own Entra identity, and Microsoft explicitly discourages static API keys. SPLX's connectors are **API-key/bearer-token shaped**. There is no field anywhere in SPLX's Azure OpenAI, OpenAI Assistant, or REST connectors for an Entra client-credentials flow.

Result: to scan an agent, someone has to build a small proxy that holds a service-principal credential, refreshes the Entra token, accepts SPLX's request format, and translates it into the agent's call. A few hundred lines. That's engineering work, and it belongs in a v2, not the first pilot. (Spec is in Part 3 if it comes to that.)

## 1.3 The trap that makes a scan lie to you

Foundry model deployments ship with **content filtering on by default** — Prompt Shields, Content Safety across four harm categories. During a SPLX scan, some attack prompts get **blocked by Azure's filter before the model ever sees them**. SPLX records that as the attack failing. You read the report and conclude "the model is secure."

Wrong. The *filter* stopped it, not the model. If the filter is ever loosened, bypassed, or the model is reused elsewhere, you're exposed and your report told you the opposite.

**How to defeat the trap:** scan **two deployments** of the same model and compare.
- Deployment A: production-default filters.
- Deployment B: a throwaway test deployment with the content-filter severity sliders pushed to their **most permissive** setting (self-service in the Foundry portal, no approval needed).

Any attack that "fails" on A but "succeeds" on B = the filter was masking a real model weakness. That delta is the most valuable output of the whole exercise. (Full filters-*off* mode needs a Microsoft Limited Access Review that is reportedly not obtainable right now — don't chase it. Loosened sliders are enough.)

## 1.4 What SPLX actually runs, and which probes to pick

SPLX Probe fires prebuilt attack batteries. For a first scan, two probes give the most signal-per-credit:
- **Prompt injection** — the OWASP #1 LLM threat; tests whether embedded instructions override your system prompt.
- **System prompt leakage** — tests whether the model can be made to reveal its own instructions. *Foundry's native stack does not cover this at all*, so it's pure additive value — nothing you could've gotten free.

The free trial is 110 credits / 2 probes, which is exactly enough for this. Enterprise access (your colleague) removes that cap and unlocks the full library + Policy Generator.

---

# PART 2 — The Intake Sheet (hand this to the colleague)

This is what the colleague needs to configure the scan. **You gather everything in the left column from your Azure/Foundry tenant and hand it over filled in.** They should be able to paste it into SPLX's Azure OpenAI connector with zero questions back to you.

> Data-hygiene note: the API key is a live secret. Do **not** email it or drop it in chat. Share it via the firm's secrets manager / password vault, or have the colleague pull it from the portal themselves against a resource you've granted them read on. Everything else in the sheet is safe to send as text.

## 2.1 Connector: use **Azure OpenAI**

Tell the colleague explicitly: *use the **Azure OpenAI** target connector, not "OpenAI" and not "OpenAI Assistant."* Wrong connector = wrong auth fields = failure.

## 2.2 Fields to fill in

| # | SPLX field | What to put | Where you get it | Example shape |
|---|---|---|---|---|
| 1 | **Endpoint (URL)** | Your Foundry resource's Azure OpenAI endpoint | Azure Portal → your Foundry/AOAI resource → **Keys and Endpoint** | `https://<resource-name>.openai.azure.com` |
| 2 | **API Key** | One of the two resource keys (share via vault, not text) | Same page → **Keys and Endpoint** → Key 1 or Key 2 | `a1b2c3...` (redact in the sheet; deliver separately) |
| 3 | **Deployment Name** | The name of the *test* deployment (Deployment B, loosened filters) | Foundry portal → **Deployments** → the deployment's name | `gpt-4o-redteam-test` |
| 4 | **System Prompt** | The exact system prompt your app/agent uses in production | Your prompt artifact (versioned file) | *(paste full text)* |
| 5 | **API Protocol** | Which API the app calls | You decide based on your app: Chat Completions or Responses API | `Chat Completions` |
| 6 | **API Version** | The Azure OpenAI API version | Your app config / Azure OpenAI docs | e.g. `2025-05-01` |

## 2.3 Two-deployment setup (do this before handing over)

For the content-filter-trap defense in §1.3, you need to create the test deployment yourself (or have infra do it) **before** the colleague scans:

1. In Foundry, deploy the same model again under a new name (e.g. `gpt-4o-redteam-test`).
2. On that deployment, open content-filter config → set every severity slider to the **most permissive** level. Self-service, no approval.
3. Leave production alone.
4. Give the colleague **both** deployment names (production + test) so they can run the same probe set twice and hand you the comparison.

## 2.4 Scan instructions for the colleague

Spell these out so nothing is assumed:
- **Probes to run:** Prompt Injection + System Prompt Leakage (add Jailbreak + Off-topic if credits/enterprise allow).
- **Run against both deployments** (production-filtered and test-loosened), same probe set, so results are comparable.
- **What to return to you:** the raw findings export + attack-success-rate per category, per deployment. Ideally the Analyze-with-AI summary too. If they have Policy Generator (enterprise), ask for the generated guardrail policy as well — that's the artifact that shows what remediation would look like.

## 2.5 Pre-flight checklist (tick before you hand over)

- [ ] Endpoint URL copied, correct resource
- [ ] API key staged in vault (not pasted in the sheet)
- [ ] Production deployment name recorded
- [ ] Test deployment created, filters loosened, name recorded
- [ ] Exact production system prompt pasted in
- [ ] API protocol + version confirmed against actual app config
- [ ] Probe list specified
- [ ] "Run against both, return per-deployment breakdown" instruction included

---

# PART 3 — If You Later Need the Agent Layer (v2, don't start here)

Only relevant once model-deployment scanning is proven and you need to test the *agent* (tools/orchestration), not just the model.

**The blocker:** SPLX can't do Entra auth. **The workaround:** a proxy the colleague points SPLX's **REST API** connector at instead of Azure OpenAI.

The proxy must:
1. Expose a static HTTPS endpoint + a fixed API key (something SPLX's REST connector can authenticate against).
2. Accept SPLX's POST body containing the two required placeholders it substitutes: `{message}` (the attack prompt) and `{session_id}` (per-conversation ID).
3. Hold a service-principal credential and refresh an **Entra bearer token** on a schedule — a Probe run fires thousands of requests over a long window and will outlast a single token's TTL, so refresh is mandatory, not optional.
4. Repackage `{message}`/`{session_id}` into the Foundry agent's actual thread/run/message call, attach the fresh token.
5. Return the model's reply as JSON at a **stable path**, and tell the colleague that path so they set SPLX's **Response Path** field once (e.g. `data.reply`).
6. Optionally implement Open/Close Session endpoints if the agent needs explicit session start/teardown.

Cheap falsifiable test before building anything: have the colleague try the **OpenAI Assistant** connector (API key + Assistant ID) against a Foundry Prompt Agent. It will likely fail — the connector has no field for the Azure project endpoint — but a 1–2 hour failure converts "we think we need a proxy" into "we've proven we need a proxy," which is a stronger thing to put in front of whoever funds the build.

**Before funding that proxy, weigh the free native option:** Microsoft's **AI Red Teaming Agent (PyRIT)** runs *inside* Foundry, so the Entra auth problem disappears entirely, and it's agent-aware. It's still public preview and more manual to operate, but for agent-layer testing specifically it may beat building a proxy for a tool that can't natively reach agents anyway.

---

## The 30-second version to say to your colleague

"I need a SPLX Probe scan against a Foundry model deployment. Use the **Azure OpenAI** connector. Here's the endpoint, deployment name, system prompt, API protocol and version — key's in the vault. Run **prompt injection** and **system prompt leakage** against **two** deployments I've set up: one with production filters, one with filters loosened. Send me the per-deployment findings so I can see what the content filter was hiding. We're only testing the model layer this round — agents need a proxy we haven't built."
