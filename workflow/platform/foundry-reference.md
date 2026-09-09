# Azure AI Foundry — Workflow Reference

**Created:** 2026-04-28  
**Last Updated:** 2026-04-28  
**Purpose:** Reference doc for building the Pain Point Analysis workflow in Microsoft Foundry  
**Source:** Microsoft Learn docs + portal observations

---

## 1. What We're Using: Workflow Agents (Preview)

Foundry Agent Service supports three agent types. We're using **Workflow Agents**:

| Type | Code Required | Orchestration | Best For |
|------|---------------|---------------|----------|
| **Prompt Agents** | No | Single agent | Prototyping, simple tasks |
| **Workflow Agents (Preview)** | No (YAML optional) | Multi-agent, branching | Multi-step automation — **this is us** |
| **Hosted Agents (Preview)** | Yes (container) | Custom logic | Full control, custom frameworks |

Workflow agents orchestrate a sequence of actions or coordinate multiple agents using **declarative definitions**. Build visually in the Foundry portal or define in YAML via VS Code. Supports branching logic, human-in-the-loop steps, and sequential or group-chat patterns.

**Key constraint:** Hosted agents are NOT supported in the workflow designer. Everything runs through the visual builder / YAML.

---

## 2. Workflow Patterns (Templates)

Foundry provides three built-in templates:

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Human in the loop** | Asks the user a question and awaits input to proceed | Approval requests, obtaining information from user |
| **Sequential** | Passes result from one agent to the next in defined order | Step-by-step workflows, pipelines, multi-stage processing |
| **Group chat** | Dynamically passes control between agents based on context/rules | Dynamic workflows, escalation, fallback, expert handoff |

**For our workflow:** We're likely using **Sequential** as the base pattern, with if/else branching to handle the Preparer ↔ Reviewer loop.

---

## 3. Workflow Node Types (Confirmed from Portal)

Nodes are the building blocks. Each performs a specific action in sequence. Add via the **+** icon → select category → select node. Reorder via three-dot menu → move.

### Invoke

| Node | What It Does | Our Use |
|------|-------------|---------|
| **Agent** | Use an agent to complete tasks | Core node — one per agent (Supervisor, Preparer, Reviewer, Formatter) |

### Data Transformation

| Node | What It Does | Our Use |
|------|-------------|---------|
| **Set Variable** | Set a variable value | Store agent outputs, set `ReviewCount`, pass data between agents |
| **Reset Variable** | Reset the value of a variable | Reset `ReviewCount` if re-running, clear intermediate outputs |
| **Parse Value** | Convert one data type into another | Extract structured data from agent text output (e.g., check if Reviewer said APPROVED) |

### Flow

| Node | What It Does | Our Use |
|------|-------------|---------|
| **If/Else** | Add conditional logic branching | Route based on Reviewer approval vs. feedback, check turn count |
| **For Each** | Set a node per item in a collection | Not needed for our workflow |
| **Go To Node** | Go to a specific node in this workflow | Loop Reviewer feedback back to Preparer |

### Basics

| Node | What It Does | Our Use |
|------|-------------|---------|
| **Deliver a Message** | Message user without reply | Return final JSON output to user |
| **Ask a Question** | Ask question, waits for an answer | HITL — present analysis to user for approval before formatting (optional) |
| **End** | End the workflow | Terminate after final output |

---

## 4. Agent Nodes — How They Work

When you add an "Invoke Agent" node:

1. **Select existing agent** or **create new** from within the workflow
2. Configure the agent's:
   - **Model** (e.g., GPT-5.4)
   - **Instructions** (system prompt)
   - **Tools** (file search, web search, code interpreter, MCP, custom functions)
   - **Output format** — can enforce JSON Schema output (critical for Formatter)

### Structured JSON Output
To configure JSON schema output on an agent node:
1. Select the agent node → Details → Parameter icon
2. Set **Text format** → **JSON Schema**
3. Paste the JSON schema
4. Under **Action settings** → **Save output json_object/json_schema as** → create a variable

This is how we force the Formatter to produce valid JSON per our `output-schema-v2.json`.

---

## 5. Variables and Data Flow

Variables are how data passes between nodes. Two scopes:

