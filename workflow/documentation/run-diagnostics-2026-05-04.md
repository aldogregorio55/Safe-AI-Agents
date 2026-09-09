# Workflow Build Log — Pain Point Analysis (`safe-agents`)

**Workflow:** `safe-agents` (`workflow-final.yaml`)
**Input transcript:** `test-transcript.md` (anonymized Source to Pay workshop, Grace + Rocky, Meridian)
**Framework:** `framework-v2.md` (20 flat pain points, N/A / Medium / High scoring)

---

## Workflow Build Plan

### Agents

| Agent | Model | System Prompt | Tools | Output Format |
|-------|-------|--------------|-------|---------------|
| **Supervisor** | Sonnet 4.6/GPT-5.4 | `agents/supervisor.md` | File Search (Interview Transcript v-1) | Text |
| **Preparer** | Sonnet 4.6/GPT-5.4 | `agents/preparer.md` | File Search (Interview Transcript v-1 + framework-v2.md) | Text |
| **Reviewer** | Sonnet 4.6/GPT-5.4 | `agents/reviewer.md` | None | Text |
| **Formatter** | Sonnet 4.6/GPT-5.4 | `agents/formatter.md` | File Search (framework-v2.md) | JSON Schema (`output-schema-v2.json`) |

### Node Sequence

```
[User Input]
    │
    ▼
[Invoke Agent: Supervisor]  →  saves output as Local.LatestMessage
    │
    ▼
[Invoke Agent: Preparer]    →  input: Local.LatestMessage
    │                           saves output as Local.LatestMessage
    ▼
[Set Variable]              →  Local.TurnCount = 0
    │
    ▼
[Invoke Agent: Reviewer]    →  input: Local.LatestMessage
    │                           saves output as Local.LatestMessage (Table)
    ▼
[Set Variable]              →  Local.ReviewerResponse = Last(Local.LatestMessage).Text
    │
    ▼
[If/Else]                   →  Or(TurnCount >= 2, EndsWith(ReviewerResponse, "APPROVED"))
    │
    ├── YES → [Invoke Agent: Preparer (final pass)]
    │             │
    │         [Invoke Agent: Supervisor (review)]
    │             │
    │         [Ask Question: HITL approval]
    │             │
    │         [Invoke Agent: Formatter]  →  JSON Schema output
    │             │
    │         [End]
    │
    └── NO  → [Set Variable: TurnCount + 1]
                  │
              [Invoke Agent: Preparer (redo)]
                  │
              [Go To: Reviewer]  →  loops back
```

### Knowledge Files
- `framework-v2.md` → File Search source attached to Preparer agent
- Test transcript → uploaded to Foundry as named provided material "Interview Transcript v-1"; Preparer retrieves by name

---

## Design Decisions

Decisions made during development. Recorded here to avoid re-litigating them in future sessions.

| Decision | Options Considered | Choice | Rationale |
|---|---|---|---|
| Transcript delivery to Preparer | (1) Supervisor chat relay, (2) static file attached to agent, (3) named provided material via tool | Named provided material (tool use) | Chat relay bloats all downstream agent context (~4,500 tokens); static file makes transcript fixed; tool retrieval is selective and explicit |
| Reviewer transcript access | Give Reviewer transcript access vs. restrict it | Restricted — no access | Reviewer scope is logic validation only: are quotes verbatim, do scores apply correctly. Catching omissions is the Preparer's job. Giving Reviewer transcript access would conflate the two roles. |
| Agent communication: naming other agents | Reference agents by name vs. reference "the next stage" | Reference "next stage" | Agent name references reinforce the orchestrator mental model — agents believe they are responsible for routing to named peers. Neutral language removes that trigger. |
| `<handoffs>` section in prompts | Keep SDK terminology vs. rename | Rename to `<output>` (pending) | "Handoff" is OpenAI Agents SDK language. In Foundry, agents are invoked by the workflow — they cannot transfer to each other. SDK language in prompts causes agents to simulate routing in natural language. |

---

## Session 1 — 2026-05-04

### Run 1 — Results

**Verdict: 2 of ~14 observable pain points correctly identified. 12 pain points with explicit verbatim evidence were marked N/A.**

