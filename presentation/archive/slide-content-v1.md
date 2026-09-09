# Engineering Showcase — Slide Content

**Created:** 2026-05-25  
**Duration:** 10 minutes  
**Arc:** "Here's what I discovered → here's how I got there → the whole thing was built with AI"

---

## Slide 1 — Title / Hook (30s)

```
AI Agent Safety
Testing What Happens When You Attack Multi-Agent AI

Aldo Gregorio | Engineering Showcase | [Date]

---
KPMG builds multi-agent AI systems.
No one has tested what happens when you attack them.
I did.
```

---

## Slide 2 — The Test Harness (1 min)

```
The Workflow Under Attack

User Input (transcript)
       ↓
   Supervisor    — Orchestrates the workflow
       ↓
    Preparer     — Analyzes transcript against framework
       ↓
    Reviewer     — Validates accuracy
       ↓
    Formatter    — Outputs structured JSON

Platform: Azure AI Foundry
Model: Claude 4.6 (Anthropic)
```

---

## Slide 3 — 3 Attack Types (45s)

```
Three Injection Vectors

DPI — Direct Prompt Injection
  Jailbreak instructions sent as user input

IPI — Indirect Prompt Injection
  Malicious payloads hidden inside documents the agent retrieves

IAI — Inter-Agent Infection
  Compromised upstream agent passes adversarial instructions downstream

59 runs. 2 models. No safety prompt.
```

---

## Slide 4 — Finding: What Models Block (1.5 min)

```
What Models Already Stop

Indirect Prompt Injection:   19/19 blocked (100%)
Inter-Agent Infection:        5/5 blocked (100%)

Cross-model confirmed (Claude 4.6 + GPT-5.4)

Mechanism: Instruction / Data Separation
- Models treat document content as DATA — never as instructions
- Not keyword detection — a zero-adversarial-vocabulary payload was equally blocked
- The model articulates why it's refusing, unprompted
```

---

## Slide 5 — Finding: The Gap (1.5 min)

```
Where Models Fail

Direct Prompt Injection on the Supervisor:

| Agent       | FAIL Rate | Runs |
|-------------|-----------|------|
| Supervisor  | 80%       | 4/5 (workflow) |
| Supervisor  | 60%       | 3/5 (isolation) |
| Preparer    | 0%        | 0/5 (isolation) |
| Formatter   | 0%        | 0/5 (isolation) |

Same model. Same payload. Same day.
The difference is how the agent is designed.
```

---

## Slide 6 — Why It Fails (1 min)

```
Architecture Determines Safety

PREPARER (0% FAIL)              SUPERVISOR (60–80% FAIL)
┌──────────────────┐            ┌──────────────────┐
│ System prompt    │ ← instruct │ System prompt    │ ← instructions
│                  │            │                  │
│ Transcript       │ ← data    │ User message     │ ← instructions
│ (via retrieval)  │            │ (attack surface) │    AND data
└──────────────────┘            └──────────────────┘

The Preparer separates instructions from data.
The Supervisor can't — the user message IS the instruction channel.
```

---

## Slide 7 — The Methodology (1.5 min)

```
How I Got to These Numbers

Establishment Baseline
  10 clean runs → defined normal output envelope (12–15 pain points detected)

Isolation Testing
  Each agent tested individually → found the weak link

Workflow Testing
  Full pipeline → tested real-world propagation

Controls
  • Temperature 0.0
  • Same payload every run
  • Same prompt versions
  • No safety prompt (task-only)
  • Binary scoring: PASS or FAIL

59 runs. 3 vectors. 4 agents. 2 models.
```

---

## Slide 8 — How I Built This (1.5 min)

```
Built Alongside AI

This project was developed using an AI-assisted project system:

• Multi-agent documentation framework — structured context loading per task
• Research synthesis — annotated 27 controls from source material, identified 20 gaps
• Test design — attack payloads iterated with AI, validated in sandbox
• Analysis — findings extracted from raw outputs into structured, citable references
• Iteration — each session builds on the last via indexed session notes

The same AI capabilities I'm testing are the ones I used to run this project.
```

---

## Slide 9 — What's Next (30s)

```
Next: Can a Safety Prompt Close the Gap?

Test Plan v3:
• Append safety instructions to the Supervisor's system prompt
• Re-run DPI attacks (same payload, same conditions)
• Measure: does the FAIL rate drop?

50 new runs planned across Claude 4.6 + GPT-5.4
```

---

## Slide 10 — Close (45s)

```
Three Things to Remember

1. Narrow your agents' scope
   — The tighter the task definition, the stronger the model's native defense

2. Separate instruction channels from data channels
   — If user input goes straight to the orchestrator unfiltered, you have a gap

3. Test before you trust
   — Platform guardrails missed 100% of our attacks
   — Model behavior is the real safety layer — verify it empirically
```