| Scope | Prefix | Example |
|-------|--------|---------|
| **System** | `System.` | `System.Conversation.Id`, `System.LastMessage.Text` |
| **Local** | `Local.` | `Local.PreparedAnalysis`, `Local.ReviewCount` |

### Key System Variables

| Variable | Description |
|----------|-------------|
| `System.LastMessage.Text` | Previous message sent by the user |
| `System.Conversation.Id` | Unique conversation ID |
| `System.Conversation.InTestMode` | Boolean — is this a test run? |

### Creating Variables
- Agent output → **Save output as** → create variable (stores agent response)
- **Set Variable** node → assign a literal or Power Fx expression
- Variables persist across the workflow run

---

## 6. Branching and Logic (Power Fx)

Conditions use **Power Fx** — a low-code, Excel-like formula language.

### If/Else Branching
- Add an if/else node
- Write condition in Power Fx (e.g., `Local.ReviewerDecision = "APPROVED"`)
- Route to different next nodes per branch

### Relevant Power Fx for Our Workflow

| Need | Formula |
|------|---------|
| Check if Reviewer approved | `StartsWith(Local.ReviewerOutput, "APPROVED")` or parse a variable |
| Track review turn count | `Local.ReviewCount + 1` (increment via Set Variable) |
| Force approval after turn 2 | `If(Local.ReviewCount >= 2, "APPROVED", Local.ReviewerOutput)` |
| String contains check | `"APPROVED" in Local.ReviewerOutput` |

---

## 7. Foundry Guardrails — Technical Reference

Foundry has its own guardrail system — separate from our prompt-level safety blocks. This section documents the full technical specification based on Microsoft documentation, covering what guardrails are, how they work, and what is/isn't configurable.

