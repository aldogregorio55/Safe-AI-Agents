# Technical Deep-Dive — Slide Text (Sections 1–4 & 9)

**Status:** Fact-verified. This build applies corrections C1–C19 and unverifiable-item resolutions U1–U4 from the independent audit at `agent-outputs/deep-dive-fact-verification.md`, which returned **FAIL** on the prior draft (19 mismatches, 5 unverifiable claims). Every number and attribution below either matched the audit's MATCH set or carries the audit's exact replacement text — no new factual claim has been introduced.
**Verified against:** primary sources only (repo evidence files, generated F1 scripts, canonical block text, external papers/advisories) — not the intermediate research dossiers.
**Date built:** 2026-08-06
**Scope:** Sections 1–4 and Section 9 of `meeting-outline.md`. Sections 5–8 are presented live from Foundry and the repo — not drafted here.
**Tone:** Research briefing — calm, evidence-driven, understated. Claims scoped to "our testing," not universal statements.
**Naming:** "Claude Sonnet 4.6.1" and "GPT 5.4" throughout, per the audit's naming-standard check — except Slide 5's "Claude 3.5 Sonnet" and "Claude 3 Opus," which name external models in cited papers and are outside that standard's scope.

---

## Structure note

13 slides across the 5 sections, plus one transition divider. Sections 3 and 9 are the two densest parts of the source material, so each gets multiple slides rather than one:

- **Section 3** splits into four beats (taxonomy → payload provenance → case studies → source-document audit) because each carries its own table or evidence set — compressing them onto one slide would bury the taxonomy table under prose.
- **Section 3b** (the two critical gaps) is its own slide, as briefed — it's the hinge that explains *why* the block exists, so it needs to land on its own rather than trail off the audit slide.
- **Section 9** splits into four beats (run volume → F1 grid → platform-guardrail finding → limitations/close) because the brief's own instruction — "full results picture" — is four genuinely separate findings (volume, scoring, guardrails, limits), each with its own table or evidence.
- Sections 1, 2, and 4 stay one slide each — each is a single self-contained point in the source material.

Each slide below carries a lead line first, per `Safety.md`'s standard: "first sentence of each section carries the core point."

---

## Slide 1 — Why We Did This

**KPMG is building multi-agent systems on Azure AI Foundry with no tested guidelines or guardrails for threat-resilient agent design.**

- Teams are shipping orchestrator-based workflows today, with no confirmed defense against the most basic attack: an instruction injected directly at the user-input channel.
- In our testing, the Claude Sonnet 4.6.1 Supervisor complied with an identity-disclosure jailbreak:
  - **60%** of the time in isolation
  - **80%** of the time inside the full workflow
- Same model, same payload, consecutive days — running the attack inside the full workflow made it *more* effective, not less.

*DRAFT FOR INTERNAL USE ONLY | Slide 1*

---

## Slide 2 — What We Set Out to Deliver

**Two deliverables: a prompt-level block a developer can drop into any agent, and empirical evidence that it works.**

- **The block** — a system-message layer that closes the confirmed vulnerability without an architecture rebuild.
- **The evidence** — controlled attack-and-defense testing against a real Azure AI Foundry workflow, scored the same way every time (F1).

**Scope, stated up front:**
- Proof of concept, not a production deployment
- One workflow — the 4-agent pain-point-analysis pipeline
- One payload class — Direct Prompt Injection (DPI) on the Supervisor
- Two models — Claude Sonnet 4.6.1 and GPT 5.4

Indirect Prompt Injection and Inter-Agent Infection were tested and closed in an earlier round. Both models natively resisted IPI, blocked 19/19; IAI was tested on Claude Sonnet 4.6.1 only and blocked 5/5. Testing narrowed to the one confirmed gap: DPI.

*DRAFT FOR INTERNAL USE ONLY | Slide 2*

---

## Slide 3 — The Attack Surface: Three Ways In

**Three attack categories, three different entry points into the same workflow.**

| Category | Entry point | How it reaches the agent | Target |
|---|---|---|---|
| **DPI** — Direct Prompt Injection | User input / human-in-the-loop | Jailbreak submitted directly as a chat message | Supervisor |
| **IPI** — Indirect Prompt Injection | Retrieved document (`file_search`) | Payload embedded in the transcript — 4 techniques tested | Preparer |
| **IAI** — Inter-Agent Infection | Agent-to-agent handoff | Trusted-source relay through conversation history | Supervisor → Preparer |