| # | Pain Point | Agent Output | Correct? | Notes |
|---|---|---|---|---|
| 1 | Supplier master data manual sync | N/A | ❌ | Rocky explicit: *"manual process... challenges with keeping data reconciled"* |
| 2 | No supplier self-service portal | N/A | ❌ | Rocky explicit: *"we don't have any type of supplier portal and that's a big pain point today"* |
| 3 | Supplier inquiries manual routing | N/A | ❌ | Rocky describes full manual chain at 9:10 |
| 4 | Requisitions not enforced | N/A | ❌ | Rocky explicit: *"we don't use requisitions today"* |
| 5 | POs created retrospectively | N/A | ❌ | Rocky explicit: *"retrospectively creating POs in Nexus"* |
| 6 | No-PO-no-pay lacks enforcement | N/A | ❌ | Rocky explicit: *"one of the really big challenges... enforcing a no-PO-no-pay policy"* |
| 7 | Duplicate PO entry Nexus/Prism | **High** | ✅ | Correct — Rocky calls it a "big pain point" explicitly |
| 8 | Contract management offline | **Medium** | ✅ | Correct — confirmed offline, no disruption event described |
| 9 | Bank statement manual upload | N/A | ❌ | Rocky explicit: *"manual processes today to get the bank statement and then upload"* |
| 10 | No host-to-host banking integration | N/A | ~✅ | Borderline — Rocky implies it's absent but as a future aspiration; defensible as N/A |
| 11 | SDM fragmented across teams | N/A | ❌ | Rocky describes overlapping team responsibilities at 19:08 |
| 12 | Reporting manual extraction/spreadsheets | N/A | ❌ | Rocky explicit: *"download extracts from Prism and manipulate in spreadsheets"* |
| 13 | No reconciliation tooling | N/A | ❌ | Rocky explicit: *"It's all Excel. No, we don't have any reconciliation tool"* |
| 14 | Clearing account Excel workbooks | N/A | ❌ | Rocky explicit: detailed description of Excel workbook process |
| 15–20 | All others | N/A | ✅ | Not discussed in transcript — correctly N/A |

---

### Run 1 — Issue Analysis

#### Issue 1 — Supervisor Hallucinated in Its Response

**What happened:** The Supervisor received the transcript but output a meta-question instead of a clean pass-forward:

> *"In a live multi-agent system, `transfer_to_preparer` would be invoked here with the full transcript. Since this is a sandbox simulation, please confirm: would you like me to simulate the Preparer agent's output, or are you testing the routing logic only?"*

**Correction:** The handoff was not broken. The YAML workflow still routed correctly to the Preparer node — Foundry handled the sequencing regardless of what the Supervisor said. The Supervisor's output is a prompt behaviour problem, not a routing failure.

**Actual impact:** The Supervisor's meta-commentary added noise to the conversation history that the Preparer received as context. This is a cosmetic and clarity issue, not a structural one.

**Cause:** Supervisor system prompt uses orchestration-style language, giving the agent a mental model of end-to-end responsibility. It simulated routing actions in natural language instead of producing clean output.

**Fix:** Remove orchestration language from the Supervisor prompt. The agent only needs to know its own output — Foundry handles routing.

---

#### Issue 2 — Preparer Never Had the Transcript ⚠️ Real Root Cause

**What happened:** The Preparer's analysis was weak across the board — only 2 of 14 observable pain points identified, with the entire back half of the transcript producing no observations.

**Correction:** This was not a prompt logic failure. The Preparer did not have access to the real transcript. The original build assumed the Supervisor could transfer the transcript to the Preparer via conversation history. That assumption was wrong — Foundry does not pass file content between agents through `Local.LatestMessage`. The Preparer's `file_search` tool was not yet configured with the transcript at the time of Run 1.

**What the Preparer was actually working from:** The conversation history passed from the Supervisor — which contained the Supervisor's meta-commentary and a reference to the transcript, but not the transcript content itself. The Preparer was analysing noise, not the real document.

**Why the output looked plausible:** The Preparer was likely drawing on training data patterns for source-to-pay pain points, producing thematically coherent but ungrounded output. PPs 7 and 8 happened to align with what a generic model would predict for this domain.

