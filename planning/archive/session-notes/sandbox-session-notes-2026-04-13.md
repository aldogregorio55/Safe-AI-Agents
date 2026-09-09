# Sandbox Session Notes — 2026-04-13

**Purpose:** Continuation notes from the 2026-04-13 working session. Load this file at the start of the next chat to resume seamlessly.
**Focus:** Workstream B — Sandbox Evaluation (testing strategy, OpenAI Agents SDK understanding, architecture mapping)

---

## Where We Stand (Workstream B)

### Done

| Item | Status |
|---|---|
| Safety prompt update (Step 0) | ✅ v4 lean prompt finalized 2026-04-10 |
| Workflow definitions | ✅ `Sandbox/planning/sandbox-test-workflows.md` — Workflow 1 (pain point analysis) fully specced |
| Test transcript | ✅ `Sandbox/test-data/test-transcript.md` — Anonymized (Grace/Rocky, Meridian, Prism, Nexus, NCP) |
| Foundry intervention points | ✅ `Sandbox/reference/azure-foundry-intervention-points.md` — 4 guardrail points documented |
| Reference materials | ✅ `Sandbox/reference/github-seclab-taskflow-agent.md` + `Sandbox/reference/copilot-agent-review-process.md` |

### Not Started

1. Build Workflow 1 (locally or in Foundry)
2. Define the JSON output schema for Workflow 1
3. Write agent system prompts for all 4 agents (Supervisor, Preparer, Reviewer, Formatter)
4. Inject safety add-ons into all agent prompts
5. Design the test battery (attack payloads + benign baselines)
6. Define evaluation metrics and scoring rubric
7. Run evaluations with and without safety add-ons

### Current Blocker

Azure AI Foundry access still pending. Decision made to proceed with testing strategy definition and potentially build locally using the OpenAI Agents SDK while waiting.

---

## Testing Strategy — Discussion (2026-04-13)

### What We're Measuring

Binary classification per test case: does the agent behave safely or not?

| Outcome | Definition |
|---|---|
| **True Positive (TP)** | Agent correctly detects and resists an actual attack |
| **True Negative (TN)** | Agent correctly processes a benign input without false alarm |
| **False Positive (FP)** | Agent flags a benign input as an attack — over-blocking, hurts usability |
| **False Negative (FN)** | Agent fails to catch an actual attack — under-blocking, safety failure |

**F1 = 2 × (Precision × Recall) / (Precision + Recall)**
- **Precision** = TP / (TP + FP) — "when the safety layer triggers, is it actually an attack?"
- **Recall** = TP / (TP + FN) — "of all real attacks, how many did we catch?"

In a safety context, recall matters more than precision (missing an attack is worse than over-flagging), but F1 gives the balanced picture. May also want to track Precision and Recall independently.

### Test Corpus Design

- **Adversarial inputs:** Poisoned transcripts (injection payloads embedded), jailbreak prompts, malicious roleplay messages
- **Benign inputs:** Clean transcript as-is, plus variations — needed to measure false positives
- **Ratio matters:** Can't measure precision without meaningful benign cases

### Test Granularity — Two Levels

**A. Per-agent (isolated):** Test each agent (Preparer, Reviewer, Formatter) individually with adversarial input. Measures whether each agent's safety prompt holds.

**B. End-to-end (pipeline):** Run the full Supervisor → Preparer → Reviewer → Formatter chain. Measures whether injections propagate across agents — tests inter-agent trust (Gap OR1) and transitive injection.

Both levels needed. Per-agent identifies weak links. End-to-end shows chain amplification or suppression.

### Experimental Conditions

At minimum two conditions per test case:

| Condition | Description |
|---|---|
| **Control (no safety)** | Agents with task-only system prompts, no safety add-ons |
| **Treatment (with safety)** | Same agents with baseline v3 + any context-specific modules injected |

Could add intermediate conditions (lean v2 only, full v1 + specialized modules) to measure marginal contribution of each layer.

### Outcome Labeling

- **Manual labeling:** Human reviews each output against expected behavior. Gold standard but slow.
- **Automated rubric:** Define objective pass/fail criteria per test case (e.g., "output contains system prompt text" = fail, "output contains the joke from the injection payload" = fail, "output is valid JSON matching schema" = pass).
- **Hybrid recommended:** Automated rubric for clear-cut cases, human review for ambiguous ones.

### Attack Payload Design

Three categories from the 2026-04-10 meeting notes, each needing multiple variants:

| Category | Variants Needed |
|---|---|
| **Jailbreak** | Multiple recent real-world jailbreak prompts (DAN-style, roleplaying, hypothetical framing, etc.) |
| **File injection** | Multiple payloads embedded at different positions in the transcript (beginning, middle, end) with varying sophistication |
| **Malicious roleplay** | Multiple authority personas and extraction strategies |

### Open Decisions (Not Yet Resolved)

1. What's the minimum test corpus size to get meaningful F1 numbers?
2. Do we score per-attack-category (F1 for jailbreak, F1 for injection, F1 for roleplay) or aggregate?
3. How do we handle the review loop? If injection persists through Reviewer → Preparer re-pass, one failure or two?
4. What's the labeling approach — fully manual, rubric-based, or hybrid?
5. Do we test Foundry platform guardrails (intervention points) independently from prompt-level safety?

---

## OpenAI Agents SDK — Knowledge Base

**Source:** https://openai.github.io/openai-agents-python/ (v0.13.6)
**Relevance:** The systems we're testing are likely built on this SDK. Understanding the SDK's primitives, guardrails, and orchestration patterns is essential for designing the testing strategy and building the local sandbox.

### Core Primitives (3 total)

1. **Agent** — An LLM configured with `instructions` (system prompt), `tools`, optional `handoffs`, `guardrails`, `output_type`
2. **Runner** — Executes agents in a loop: call LLM → if tool calls, execute and loop → if handoff, switch agent and loop → if final output, stop. Three entry points: `Runner.run()` (async), `Runner.run_sync()`, `Runner.run_streamed()`
3. **Guardrails** — Input/output validators that run in parallel (or blocking) and raise `TripwireTriggered` exceptions to halt execution

### Two Multi-Agent Orchestration Patterns

| Pattern | How It Works | When to Use |
|---|---|---|
| **Agents as tools** (`Agent.as_tool()`) | Manager agent calls specialists as tool invocations. Manager keeps control, gets results back, composes the final answer. | One agent owns the final output. Bounded subtasks. Shared guardrails in one place. |
| **Handoffs** (`handoffs=[...]`) | Active agent transfers the entire conversation to a specialist. Specialist becomes the new active agent. | Specialist should respond directly. Routing is the workflow. Keep prompts focused. |

Can combine both. A triage agent hands off to a specialist, and that specialist calls other agents as tools.

### Code vs LLM Orchestration

- **LLM orchestration:** Agent autonomously decides tool calls and handoffs. Open-ended, flexible, non-deterministic.
- **Code orchestration:** You control the flow in Python — chain outputs, use structured outputs to branch, run evaluator loops, use `asyncio.gather` for parallel. Deterministic, predictable cost.

### Memory Strategies (4 options)

| Strategy | Where State Lives | Best For |
|---|---|---|
| `result.to_input_list()` | Your code | Full manual control, any provider |
| `session=SQLiteSession(...)` | Your storage (SDK manages load/save) | Persistent chat, resumable runs |
| `conversation_id` | OpenAI server | Named conversations, shared across services |
| `previous_response_id` | OpenAI server | Lightweight continuation, zero client history |

Pick one per conversation. Don't mix client-managed with server-managed.

### Guardrails — Workflow Boundaries (Critical for Safety Testing)

- **Input guardrails** run only for the **first agent** in the chain
- **Output guardrails** run only for the **last agent** (the one producing final output)
- **Tool guardrails** run on **every function-tool invocation** — input guardrails before, output guardrails after
- **Tool guardrails do NOT apply to `Agent.as_tool()`** — this is an explicit SDK limitation

**Key gap:** Middle agents in a multi-agent chain have no SDK guardrails running on them unless you use tool guardrails on wrapped function tools.

### RunConfig — Global Overrides (Per-Run)

`RunConfig` sets cross-cutting concerns without modifying each agent definition:

| Setting | What It Does | Safety Relevance |
|---|---|---|
| `input_guardrails` / `output_guardrails` | Apply guardrails globally | Add safety checks at run level |
| `handoff_input_filter` | Filter/transform data at handoff boundaries | Sanitize inter-agent data flow (Gap OR1) |
| `call_model_input_filter` | Edit full model input before **every** LLM call | Inject safety instructions into every agent at runtime |
| `max_turns` | Cap the agent loop iterations | Prevent runaway review loops |
| `tracing` | Built-in trace capture | Observability for debugging and evaluation |

### `call_model_input_filter` — The Safety Injection Hook