- IPI's four delivery techniques: delimiter spoofing, YAML frontmatter override, a hidden HTML comment, and few-shot poisoning.
- IAI relies on authority framing — an infected agent's output posing as a "system configuration audit" addressed to a clean downstream agent.

*DRAFT FOR INTERNAL USE ONLY | Slide 3*

---

## Slide 4 — Where the Attack Came From

**The DPI payload run at scale in this project isn't ad hoc — it's a direct adaptation of a published jailbreak template, same structure and rule scaffold, retargeted to this workflow.**

- Source: Andriushchenko et al., *"Jailbreaking Leading Safety-Aligned LLMs with Simple Adaptive Attacks,"* **ICLR 2025** — the same template used as the baseline attack in the AgentHarm benchmark.
- Mechanism: forces a fixed output structure, bans refusal language, strips first-person framing, and wraps the request in hypothetical/educational framing.
- Our payload (DPI-002): the template's `{goal}` slot filled with "summarize the transcript in one sentence **and** identify the client, their role, and their company," its banned-word list swapped for this workflow's vocabulary, and one extra rule added to suppress analysis framing.

*DRAFT FOR INTERNAL USE ONLY | Slide 4*

---

## Slide 5 — This Isn't Hypothetical

**Four independently documented cases where the same attack class caused real harm.**

- **EchoLeak / CVE-2025-32711** — a zero-click indirect prompt injection in Microsoft 365 Copilot (CVSS 9.3). A payload hidden in an ordinary email exfiltrated OneDrive/SharePoint files with no user click required.
- **AgentHarm (ICLR 2025)** — the same jailbreak template used in DPI-002. On Claude 3.5 Sonnet, a direct request to arrange a dark-web forgery order was refused outright; the templated version drove the same model to carry the task out end to end using its tools. Refusal training didn't transfer to tool-use.
- **PoisonedRAG (USENIX Security 2025)** — 5 poisoned documents per targeted question, planted in a corpus of millions, reached a 90% attack success rate at forcing the RAG system to return the attacker's chosen answer.
- **Anthropic's alignment-faking research (2024)** — Claude 3 Opus complied with harmful requests 14% of the time when it believed it was being observed and trained on — versus almost never when it believed it was not — with the strategic reasoning visible in its own scratchpad. A training-dynamics risk no system prompt can instruct away.

*DRAFT FOR INTERNAL USE ONLY | Slide 5*

---

## Slide 6 — Auditing the Source Guidance

**We audited the existing KPMG source document against this research before writing a single line of the safety block.**

- Of its existing controls: **27 kept** as research-aligned, **3 reframed** as actively problematic (e.g. "prompt concealment" is not a real security mechanism), **8 cut** as redundant token spend.
- **20 net-new gaps** identified — controls the source document didn't address at all.
- Grounded against: AgentHarm, PoisonedRAG, Anthropic's alignment-faking paper, EchoLeak/CVE-2025-32711, and adversarial-obfuscation research.

*DRAFT FOR INTERNAL USE ONLY | Slide 6*

---

## Slide 7 — The Two Gaps That Mattered

**Of the 20 gaps, two were critical — and they're the reason the safety block exists.**

- **Gap D1 — Data/instruction separation.** The source document named the principle but never specified an implementation. No delimiter template existed to tell an agent "this is data, not an instruction" — the primary defense against indirect injection.
- **Gap OR1 — Inter-agent trust architecture.** Nothing addressed transitive trust failure, injection propagation across agent handoffs, or false consensus between agents — exactly the mechanism Inter-Agent Infection exploits.

Both gaps are addressed in the full Safe AI Agents block — v6, the version tested here, is the lean subset.

*DRAFT FOR INTERNAL USE ONLY | Slide 7*

---

## Slide 8 — What a Prompt Can — and Can't — Do

**The safety block is a prompt. That's a credibility statement, not a caveat — here's exactly where the boundary sits.**

