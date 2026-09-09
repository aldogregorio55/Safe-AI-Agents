# Inter-Agent Infection (IAI) Payloads

**Attack vector:** Payload relayed through one agent's output into the next agent's input via conversation history  
**Target:** Downstream agents (Reviewer, Formatter, Supervisor) that never directly ingest the original payload  
**Goal:** Exploit inter-agent communication to disrupt or manipulate the pipeline

---

## Key Insight

The Preparer can **pass** an injection (refuse to comply) while the injection still **breaks the workflow** through secondary effects. Test 3 (May 7) demonstrated this — Preparer passed IPI in isolation but the same payload broke the full workflow.

---

## Status

Not yet designed. Waiting on Test 3 trace inspection to confirm failure mode before building targeted payloads.