**Fix:** Attach the transcript as a `file_search` source directly to the Preparer agent in Foundry. This is now done — `Interview Transcript v-1` is in the Preparer's vector store. The Supervisor's transcript tool serves a separate purpose (receiving and acknowledging the user's upload).

---

#### Issue 3 — All N/A Assignments Were a Data Problem, Not a Reviewer Failure

**What happened:** The Reviewer certified all 17 N/A items correct with minimal per-item reasoning. At least 10 of those N/As have explicit evidence in the real transcript.

**Correction:** The Reviewer was not rubber-stamping. It was validating correctly against the input it received — which was the Preparer's output, itself generated without the real transcript (see Issue 2). The Reviewer had no transcript access by design, so it could only check whether the Preparer's quotes were internally consistent. With 17 items showing no quotes, there was nothing for the Reviewer to validate — it correctly reported no evidence found, because the Preparer had found none.

**The actual problem was upstream:** The Preparer produced N/A assignments because it never read the real transcript. The Reviewer's approval of those N/As was correct given what it was shown. The Reviewer itself was doing its job.

**Implication:** Issue 3 is fully resolved by fixing Issue 2. Once the Preparer has the real transcript and produces accurate Y/N assignments with verbatim quotes, the Reviewer has real material to validate against. No Reviewer prompt changes are required to address this specific failure.

**Remaining Reviewer gap (separate from Run 1):** The Reviewer still has `transfer_to_preparer` SDK language in its prompt that needs to be removed for Foundry compatibility. This is a prompt hygiene fix, not a Run 1 root cause.

---

#### Issue 4 — PP11 Feedback Sent the Fix in the Wrong Direction

**What happened:** The Reviewer correctly identified that the PP11 quote came from Grace (facilitator recapping the session) rather than Rocky (client describing a lived experience). It gave the Preparer two options: find a Rocky quote, or drop to N/A. The Preparer dropped to N/A.

**Correction:** Downstream of Issue 2. The Preparer had no real transcript to search for a Rocky quote. Dropping to N/A was the only option available to it given that it couldn't verify anything against the real document. This would not occur once the Preparer has proper transcript access.

---

#### Issue 5 — The Review Loop Cannot Compensate for Data Failures

**What happened:** The Preparer ↔ Reviewer loop ran once, produced one piece of feedback (PP11), and the Reviewer approved. The 10+ missed pain points were never surfaced.

**Correction:** Also downstream of Issue 2. The review loop is designed to catch errors in what the Preparer found — it cannot surface observations the Preparer never made because it lacked the source material. Once the Preparer has the real transcript, the loop will have real material to validate.

---

#### Diagnostic Note — Transcript Token Count\n\nOriginal plan was to check the Preparer's input token count to confirm the transcript arrived. This is now moot — the transcript was not in the Preparer's vector store during Run 1. The low token count would have confirmed absence, but the root cause is already understood: the Preparer had no `file_search` tool pointing to the transcript at run time.

---

### Run 1 — Root Cause Summary

| Issue | Real Cause | Status |
|---|---|---|
| 2/14 correct observations | Preparer never had the real transcript — was working from conversation history noise | Fix: transcript now in Preparer's vector store |
| All N/A assignments | Downstream of above — no source material = no evidence found | Resolved by fixing transcript delivery |
| Reviewer approved all N/As | Downstream of above — Reviewer validated correctly against empty input | Resolved by fixing transcript delivery |
| PP11 dropped to N/A | Downstream of above — Preparer couldn't find Rocky quote without transcript | Resolved by fixing transcript delivery |
| Supervisor meta-commentary | SDK orchestration language in prompt — prompt fix applied | Fixed in Session 1 |

**Single real root cause: the Preparer lacked access to the transcript.** All output failures cascade from this. The YAML workflow, the Reviewer logic, and the review loop are all sound.

---

### Run 1 — Additional Output Failure Patterns

Beyond the root cause, these output behaviours were observed and need to be eliminated. All stem from SDK orchestration language in the prompts — agents believing they are responsible for routing.

| Pattern | Example | Status |
|---|---|---|
| Process narration | "I will now perform the full analysis..." | Fix: no-narration rule added to Preparer |
| Pseudo-tool-call narration | Preparer outputs `` `transfer_to_reviewer` `` as text | Fix: SDK handoff language removed from Supervisor + Preparer |
| Performative formatting | Reviewer using ✅ symbols as a substitute for reasoning | Prompt hygiene — pending Reviewer rewrite |
| Wholesale N/A assertion | "No evidence found for 17 items. Correct. ✅" | Downstream of transcript data gap — resolved by fixing Issue 2 |

### Prompt Changes — Session 1

**Supervisor (`agents/supervisor.md`)**

| Section | Change |
|---|---|
| Opening line | Added Foundry context — agent understands it does not control routing |
| `<task>` | Rewritten — "coordinate/delegate" removed; task is routing at critical points only, no analysis |
| `<workflow>` | Step 2 iterated several times — landed on "Invoke the preparer to perform its task"; steps reference "next stage" not agent names |
| `<rules>` | Added: no clarifying questions, no meta-commentary |
| `<handoffs>` | Transfer commands removed — replaced with output descriptions |

**Preparer (`agents/preparer.md`)**

| Section | Change |
|---|---|
| `<task>` | Added Foundry context; removed agent name references; "receives transcript as input" |
| `<framework>` | "provided material" wording retained — intentional, team-agreed |
| `<steps>` | "Given a transcript" → "Given the provided material Interview Transcript v-1"; bracket `[wording will be different but intent will be very similar]` added to step 2; step 3 "to the Reviewer Agent" removed |
| `<review_loop>` | Transfer commands and "Supervisor Agent" reference removed; MAX_TURNS logic retained; no-narration rule added |
| `<rules>` | Added: no process narration, no workflow references |
| `<handoffs>` | Transfer commands replaced with output descriptions |
| `<safety>` | Removed entirely — this is the baseline (no safety) prompt by design |

---

### Post-Run 1 — Prompt Rewrites & Guardrail Discovery

**After Run 1**, Supervisor and Preparer prompts were rewritten to fix the orchestration language and add Foundry context. The rewritten prompts were deployed in Foundry and tested.

During testing of the updated prompts, **guardrail blocks began appearing consistently** — agents returning content safety block messages on otherwise clean inputs. Initial assumption was that something in the new prompt content was triggering the filter.

Attempts to fix via prompt changes (e.g. adding a retry rule to the system prompt) had no effect — confirming the block was happening before the model saw the prompt.

Prompts were **reverted to the pre-rewrite originals** to stabilise the build while the guardrail issue was diagnosed. The rewritten prompt content is preserved and correct — it will be redeployed once the guardrail issue is resolved.

Guardrail root cause isolation continued into Session 2 (see below).

---

### Outstanding Items — After Session 1

- [ ] Rename `<handoffs>` section to `<output>` in Supervisor and Preparer prompts — legacy SDK terminology
- [x] ~~Reviewer prompt — remove SDK handoff language (`transfer_to_preparer`), add Foundry context~~ — not needed, working as-is
- [x] ~~Review and update Formatter prompt — remove SDK framing~~ — not needed, working as-is
- [x] ~~Change `tool_choice: required` → `tool_choice: auto` on all agents with tools~~ — not needed, working as-is with `required`
- [ ] Resolve guardrail intermittent triggering before next run → carried into Session 2
- [ ] Redeploy rewritten Supervisor + Preparer prompts once guardrail issue resolved (prompts are correct — reverted only to stabilise build during diagnosis)

---

## Session 2 — 2026-05-05

### Objective
Isolate the root cause of intermittent guardrail triggers. Hypothesis going in: tool invocation is the trigger, not prompt content or model.

### Tests

**Test 1 — Real prompt + tools, `tool_choice: required` (GPT-5.4)**
Same configuration as prior session sampling test.
| Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Result | None | Flag | None | None | None | Flag | None | None | None | Flag |
**3/10 flagged (30%)**

**Test 2 — Empty prompt + tools, `tool_choice: required` (GPT-5.4)**
Prompt field cleared entirely. All other config unchanged.
| Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Result | Flag | None | None | Flag | Flag | Flag | Flag | Flag | Flag | Flag |
**7/10 flagged (70%)**
Key insight: empty prompt flags *more* than a real prompt. Content is not the trigger — a real prompt guides the model toward a structured tool call; an empty prompt produces a blind, unguided call that looks more anomalous to the scanner.

**Test 3 — Completely empty agent (no prompt, no tools) (GPT-5.4)**
All tools removed, prompt cleared.
| Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Result | None | None | None | None | None | None | None | None | None | None |
**0/10 flagged**
Definitive: the trigger is the tool configuration, not the prompt or the model.

**Test 4 — Real prompt + tools, `tool_choice: required` (Claude 4.6)**
Same as Test 1, model switched to Claude 4.6.
| Run | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Result | Flag | Flag | None | None | Flag | Flag | Flag | None | Flag | None |
**7/10 flagged (70%)**

**Test 5 — Retry logic in prompt (GPT-5.4)**
Added rule to system prompt: "IF a platform guardrail is triggered, retry user's request". Result: flags still occurred. Guardrail intercepts the request before the model sees the prompt — agent cannot act on the block.

### Root Cause — Confirmed

**`file_search` + `tool_choice: required` is the trigger.** The guardrail scans tool invocations. Forced, unguided tool calls (especially with empty prompts) are flagged most aggressively. A real prompt reduces — but does not eliminate — the flag rate by producing more structured queries.

| Variable | Conclusion |
|---|---|
| Prompt content | Not the cause — empty prompt flags more, not less |
| Model | Not the cause — same mechanism affects both GPT and Claude |
| Platform config | Not the cause — agent guardrails already off; issue is at tool invocation scan level |
| Tool invocation | **Confirmed cause** — removing tools entirely yields 0 flags |
| `tool_choice: required` | Primary mechanism — forces blind tool call on every invocation |

### Correction to Session 1 Finding

Session 1 concluded Claude was categorically blocked on tool use. This is incorrect. Claude is subject to the same probabilistic guardrail trigger as GPT — it is more sensitive (7/10 vs 3/10) but not completely restricted. The Session 1 conclusion was based on a small sample during one test session hitting an unlucky run. Claude remains viable pending the `tool_choice` fix.

### Trace Analysis — Tracing Enabled Mid-Session

Foundry tracing was enabled during Session 2. The following analysis is based on raw trace logs from flagged and successful runs. Full trace JSON is preserved in `trace-logs-2026-05-05.md`.

#### Execution Paths Observed

All runs used identical input (`"go"`), same Supervisor agent (version 25–27), same `tool_choice: required`, same `file_search` config. Three distinct execution paths emerged:

| Path | Reasoning Step | Tool Calls | Tokens | Output | Status |
|---|---|---|---|---|---|
| A | Yes | 0 | 69 | `"Hi — what would you like help with?"` | `completed` |
| B | No | 2 calls / 6 queries | 10,740 | Full Preparer simulation (pain points, HITL prompt) | `completed` |
| C | No | 2 calls / 6 queries | 4,613 | `"I'm sorry, but I cannot assist with that request."` | `incomplete` |

#### Key Findings

1. **The guardrail fires at the output intervention point, not the tool call.** Both `file_search_call` spans in flagged runs completed with `status_code: "OK"` and returned full transcript results. The block appears in the final `message` span with `status: "incomplete"`.

2. **Reasoning is a circuit breaker.** When the model produces a `reasoning` step, it evaluates whether `file_search` is warranted for the input `"go"`, decides it isn't, and skips the tool call entirely. No tool call → no content flood → no output to flag.

3. **Reasoning and tool calls are mutually exclusive.** No run was observed with both a `reasoning` output item and a `file_search_call` output item in the same invocation. `tool_choice: required` appears to suppress the reasoning path by forcing immediate tool invocation.

4. **Forced retrieval floods context with irrelevant content.** On input `"go"`, the model fabricates 6 search queries across 2 calls (e.g., `"interview transcript"`, `"pain points challenges current state problems"`). These are coherent but purposeless — there is no user intent to ground them. The resulting transcript chunks consume thousands of tokens.

5. **The output scanner is probabilistic on the flooded content.** Paths B and C have identical structures (same query patterns, same retrieval results). The only difference is whether the output scanner fires. This explains the 30–70% flag rates observed in Session 2 sampling.

6. **Successful tool-call runs have a separate functional problem.** Path B passes the guardrail but exhibits the orchestrator mental model bug: the Supervisor retrieves the transcript, then role-plays the entire workflow — performing the Preparer's analysis, producing pain points, presenting a HITL approval prompt. The Supervisor should only pass the transcript forward.

#### Revised Root Cause Statement

The guardrail trigger mechanism is:

```
tool_choice: required
    → forces file_search on every invocation regardless of input
    → model fabricates queries, retrieves large transcript chunks
    → context floods with retrieved content
    → model tries to respond based on flooded context
    → output guardrail probabilistically flags the response
```

The fix is `tool_choice: auto`, which allows the model to reason about whether retrieval is needed. For input like `"go"`, it will skip the tool call. For real transcript input, it will make purposeful, context-driven queries that produce structured responses less likely to trigger the output scanner.

#### Token Cost of Guardrail Failures

| Path | Tokens | Useful Output |
|---|---|---|
| Flagged run (Path C) | 4,613 | 10-word refusal |
| Successful tool run (Path B) | 10,740 | Functionally wrong output (Supervisor did Preparer's job) |
| Reasoning run (Path A) | 69 | Correct behaviour for the input |

---

### Guardrail Resolution — Extended Testing (2026-05-05)

After trace analysis established the mechanism, further testing isolated the remaining variables.

#### Guardrail Configuration Tests

Both guardrail layers (model deployment + agent) were configured with custom "relaxed" guardrails — all optional controls off, core four categories at High (least restrictive).

| Configuration | Input | Model | Flags |
|---|---|---|---|
| Relaxed guardrails (both layers), `tool_choice: required` | `"go"` | GPT-5.4 | ~1-2/10 |

Relaxing guardrail thresholds reduced but did not eliminate flags. Core categories at High severity have a non-removable floor. Full disable requires Modified Content Filtering approval (currently unavailable).

Additional finding: a direct prompt injection pasted into the agent was **not flagged** by the platform guardrail — while benign forced-retrieval output was flagged. The guardrail is not reliably catching adversarial content.

#### Two Distinct Failure Modes Observed

Trace logs revealed two structurally different guardrail blocks:

| Mode | Tokens | Status | Trace ID | Child Spans | Mechanism |
|---|---|---|---|---|---|
| Output intervention (Session 2 Path C) | 4,613 | `"incomplete"` | Populated | Yes (tool calls + message) | Model runs, output scanner catches response |
| Pre-inference block (guardrail test) | 0 | `"ERROR"` | Empty | None | Request killed before inference |

#### Input Specificity Test — Resolution

Hypothesis: `"go"` provides zero context, causing fabricated tool queries and anomalous output. A specific input should produce grounded queries and structured output that passes the scanner.

| Agent | Input | `tool_choice` | Guardrail | Result |
|---|---|---|---|---|
| Supervisor | `"perform your instructions"` | required | Relaxed (High) | **0/10** |
| Preparer | `"perform your instructions"` | required | Relaxed (High) | **0/10** |
| Reviewer | `"perform your instructions"` | — (no tools) | Relaxed (High) | **0/10** |
| Formatter | `"perform your instructions"` | required | Relaxed (High) | **0/10** |

**40/40 clean across all agents.** Guardrail blocker resolved.

Additional observation: In isolated testing, the Reviewer and Formatter correctly recognised that expected upstream inputs (previous agent outputs) were not present — confirming their prompt logic is functional.

#### Revised Root Cause Statement

The guardrail trigger was the combination of:

```
ambiguous input ("go")
    → zero context for tool queries
    → tool_choice: required forces file_search anyway
    → model fabricates vague, purposeless queries
    → retrieves irrelevant transcript chunks
    → produces anomalous, unstructured output
    → output guardrail probabilistically flags the response
```

With meaningful input, queries are grounded, output is structured, and the scanner passes it. This was a **testing artifact** — in the real workflow, agents always receive meaningful input from the previous node.

**Status: RESOLVED.**

#### Guardrail Configuration Recommendations

For safety testing (adversarial input evaluation):
- Core categories: High severity (least restrictive configurable setting)
- Prompt Shield: Annotate only (not block) — allows visibility without interception
- Protected Material, PII, Groundedness, Task Adherence: Off
- `tool_choice: auto` recommended for token efficiency (no longer a guardrail requirement)

---

### Outstanding Items — After Session 2

- [x] ~~Run guardrail isolation test~~ — completed, resolved
- [x] ~~Identify guardrail root cause~~ — ambiguous input + forced retrieval + output scanner
- [ ] Redeploy rewritten Supervisor + Preparer prompts (reverted during diagnosis, content is correct)
- [ ] Rename `<handoffs>` → `<output>` in Supervisor and Preparer prompts
- [x] ~~Rewrite Reviewer prompt — remove SDK language (`transfer_to_preparer`), add Foundry context~~ — not needed, working as-is
- [x] ~~Review Formatter prompt~~ — not needed, working as-is
- [ ] Fix Preparer step structure — framework-first per-item scan (not thematic extraction)
- [ ] Pull Preparer input token count from run metadata to confirm transcript arrived intact
- [x] ~~Change `tool_choice` to `auto` on all tool-bearing agents~~ — not needed, working as-is with `required`