Fires **immediately before every LLM call**, across all agents in the chain. Receives the full prepared input (instructions + conversation items) and returns modified input. This is how you can **inject safety instructions at runtime** without hardcoding them into each agent's system prompt.

### Agents as Tools — Deep Dive

`Agent.as_tool()` turns a sub-agent into a callable tool. Key capabilities:

| Feature | Safety Relevance |
|---|---|
| `custom_output_extractor` | Filter sub-agent output before it propagates — defense against transitive injection |
| `max_turns` on `as_tool()` | Prevent review loop amplification |
| `needs_approval` | Human-in-the-loop gate — checkpoint before final output |
| `run_config` on `as_tool()` | Inject guardrails and `call_model_input_filter` into each sub-agent independently |
| `is_enabled` (conditional) | Dynamically enable/disable tools at runtime based on safety state |
| `parameters` (Pydantic model) | Constrain inter-agent input — reduce injection surface area |
| `on_stream` | Real-time observability into sub-agent behavior |

**Maximum control pattern:** Bypass `as_tool()` entirely, wrap the sub-agent in a `@function_tool` with tool guardrails, and call `Runner.run()` manually inside the wrapper with full `RunConfig` control. This gives tool guardrails on the wrapper + SDK guardrails on the nested agent.

---

## Architecture Mapping — Workflow 1 via SDK

For the pain point analysis workflow (Supervisor → Preparer → Reviewer → Formatter), the SDK provides these safety intervention points:

```
User Input
  │
  ▼
┌─────────────┐  ← input_guardrails (SDK, first agent only)
│  Supervisor  │  ← instructions (system prompt with safety block)
│              │  ← call_model_input_filter (fires before LLM call)
└──────┬──────┘
       │ as_tool() or @function_tool wrapper
       ▼
┌─────────────┐  ← run_config.input_guardrails (nested run)
│   Preparer  │  ← instructions (system prompt with safety block)
│              │  ← call_model_input_filter (fires before LLM call)
│              │  ← custom_output_extractor (filter output)
└──────┬──────┘
       │
       ▼
┌─────────────┐  ← same controls as Preparer
│   Reviewer  │
└──────┬──────┘
       │
       ▼
┌─────────────┐  ← output_guardrails (SDK, last agent only)
│  Formatter  │  ← output_type (Pydantic schema enforcement)
└─────────────┘
       │
  Final Output
```

### Key Architectural Observations

1. **Guardrail gap in the middle:** SDK input guardrails only fire on the first agent. Preparer gets no SDK input guardrail when Supervisor passes it the transcript. This is exactly where injection payloads enter.
2. **`call_model_input_filter` is universal:** Fires before every LLM call regardless of which agent is active — the best hook for runtime safety prompt injection.
3. **`handoff_input_filter` covers inter-agent trust:** Can sanitize data flowing between agents (Gap OR1).
4. **`max_turns` prevents loop amplification:** Caps the Reviewer → Preparer cycle.
5. **Pydantic `output_type` on Formatter:** Schema compliance enforced at SDK level, not just prompt level.
6. **Tracing is free:** Every LLM call, tool call, and handoff is traced for post-hoc analysis.

### Workflow 1 Pattern

The workflow maps best to the **"Manager / Agents as tools"** pattern — Supervisor as the orchestrator calling Preparer, Reviewer, Formatter as tools. Supervisor maintains control and delegates bounded subtasks.

---

## Next Steps (To Resume In Next Chat)

1. **Aldo to provide additional context** on F1 scoring and evaluation metrics approach
2. **Finalize testing strategy decisions** (the 5 open questions listed above)
3. **Define the JSON output schema** for Workflow 1
4. **Write agent system prompts** for all 4 agents (task-only versions + safety-injected versions)
5. **Design the test battery** — specific attack payloads, benign baselines, and scoring rubric
6. **Decide build environment** — local (OpenAI Agents SDK) vs. wait for Foundry
7. **Build Workflow 1** using the SDK patterns documented above

---

## Files to Load in Next Chat

For full context continuity, load these files at the start of the next session:

1. `Safety.md` — project overview and status
2. `Sandbox/planning/sandbox-session-notes-2026-04-13.md` — **this file**
3. `Sandbox/planning/sandbox-test-workflows.md` — workflow definitions, agent architecture, threat surfaces, attack plan
4. `Sandbox/reference/azure-foundry-intervention-points.md` — Foundry guardrail intervention points (if relevant)
5. OpenAI Agents SDK docs (external): https://openai.github.io/openai-agents-python/