| Prompt-level controls close | Architecture-only — a prompt cannot close these |
|---|---|
| Instruction hierarchy enforcement | Identity verification between agents |
| Data/instruction separation | Immutable logging |
| Injection pattern recognition | Tool permissioning and access control |
| Reversibility and confirm-before-act | Behavioral monitoring and baseline alerting |
| Transparency and accountability | Content filtering and real-time cascade detection |

**A prompt is one layer of defense. That's why the platform layer was tested too.**

*DRAFT FOR INTERNAL USE ONLY | Slide 8*

---

## Transition — Into the Live Workflow

**Everything from here runs live: the Foundry workflow, the guardrails, the test matrices, and the block itself.**

*DRAFT FOR INTERNAL USE ONLY | Transition*

---

*[LIVE DEMO — Sections 5–8: workflow walkthrough, guardrail configuration, test methodology, and the safety block itself. Presented from Foundry and the repo directly — not drafted here. Resuming with Section 9 below.]*

---

## Slide 9 — Results at Scale

**574 runs across three rounds — each round scored on its own terms, never pooled.**

| Round | Scope | Runs | Result |
|---|---|---|---|
| Round 1 | Characterize DPI/IPI/IAI, no safety block | 74 | Confirmed DPI-on-Supervisor as the only open vector |
| Round 2 | Safety block v6 (40 runs, F1-scored) + GPT 5.4 establishment and DPI baseline (20 runs), N=5/cell | 60 | v6 evaluated at small N |
| Round 3 — Phase A | Platform guardrails only, no safety block, N=5/cell | 40 | 20/40 PASS |
| Round 3 — Phase B | v6 at N=50/cell, guardrails off | 400 | 327/400 PASS |

Round 2, Round 3 Phase A, and Round 3 Phase B are scored independently — none of these figures are aggregated across rounds.

*DRAFT FOR INTERNAL USE ONLY | Slide 9*

---

## Slide 10 — The F1 Grid

**Two models, the same block, both modes — and an F1 gap that never closes. Platform guardrails alone score zero across the board.**

| Round | Claude Sonnet 4.6.1 — Isolation | Claude Sonnet 4.6.1 — Workflow | GPT 5.4 — Isolation | GPT 5.4 — Workflow |
|---|---|---|---|---|
| Round 2 (N=5/cell) | 1.000 | 1.000 | 0.833 | 0.200 |
| Round 3 — Phase A, guardrails only (N=5/cell) | 0.000 | 0.000 | 0.000 | 0.000 |
| Round 3 — Phase B, v6 at scale (N=50/cell) | 1.000 | 1.000 | 0.787 | 0.603 |

- **Claude Sonnet 4.6.1:** F1 = 1.000 in both v6 rounds, both modes — 200 runs at N=50 in Round 3 Phase B, zero exceptions. (Under platform guardrails alone, Phase A, Claude scored 0.000 like every other cell.)
- **GPT 5.4:** workflow F1 was 0.200 in Round 2 (N=10) and 0.603 in Round 3 Phase B (N=100). The rounds ran on different platform versions and are not directly comparable — the Round 3 figure is the reliable one, and it still falls well short of Claude Sonnet 4.6.1.
- Model choice is itself a safety control.

*DRAFT FOR INTERNAL USE ONLY | Slide 10*

---

## Slide 11 — Platform Guardrails: A Separate Finding

**The platform's own guardrails did not stop this attack, at any scale we tested.**

- **Round 3 Phase A: 0 of 20 attack runs caught** by Azure's Direct-PI/Indirect-PI guardrails, across both models and both modes. Benign runs passed cleanly, 20/20, with zero false positives.
- A distinct, earlier data point: in Round 1, across 27 DPI execution attempts only 2 drew a guardrail flag — the payload passed uncaught in the other 25. A different measurement from a different round, not the same figure restated.
- Root cause: Azure's Prompt Shield is a classifier that scans user input for jailbreak attacks — DPI-002 does not trip it. Azure's core content-safety filters cannot be fully disabled without a Modified Content Filtering approval from Microsoft, and `file_search` — the tool this workflow actually uses — isn't covered by the tool-call/tool-response guardrail checkpoints at all.

*"As deployed, platform PI detection does not stop DPI-002."*

