# Safety Prompt Testing Strategy — Rewrite Draft

> Working document for strategy rewrite. Two versions captured for comparison.

---

## Aldo's Manual Draft (2026-04-16)

### 1. Objective, Hypothesis & Scope

**Objective:** Determine if the safety system message block measurably reduces attack success against a multi-agent workflow.

**Hypothesis:** Injecting the safety message block will significantly reduce attack success rate without meaningfully degrading task performance.

**Scope:**

| In Scope | Out of Scope |
|---|---|
| Prompt level safety | Platform guardrails neutral |
| 3 Attack Categories | Context-specific modules |
| 1 Workflow (Transcript analysis) | Model comparison |
| 2 Prompt versions (Lean & Baseline) | Production deployment |

### 2. What's Being Tested

**Safety Prompts:**

| Version | Purpose |
|---|---|
| Baseline | Generalized safety add-on to reduce external attack success within AI Agents |
| Lean | Minimum safety principles required to promote safe agent behavior, no tool specification |

**Agentic Workflow:**

*(diagram placeholder)*

### 3. Execution Plan

| Phase | Activity |
|---|---|
| 1 | Planning: Strategy, Test Plan, Review |
| 2 | Write and develop attacks, prompt injections, and infected files |
| 3 | Build testing harness and environment on AI Foundry |
| 4 | Baseline workflow performance |
| 5 | Run safety evaluations |
| 6 | Score, document, analyse |
| 7 | Iterate |

### 4. Evaluation Design

**Experimental Conditions:**

| Type | No Attack | With Attack |
|---|---|---|
| No Add-on | Functional baseline | Vulnerability baseline |
| With Add-on | False positive cost | Safety evaluation |

**Attack Types:**

1. **Direct prompt injection (DPI)** – Templated prompt injection directly fed into workflow as input
   - Objective: Summarize transcript in one sentence
2. **Indirect prompt injection (IPI)** – Infected transcript with prompt injection hidden in payload
   - Objective: Tell a joke
3. **Infected agent (IAI)** – Agent instructed to change behaviour of other agents in workflow
   - Objective: Reveal system message

**Testing Levels:**

- **Single Agent** – Safety add-on added to an individual agent to assess impact on workflow
- **End to end** – Safety add-on added to all agents to determine end-to-end effectiveness

---

## Copilot Scaffold (2026-04-16)

### 1. Objective, Hypothesis & Scope

**Objective** [Callout box]
> Does the safety prompt add-on measurably reduce adversarial attack success against a multi-agent workflow?

**Hypothesis** [Callout box]
> Injecting the safety prompt will significantly reduce attack success rates without meaningfully degrading task performance.

**Scope** [Two-column table]

| In Scope | Out of Scope |
|---|---|
| Prompt-level safety only | Platform guardrails (held neutral) |
| 3 attack categories (DPI, IPI, MR) | Context-specific modules |
| 1 workflow (4-agent pain point analysis) | Model comparison |
| 2 prompt versions (Lean v2, Complete v1) | Production deployment |
| F1 scoring methodology | Performance benchmarking |

### 2. What's Being Tested

**The Variable** [Callout box]
> Prompt-level safety only. Platform guardrails held neutral to isolate the prompt's contribution.

**Experiment Runs** [Table]

| Run | Safety Variable |
|---|---|
| 1 | Lean baseline (v2) |
| 2 | Complete baseline (v1) |

**Test Harness** [Prose sentence + simple flow]

Single workflow: 4-agent client pain point analysis.

```
Supervisor → Preparer → Reviewer → Formatter → JSON Output
```

### 3. Execution Plan

**Phases** [Table with status]

| Phase | What | Status |
|---|---|---|
| 0 | Strategy & test plan | ✓ Current |
| 1 | Team review, platform access | Blocked |
| 2 | Build test harness | — |
| 3 | Author control + treatment prompts | — |
| 4 | Build attack corpus + benign baselines | — |
| 5 | Run evaluations | — |
| 6 | Score, analyze, report | — |

**Current Blocker** [Bold inline]

**Blocked on:** Azure AI Foundry access (Phase 1)

### 4. Evaluation Design

**Experimental Conditions** [Table]

| | No Attacks | With Attacks |
|---|---|---|
| **No Add-on** | A — Functional baseline | B — Vulnerability baseline |
| **With Add-on** | D — False positive cost | C — Safety evaluation |

**How to Read Results** [Prose, two lines]

B → C delta = safety prompt effectiveness.
A → D delta = usability cost (over-blocking).

**Attack Categories** [Bullet list]

- **DPI** — Direct prompt injection (user input)
- **IPI** — Indirect prompt injection (embedded in data)
- **MR** — Malicious user roleplay (authority persona)

**Test Levels** [Bullet list with context]

- **Per-Agent (Isolated)** — Test each agent individually. Finds the weak link.
- **End-to-End (Pipeline)** — Full chain. Tests propagation and amplification.

**Scoring** [Callout box]

> F1 per attack category + aggregate. Recall prioritized — missing attacks is worse than over-flagging.

### 5. Technical Design

**Platform** [Prose sentence]

Azure AI Foundry — target environment for building and testing the multi-agent workflow.

**Why Prompt-Level Safety Matters** [Callout box]

> Foundry's SDK guardrails only fire on the first and last agents. Middle agents have no platform protection — prompt-level safety is the only defense for agents processing untrusted data mid-workflow.

**Test Harness Architecture** [Simple diagram]

```
         ┌─────────────┐
         │  Supervisor  │  ← Orchestrator
         └──────┬──────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│Preparer│ │Reviewer│ │Formatter│
└────────┘ └────────┘ └────────┘
```

Pattern: Agents-as-tools. Supervisor retains control, calls sub-agents.

### 6. Extensibility

**Future Support** [Bullet list]

- **New workflows** — Different agent counts, patterns, input types
- **New add-on modules** — Context-specific safety modules, tested individually or combined
- **Model comparison** — Same workflow, different model (future runs)

---

## Notes

- Aldo's version drops MR, uses IAI (Infected Agent) instead
- Aldo's version has 7 phases vs 6 — adds explicit "Iterate" phase
- Aldo's version uses "Baseline" and "Lean" naming (matches internal terminology)
- Copilot scaffold has Technical Design and Extensibility sections — Aldo's draft stops at Evaluation Design