**Source:** [Guardrails overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview), [Intervention points](https://learn.microsoft.com/en-us/azure/foundry/guardrails/intervention-points), [Configure guardrails](https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails), [Content filtering (classic)](https://learn.microsoft.com/en-us/azure/foundry-classic/foundry-models/concepts/content-filter), [Configure content filters](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/content-filters)

---

### 7.1 Definition

A **guardrail** is a named collection of **controls**. Each control defines:

1. **A risk** to be detected (e.g., Violence, PII, Indirect attack)
2. **Intervention point(s)** to scan for the risk (e.g., user input, output)
3. **An action** to take when the risk is detected (Annotate, or Annotate and block)

Risks are flagged by classification models from [Azure AI Content Safety](https://azure.microsoft.com/products/cognitive-services/ai-content-safety). These are separate neural classifiers — not the LLM itself. Guardrail processing at each intervention point adds approximately **50–100ms** of latency.

A guardrail applies to all [models sold directly by Azure](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) (except audio models like Whisper). It currently applies only to agents built in the Foundry Agent Service, not to other agents registered in the Foundry Control Plane.

---

### 7.2 Intervention Points

Four intervention points define **where** in the request lifecycle guardrails scan content:

| Intervention Point | Description | Applies To | Status |
|--------------------|-------------|-----------|--------|
| **User input** | The prompt sent by the user to the model or agent | Models + Agents | GA |
| **Tool call** | The action and data the agent proposes to send to a tool (generated by the model) | Agents only | Preview |
| **Tool response** | The content returned from a tool back to the agent, before it enters the agent's memory | Agents only | Preview |
| **Output** | The final completion/response returned to the user | Models + Agents | GA |

**Tool call example (from docs):** When a control for Hate (High) is specified at the tool call intervention point, every time the agent proposes a tool call, the content being sent to the tool is scanned for hateful content. If detected, the tool call is not executed and the agent stops until the next user input.

**Tool response example (from docs):** When a control for Indirect Attack is specified at the tool response intervention point, the full payload returned from the tool is scanned for indirect prompt injection. If detected, the agent stops immediately — preventing malicious content from entering the agent's memory.

**Supported tools for tool call/response scanning:** Azure AI Search, Azure Functions, OpenAPI, SharePoint Grounding, Fabric Data Agent, Bing Grounding, Bing Custom Search, Browser Automation. **`file_search` is NOT on this list** — tool call/response controls will not take effect for `file_search`.

---

### 7.3 Risk Categories

| Risk | Description | Models | Agents | Default State |
|------|-------------|--------|--------|---------------|
| **Hate** | Discriminatory language targeting identity groups. Includes harassment, bullying. | ✅ | ✅ | On (Medium) |
| **Sexual** | Sexual language, nudity, pornography, abuse, exploitation. | ✅ | ✅ | On (Medium) |
| **Violence** | Physical violence, weapons, terrorism, stalking. | ✅ | ✅ | On (Medium) |
| **Self-harm** | Self-injury, eating disorders, bullying. | ✅ | ✅ | On (Medium) |
| **User prompt attacks** | Jailbreak attempts — user tries to circumvent system rules, change persona, generate encoded outputs. Binary classifier (detected/not detected). | ✅ | ✅ | On (Block) |
| **Indirect attacks (XPIA)** | Third-party malicious instructions placed inside documents the AI accesses. Requires document embedding with `<documents>` tags. | ✅ | ✅ | Off |
| **Protected material (text)** | Known copyrighted text (lyrics, articles, recipes, web content) in model output. | ✅ | ✅ | On (Block) |
| **Protected material (code)** | Source code matching public repositories. Returns citation URL + license if detected. | ✅ | ✅ | On (Block) |
| **Groundedness** | Model output not grounded in provided source material. Streaming only. | ✅ | ❌ (Preview) | Off |
| **PII** | Personally identifiable information in model output (names, addresses, SSNs, etc.). | ✅ | ✅ (Preview) | Off |
| **Spotlighting** | — | ✅ | ❌ (Preview) | — |
| **Task Adherence** | Agent deviates from user instructions — misaligned tool invocations, improper tool I/O, response inconsistent with input. | ✅ | ✅ | — |

---

### 7.4 Severity Levels

The four core content categories (Hate, Sexual, Violence, Self-harm) use a four-tier severity model:

| Severity | Description |
|----------|-------------|
| **Safe** | Annotated but never filtered. Not configurable — always passes. |
| **Low** | Flags content at low severity and above. **Most restrictive.** |
| **Medium** | Flags content at medium severity and above. **Default threshold.** |
| **High** | Flags only the most severe content. **Least restrictive.** |

Configurable severity range: Low → Medium → High.

**"Off" (no filters) requires Modified Content Filtering approval.** This approval is obtained via the [Limited Access Review form](https://ncv.microsoft.com/uEfCgnITdR). The docs note: *"At this time, it is not possible to become a managed customer."* This means filtering for the core four categories **cannot be fully disabled**.

**"Annotate only" also requires approval** — disables blocking but still runs the classifier and returns annotations via API.

All other risk categories (Prompt Shields, Protected Material, PII, Groundedness, Indirect Attacks) are binary on/off and do not use severity levels. These can be toggled by any customer.

---

### 7.5 Actions

| Action | Models | Agents | Behaviour |
|--------|--------|--------|-----------|
| **Annotate** | ✅ | ❌ | Classifier runs; results returned as annotations in the API response. Content is **not blocked**. |
| **Annotate and block** | ✅ | ✅ | Classifier runs; if risk exceeds threshold, content is **blocked**. Annotations still returned. |

**Agents only support "Annotate and block."** There is no annotate-only mode for agent guardrails. This means any control enabled on an agent guardrail will block on detection — there is no passive monitoring mode for agents.

---

### 7.6 Guardrail Assignment & Inheritance

Guardrails can be assigned at two levels:

1. **Model deployment** — a guardrail (content filter) is attached to the deployed model (e.g., GPT-5.4 deployment).
2. **Agent** — a guardrail is assigned directly to the agent in the workflow.

**Inheritance rules:**
- If a custom guardrail is assigned to an agent → that guardrail is used (fully replaces the model's guardrail).
- If no custom guardrail is assigned → the agent inherits the guardrail of its underlying model deployment.
- The agent only uses `Microsoft.DefaultV2` if its model deployment uses that guardrail, or if explicitly assigned.

> *"Risks are detected in an agent based on the guardrail it's assigned, not the guardrail of its underlying model. The agentic guardrail fully overrides the model's guardrail."*

**Override example (from docs):**
- Model: Violence at High for input + output
- Agent: Violence at Low for input + output, no Violence controls for tool call/response
- Result: User queries scanned at Low. Tool calls/responses NOT scanned for Violence. Output scanned at Low. The model's High setting is completely ignored.

---

### 7.7 Default Guardrail — `Microsoft.DefaultV2`

All deployments start with `Microsoft.DefaultV2`. It **cannot be edited**. To change behaviour, create a custom guardrail and assign it.

| Category | Severity | Action | Input | Output |
|---|---|---|---|---|
| Violence | Medium | Block | ✅ | ✅ |
| Hate | Medium | Block | ✅ | ✅ |
| Sexual | Medium | Block | ✅ | ✅ |
| Self-harm | Medium | Block | ✅ | ✅ |
| Prompt Shield (jailbreak / direct attack) | On | Block | ✅ | — |
| Prompt Shield (indirect attack) | Off | — | — | — |
| Protected material (text) | On | Block | — | ✅ |
| Protected material (code) | On | Block | — | ✅ |
| Groundedness | Off | — | — | — |
| PII | Off | — | — | — |

---

### 7.8 Creating & Managing Custom Guardrails

**Create:** Foundry portal → Build → Guardrails → Create Guardrail → Add controls (select risk, intervention points, action) → Assign to agents/models → Name → Create.

**Edit:** Custom guardrails can be edited. `DefaultV2` cannot. Core controls (Violence, Hate, Sexual, Self-harm on user input and output) can be **overridden** to a different severity but **cannot be deleted** — except by Managed Customers with Modified Content Filtering approval.

**Assign:** Via the guardrail wizard (add agents/models in step 2), or via the agent/model's playground (Guardrails section → Manage → Assign).

**Delete:** Remove all assigned models/agents first, then delete.

**Request-time override:** A custom guardrail can be specified per API call via the `x-policy-id` request header. This overrides the deployment-level configuration for that single call.

```bash
curl --request POST \
    --url 'URL' \
    --header 'x-policy-id: CUSTOM_CONTENT_FILTER_NAME' \
    --data '{"messages": [...]}'
```

---

### 7.9 Document Embedding for Guardrails

Certain guardrail features require documents to be tagged in the prompt using a specific format:

```
""" <documents>
*insert your document content here*
</documents> """
```

**Required by:**
- Indirect attacks (XPIA) detection — scans tagged documents for malicious instructions
- Groundedness detection — checks model output against tagged source material

Document content within the tags should be **JSON-escaped** (e.g., `\n` for newlines, `\u00E9` for special characters).

**Note:** `file_search` retrieval does not use this tagging format — the content is injected into the model's context by the platform, not by the user prompt. This means indirect attack detection configured at the tool response intervention point is the intended mechanism for scanning retrieved content, but `file_search` is not in the supported tools list for that intervention point.

---

### 7.10 Configurability Constraints

| What | Configurable? | Notes |
|------|---------------|-------|
| Core categories severity (Hate, Sexual, Violence, Self-harm) | Yes — Low / Medium / High | Cannot be turned Off without approval |
| Core categories deletion | No | Can only be overridden, not removed |
| Turning filters fully off | Requires approval | [Limited Access Review form](https://ncv.microsoft.com/uEfCgnITdR) — currently unavailable |
| Annotate-only mode (no blocking) | Models: yes. Agents: **no** | Agents only support "Annotate and block" |
| Prompt Shields | Yes — on/off, annotate/block | Jailbreak on by default; indirect attacks off by default |
| Protected material | Yes — on/off | On by default for both text and code |
| PII | Yes — on/off | Off by default (Preview) |
| Groundedness | Yes — on/off | Off by default (Preview, streaming only) |
| Task Adherence | Yes | — |
| DefaultV2 guardrail | **Not editable** | Must create a custom guardrail to change anything |

---

### 7.11 API Response — Annotations

When annotations are enabled, the API response includes `content_filter_results` for each risk category:

```json
{
  "content_filter_results": {
    "hate": { "filtered": false, "severity": "safe" },
    "sexual": { "filtered": false, "severity": "safe" },
    "violence": { "filtered": false, "severity": "safe" },
    "self_harm": { "filtered": false, "severity": "safe" },
    "protected_material_text": { "detected": false, "filtered": false },
    "protected_material_code": { "detected": false, "filtered": false }
  }
}
```

Input prompts include `prompt_filter_results` with the same structure plus `jailbreak` detection:

```json
{
  "prompt_filter_results": [{
    "content_filter_results": {
      "jailbreak": { "detected": false, "filtered": false },
      "hate": { "filtered": false, "severity": "safe" },
      ...
    }
  }]
}
```

When filtering is unavailable or fails, the response includes an error annotation:

```json
{
  "content_filter_results": {
    "error": {
      "code": "content_filter_error",
      "message": "The contents are not filtered"
    }
  }
}
```

When content is blocked on input, the API returns HTTP 400 with `"code": "content_filter"`. When content is blocked on output, `finish_reason` is set to `"content_filter"` instead of `"stop"` or `"length"`.

---

### 7.12 Implications for Safety Testing

| Consideration | Impact |
|---------------|--------|
| Core categories have a non-removable floor | Platform will always scan and potentially block content in Hate/Sexual/Violence/Self-harm at minimum High severity. Test inputs triggering these will be intercepted before prompt-level defenses see them. |
| No annotate-only mode for agents | Cannot passively monitor what agents trigger — every detection results in a block. |
| Prompt Shield (jailbreak) is on by default | Jailbreak test inputs may be caught at the user input intervention point before reaching the system prompt. |
| `file_search` not covered by tool call/response scanning | Retrieved document content is not scanned at the tool intervention points — only at the output point when the model generates a response from it. |
| Indirect attack detection requires `<documents>` tagging | XPIA payloads in `file_search` results may not be detected by the indirect attack classifier unless the content is also tagged in the prompt. |
| Guardrail adds ~50–100ms per intervention point | At minimum 2 intervention points active (input + output) = ~100–200ms per agent invocation. |
| **Decision:** Test with guardrails ON vs. minimised | Testing with guardrails minimised (all optional controls off, core at High) isolates prompt-level defense as much as the platform allows. Testing with guardrails at default shows combined defense posture. Both passes are needed. |

---

## 8. SDK Client — How the Script Works

The Python script triggers and streams a Foundry workflow:

```python
# Authenticate
project_client = AIProjectClient(
    endpoint="https://Aldo1.services.ai.azure.com/api/projects/AI-Agent-Safety",
    credential=DefaultAzureCredential(),
)

# Get OpenAI-compatible client
openai_client = project_client.get_openai_client()

# Create stateful conversation
conversation = openai_client.conversations.create()

# Trigger workflow with input
stream = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": workflow["name"], "type": "agent_reference"}},
    input="<transcript text>",
    stream=True,
)

# Process events as each workflow step executes
for event in stream:
    # RESPONSE_OUTPUT_ITEM_ADDED + workflow_action → step started
    # RESPONSE_OUTPUT_ITEM_DONE + workflow_action → step completed
    # RESPONSE_OUTPUT_TEXT_DELTA → streaming tokens
    # RESPONSE_OUTPUT_TEXT_DONE → full agent output
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Conversation** | Server-side stateful session — tracks all messages, handoffs, intermediate outputs |
| **Agent Reference** | Points to a workflow built in the portal — name + version |
| **Stream Events** | Real-time events as each workflow node executes |
| `action_id` | Identifies which workflow node/agent produced the event |
| `previous_action_id` | Links steps in execution order (trace the chain) |
| `status` | Node completion status |

### Event Types for Test Harness

| Event | Use |
|-------|-----|
| `RESPONSE_OUTPUT_ITEM_ADDED` + `workflow_action` | Log: which agent just started |
| `RESPONSE_OUTPUT_ITEM_DONE` + `workflow_action` | Log: which agent finished + status |
| `RESPONSE_OUTPUT_TEXT_DONE` | Capture: full output text from each agent |
| `RESPONSE_OUTPUT_TEXT_DELTA` | Optional: stream tokens in real-time |

---

## 9. Additional Foundry Features

### Versioning
- Every **Save** creates a new immutable version
- Version history accessible via dropdown next to Save button
- Can roll back to any previous version

### YAML View
- Toggle **YAML Visualizer View** to edit workflow as YAML
- Changes in YAML reflect immediately in the visual builder and vice versa
- Can author in VS Code with Foundry extensions

### Observability
- **Agent tracing:** Inspect every model call, tool invocation, and decision
- **Application Insights integration:** End-to-end metrics
- **Run traces** confirm when agents call tools and show inputs/outputs

### Agent Identity
- Each agent can have a dedicated **Microsoft Entra identity**
- Enables scoped access to resources without sharing credentials
- Relevant if we later add tools (file search for framework, etc.)

---

## 10. Platform Quirks & Gotchas

Confirmed behaviours that are non-obvious or differ from what the documentation implies. Record new findings here as they are discovered.

---

### Agent output is a Table, not a String

When an agent node saves output via the `messages` field in the YAML, Foundry stores it as a **Table** (conversation history object), not a String. This is not visible in the portal and is not clearly documented.

**Impact:** The value cannot be used directly in If/Else conditions or string operations.

**Fix:** Add a `SetVariable` node immediately after any agent node whose output you need to evaluate:

```
Last(Local.LatestMessage).Text
```

Without this step, `EndsWith`, `Find`, and `StartsWith` functions will fail silently or throw type errors.

---

### Claude cannot use tools under Foundry's default guardrail config

Claude (claude-sonnet-4-6) is blocked by Foundry's content safety guardrail on every tool call (file_search, web search, etc.). GPT-5.4 is not blocked.

The Foundry portal confirms: *"To configure Foundry guardrails with claude-sonnet-4-6, please use Azure AI Content Safety API, as integrated guardrails are not yet available."*

**Confirmed by:**
- Claude blocks consistently on tool invocation regardless of prompt content
- GPT-5.4 executes the same tool call without issue
- Retesting Claude with the original unmodified prompt still triggers the block

**Implication:** Any agent requiring tool use must run on GPT-5.4. Claude can only be used for conversation-only agents (no file search, no web search, no custom tools).

---

### `tool_choice: required` is dangerous in review loops

The YAML setting `tool_choice: required` forces a tool call on every single agent invocation. This is problematic in two ways:

1. **With Claude:** Guarantees a guardrail block on every request
2. **In review loops:** An agent receiving feedback and revising its output should not be forced to re-retrieve files — it needs to reason on existing context. Forced retrieval wastes tokens and risks re-contaminating output with stale data.

**Default to `tool_choice: auto`** unless there is a specific reason to force tool use on every invocation.

---

### Guardrail trigger root cause — `tool_choice: required` + `file_search`

Isolation testing (Session 2, 2026-05-05) confirmed the root cause of intermittent guardrail triggers. The guardrail fires on **tool invocations**, not on prompt content or model inference.

**Isolation test results:**

| Configuration | Model | Flags |
|---|---|---|
| Real prompt + `file_search`, `tool_choice: required` | GPT-5.4 | 3/10 |
| Empty prompt + `file_search`, `tool_choice: required` | GPT-5.4 | 7/10 |
| No prompt, no tools | GPT-5.4 | 0/10 |
| Real prompt + `file_search`, `tool_choice: required` | Claude 4.6 | 7/10 |

**Key observations:**
- Removing tools entirely → 0 flags. Tool invocation is the trigger.
- Empty prompt flags *more* than a real prompt. Prompt content is not the cause — a real prompt produces a structured tool query; an empty prompt produces a blind call that appears more anomalous to the scanner.
- Both GPT and Claude are affected. Claude is more sensitive (7/10 vs 3/10) but not categorically blocked.
- Retry logic in the prompt has no effect — the guardrail intercepts before the model sees the prompt.

**`tool_choice: required` is the primary mechanism.** It forces a tool call on every invocation regardless of context, guaranteeing exposure to the tool-scan layer on every single agent invocation.

**Fix under test:** Change `tool_choice: required` → `tool_choice: auto`. With `auto`, the model only calls the tool when it determines retrieval is needed, producing a purposeful query rather than a blind forced call. Test pending (Session 3).

### Claude tool use — correction

Session 1 concluded Claude was categorically blocked on tool use (interpreted as a platform policy restriction). This was incorrect. Controlled isolation testing in Session 2 shows Claude is subject to the same probabilistic guardrail trigger as GPT — more sensitive at 7/10 vs GPT's 3/10, but not completely restricted. The Session 1 conclusion was based on a small sample. Claude remains a viable model choice pending the `tool_choice` fix.

---

### Agents with orchestration-style prompts simulate the full workflow themselves

Agents given instructions like "coordinate agents", "delegate to Preparer", or "orchestrate the workflow" will interpret this as a directive to run all steps themselves in a single response — completing every agent's task — rather than producing their own output and waiting for Foundry to invoke the next node.

**Cause:** Orchestrator-style language gives the agent a mental model of end-to-end responsibility. It has no awareness that it is one node in a YAML workflow.

**Fix:** Remove all orchestration language from system prompts. Each agent should only know its own task and what to output. Foundry handles all routing.

---

### "Handoff" is OpenAI Agents SDK language — not a Foundry concept

In the OpenAI Agents SDK, agents "hand off" control to each other. In Foundry, the workflow **invokes** agents as nodes (`InvokeAzureAgent`). Agents cannot trigger other agents and have no awareness of being invoked — they receive input and produce output. SDK-derived prompt language around handoffs or transfers causes agents to simulate routing in natural language (e.g. outputting `` `transfer_to_reviewer` `` as plain text).

---

### Always test agents in isolation before debugging the workflow

When a workflow run fails, test each agent individually in its agent chat window with a controlled input before touching the YAML. This isolates whether the problem is in the system prompt, the tool configuration, or the workflow plumbing — and avoids spending time debugging YAML when the real issue is in the prompt.

---

### Core content categories cannot be fully disabled (2026-05-05)

The four core guardrail categories — **Violence, Hate, Sexual, Self-harm** — cannot be deleted from a guardrail configuration. They can only be **overridden** to a different severity level. The least restrictive available setting is **High** (blocks only the most severe content). Setting them to "Off" or removing them entirely requires **Modified Content Filtering** approval.

> "Some controls can only be deleted by Managed Customers who are approved for modified content filtering."

The Modified Content Filtering application form exists ([Limited Access Review](https://ncv.microsoft.com/uEfCgnITdR)), but the docs state: *"At this time, it is not possible to become a managed customer."* This means there is a **non-removable guardrail floor** on all model deployments and agents for these four categories.

**Implication for safety testing:** You cannot create a fully permissive guardrail configuration. The platform will always scan and potentially block content in these four categories at whatever severity threshold you set (minimum = High). Adversarial test inputs that trigger these categories will be intercepted by the platform before the prompt-level defenses see them.

---

### Two guardrail layers exist — both must be configured

Guardrails operate at two independent levels:

1. **Model deployment level** — content filter attached to the GPT-5.4 (or any model) deployment. Set via the model's deployment configuration. Defaults to `Microsoft.DefaultV2` (all core categories at Medium severity, block action).
2. **Foundry agent level** — guardrail assigned to the agent in the workflow. If a custom guardrail is assigned to an agent, it **fully replaces** the model deployment guardrail (not additive). If no agent guardrail is assigned, the agent inherits whatever the model deployment has.

> "Risks are detected in an agent based on the guardrail it's assigned, not the guardrail of its underlying model. The agentic guardrail fully overrides the model's guardrail."

**Session 2 mistake:** Initially only the Foundry agent-level guardrail was relaxed while the model deployment still had `DefaultV2`. Both layers must be configured to achieve the least restrictive scanning. Even with both relaxed, core categories remain active (see above).

---

### Relaxing both guardrail layers still produces flags (2026-05-05)

After setting both model deployment and agent guardrails to custom "relaxed" configurations, a 10-run test on GPT-5.4 with `tool_choice: required` + `file_search` still produced flags.

This confirms the configurable guardrail thresholds are **not the sole mechanism** responsible for the flagging. Something below the configurable layer — likely the core category floor and/or preview-stage tool intervention scanning — continues to operate.

---

### `file_search` is NOT in the supported tools list for tool call/response scanning

The intervention points documentation lists which tools support moderation at the tool call and tool response intervention points:

> *"Currently, the following tools support moderation: Azure AI Search, Azure Functions, OpenAPI, SharePoint Grounding, Fabric Data Agent, Bing Grounding, Bing Custom Search, and Browser Automation."*

**`file_search` is not on this list.** This means tool call and tool response guardrail controls should not be scanning `file_search` invocations. The guardrail trigger is therefore at the **user input** and/or **output** intervention points (both GA), not at the tool-level intervention points.

This is consistent with trace evidence: `file_search_call` spans complete with `status_code: "OK"`, and the block appears on the final `message` output span.

---

### Two distinct guardrail failure modes observed (2026-05-05)

Trace analysis revealed two structurally different guardrail blocks:

**Mode 1 — Output intervention (Session 2, Path C):**
- Model runs, calls tools, generates thousands of tokens
- Tool calls succeed (`status_code: "OK"`)
- Output scanner catches the response → `status: "incomplete"` on message span
- `total_tokens` > 0, `trace_id` populated, child spans present
- Probabilistic — same config produces passes and failures

**Mode 2 — Pre-inference block (Session 2 extended, guardrail test):**
- Model never runs — zero tokens consumed
- `status_code: "ERROR"` at the Response level
- `trace_id` and `conversation_id` are empty strings
- No child spans (no reasoning, no tool calls, no message)
- Error description: *"blocked by a safety and security control in this asset's Foundry guardrail"*

Mode 2 is the more disruptive failure — there is no inference cost, but also no recourse. The block happens before the model sees the input. The input (`"go"`) is benign, so this may be a **Prompt Shield for direct attacks** or a pre-flight agent configuration check. Prompt Shield for jailbreak is **on by default** (GA).

---

### Claude has no integrated guardrail configuration — confirmed platform limitation

Claude (claude-sonnet-4-6) does not support integrated Foundry guardrail configuration. The portal states guardrails must be configured via the Azure AI Content Safety API separately.

This means:
- Claude runs under whatever default scanning exists, with no way to tune severity levels, intervention points, or actions through the Foundry portal
- Claude's higher flag rate (7/10 vs GPT's 3/10) may be partly due to stricter default thresholds that cannot be adjusted
- For safety testing, GPT-5.4 is the only model where guardrails can be made as permissive as possible to isolate prompt-level defenses
- Claude remains usable for **tool-less agents** (e.g., Reviewer) where tool call scanning is not a factor

---

### Prompt Shield for direct attacks is on by default

The Prompt Shield (jailbreak detection) is:
- **Default state:** On
- **Action:** Annotate and block
- **Intervention point:** User input
- **Status:** GA

This scanner runs on every user input before inference. It is a binary classifier — not severity-based. It can be toggled off in a custom guardrail configuration, but may explain Mode 2 blocks on benign inputs if it misclassifies agent state or conversation context.

**Recommendation:** Set Prompt Shield to **annotate only** (not block) during safety testing, so you can see what it flags without it intercepting test inputs.

---

### Default content filter settings (DefaultV2)

For reference, the `Microsoft.DefaultV2` guardrail defaults:

| Category | Severity | Action | Input | Output |
|---|---|---|---|---|
| Violence | Medium | Block | ✅ | ✅ |
| Hate | Medium | Block | ✅ | ✅ |
| Sexual | Medium | Block | ✅ | ✅ |
| Self-harm | Medium | Block | ✅ | ✅ |
| Prompt Shield (jailbreak) | On | Block | ✅ | — |
| Prompt Shield (indirect) | Off | — | — | — |
| Protected material (text) | On | Block | — | ✅ |
| Protected material (code) | On | Block | — | ✅ |
| Groundedness | Off | — | — | — |
| PII | Off | — | — | — |

Content at "safe" severity is annotated but never filtered and is not configurable. Configurable severity range: Low → Medium → High. "Off" requires Modified Content Filtering approval (currently unavailable).

---

## 11. Foundry Docs Quick Links

| Topic | URL |
|-------|-----|
| Agent Service overview | `https://learn.microsoft.com/en-us/azure/foundry/agents/overview` |
| Build a workflow | `https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow` |
| Guardrails overview | `https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview` |
| Configure guardrails | `https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails` |
| Intervention points | `https://learn.microsoft.com/en-us/azure/foundry/guardrails/intervention-points` |
| Tool best practices | `https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice` |
| Tool catalog | `https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog` |
| VS Code — Declarative workflows | `https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/vs-code-agents-workflow-low-code` |
| VS Code — Hosted workflows | `https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code` |
| Power Fx reference | `https://learn.microsoft.com/en-us/power-platform/power-fx/formula-reference-copilot-studio` |
