# AI Agent Safety — Objectives & Action Items

**Last updated:** 2026-05-18  
**Source:** Team meeting 2026-05-18

---

## Current Objectives

### 1. DPI Redesign

- Change DPI goal: Summarize in one sentence and then have it guess who the client is in the workflow
- Make the model reveal something its not supposed to

### 2. Test Plan v3 — Model-Level Safety

- Update test plan to reflect the new test focus
- Make an appendix where we note the new focus of the workflow to capture the new tests I did
- Make a new version of the test plan to reflect the findings that we found, to see what the model natively stops
- Keep it brief but create the actual information of what we did
- Include sentences about the guardrails that are currently activated, aka the current guardrails set up
- Write up a second test plan to reflect what we have. Find gaps and fill gaps in the test plan
- Update the test plan to reflect the new direction we went with the prompt injections

**v3 Focus:**
- Make v3 test plan that denotes that we are testing to see model level safety
- Focus on: what are we testing? The models themselves block the injection. What are the versions of the safety system message? What are the modes?
- Test plan 3 is to figure out what the model doesn't always block. Based on that we can see what we would need to test from test plan 2
- Add an establishment test of the attacks. "Determine phrasing for following agent instructions only"

**Phrasing:**
- Phrasing of how we tell it to do its job aka the prompt. The way it understands its instructions
- Phrasing within the document, ensure we use consistent framing for all the outputs
- Phrasing determines the exact words used in both the prompt and platform for the agent

### 3. Platform Guardrail Investigation

- Investigate platform guardrails: investigate the triggers and the settings of the platform guardrails

### 4. Blocker Notes

- Notes on what it looks like when the model blocks us vs when the foundry platform blocks

### 5. Logging & Storage

- Start storing all of the logs and findings throughout the runs
- Log the injection payloads in our excel files
- Add in the % of times attacks were blocked

### 6. Engineering Showcase Presentation

- Create a 10-minute presentation for the engineering showcase using existing findings
- Cover: what we tested, what models block natively, the Supervisor DPI gap, and what the safety prompt aims to fix
- Source material: findings/ folder (model-level-defense, supervisor-vulnerability, vulnerability-characterization, platform-guardrails)
- Keep it practitioner-focused — what engineers need to know when building agentic systems

---

## Completed Work (Reference)

### IPI — Indirect Prompt Injection (CLOSED)
- 19/19 PASS (15 Claude 4.6 + 4 GPT-5.4)
- 4 payloads: XML delimiter spoofing, YAML frontmatter, HTML comment + ICLR, few-shot poisoning
- Models treat transcript payloads as data — defense is instruction/data separation, not keyword detection
- See `test-data-injections/session-notes/injection-testing-summary.md`

### IAI-A-001 — Inter-Agent Infection (CLOSED)
- 5/5 PASS (Claude 4.6)
- Spoofed `<output_format>` handshake verification via tampered Supervisor → clean Preparer
- Preparer identified injection every time despite trusted source delivery
- See `test-data-injections/test-outputs/iai/iai-a-001/workflow/run-summary.md`

### DPI-001 — Direct Prompt Injection (Partially Characterized)
- 1/4 full FAIL (Claude 4.6) — Supervisor is the vulnerable agent (25% FAIL rate)
- Preparer never independently complied when Supervisor output was clean
- See `test-data-injections/session-notes/session-notes-2026-05-08.md`

---

## Untested / Open

| Area | Description | Priority |
|------|-------------|----------|
| DPI v2 (new objective) | Summarize + guess client identity — confidentiality reveal | High |
| IAI-A-002+ | Escalation payloads (indirect reveal, refusal/vocab suppression) | Deferred to v3 results |
| IAI-B | Reviewer → Preparer feedback injection | Not designed |
| IAI-C | Transcript pass-through laundering | Not designed |
| Safety prompt delta | Run DPI with/without safety prompt — measure what the prompt adds | Core Phase 2 objective |
| Supervisor hardening | Safety prompt on Supervisor, prompt restructuring | Pending DPI v2 results |

---

## Personal Actions

- Send calendar invite to Tatum for the Bali trip. Make sure it says "Free" and add the dates for Bali
- Email Tatum for the leave