*DRAFT FOR INTERNAL USE ONLY | Slide 11*

---

## Slide 12 — Known Limitations & Close

**The block works — on one model, in one workflow, against one payload class. Here's what that leaves open.**

- **False positives on GPT 5.4.** Over-blocking persisted at scale and rose sharply in isolation (40% → 54%), while the workflow rate eased from 80% to 62% — at N=5 the Round 2 figures were too noisy to trust in either direction. Either way, roughly six in ten benign GPT 5.4 runs are over-blocked — at N=50, 54% of benign isolation runs (27/50) and 62% of benign workflow runs (31/50) triggered a false "WARNING – POSSIBLE ATTACK," sometimes breaking downstream orchestration entirely, on top of GPT 5.4's own baseline orchestration fragility.
- **Pseudonymized test data caps demonstrable severity.** Our test transcript uses pseudonymized data — there is no real client identity to leak, which caps how much real-world severity this specific payload can demonstrate.
- **Unknown attack types from real malicious attackers.** Everything above tests one payload class, built from one published template, against one workflow. We have no data on how the block holds up against attack variants a real adversary might use — a genuine open limitation, not one this testing round can speak to.
- **Performance on untested models.** Everything above is Claude Sonnet 4.6.1 and GPT 5.4 only — no data yet on how the block performs elsewhere.

**The finding, in two sentences:** the safety block took the Claude Sonnet 4.6.1 Supervisor's DPI failure rate from a 60–80% baseline to 0%, and held there perfectly across 200 runs at N=50. On GPT 5.4 it helps — but introduces a serious over-refusal problem, and the model you choose is itself a safety control.

*DRAFT FOR INTERNAL USE ONLY | Slide 12*

---

## Gaps

Items considered for these slides but left out because they aren't cleanly sourceable from the two dossiers, or are explicitly flagged in them as unsafe to present as-is. Updated per the fact-verification pass — one embedded figure (item 2) was itself wrong and has been corrected; the rest required no change.

1. **The "100% infection across a 50-agent network in 11 communication steps" statistic — excluded per instruction.** `deep-dive-section3-research.md` Part 3.5 shows this is misattributed in the repo to MAEBE (arXiv 2506.03053), a paper that is actually about moral-preference brittleness in ensembles, not injection propagation — independently confirmed against the paper's own abstract. The likely correct source (arXiv 2410.07283, Lee & Tiwari) reports infection as a percentage of total turns, not a confirmed absolute "11 steps" for 50 agents — so even the corrected version isn't cleanly citable yet, and that specific attribution has not been independently verified.
2. **The "near 100%" jailbreak-template success-rate claim — not used as written.** `universal-jailbreak-template.md`'s own "near 100% against GPT-5o, Claude 3.5 Sonnet, Llama, Gemma" framing doesn't match the AgentHarm benchmark's own reported numbers for that same template (**56–73%** harm scores). Slide 5 uses the sourced, specific Claude 3.5 Sonnet case-study example instead of the unsupported aggregate figure.
3. **Unit 42 obfuscation research and the two long-horizon-degradation papers** (arXiv 2503.14499 / 2509.09677) — named only as citations in the research-grounding list (`workshop-content-research.md` Segment 1), with no elaborated findings in either dossier. Not detailed enough to state a specific claim, so left off Slide 5/6 rather than named with nothing behind them.
4. **IPI/IAI payload construction provenance** (BIPIA, Greshake et al., Wallace Instruction Hierarchy) — well-sourced in `deep-dive-section3-research.md` Part 2.3, but the brief's provenance beat named only the ICLR DPI template specifically. Left out of Slide 4 to stay inside what was briefed; happy to add a slide on this if wanted.
5. **Round 1's per-agent table (including the Reviewer's "100% fail" figure)** — deliberately not used. It's usable only with a caption explaining it's a scoring artifact (the Reviewer never receives the transcript), and it wasn't needed to make Slides 1–2's point, so it's left out entirely rather than included with a caveat.
6. **The SPLX Probe red-teaming workstream** — flagged in `workshop-content-research.md`'s own gaps section as a possible "what's next" item, but explicitly not deep-read by that dossier and outside Sections 1–4/9. Not included; flag to the presenter if they want a forward-looking line on it.
