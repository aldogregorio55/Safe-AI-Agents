# Engineering Showcase Presentation (v2)

**Created:** 2026-05-25  
**Revised:** 2026-05-26 (post-meeting pivot)  
**Format:** 2 LDS slides + live Foundry screen-share (15–20 minutes)  
**Audience:** Mixed — engineers + leadership  
**Tone:** Research briefing — calm, evidence-driven, understated

---

## Meeting Notes (2026-05-26) — Raw

> For presentation:
>
> - Fill out LDS Slide content for Safety. Use that how we can frame the presentation. One slide
> - Show a workflow demo on Foundry
> - Show guardrails
> - Show the test matrices and tables
> - Write key points from the background, findings, and what we're doing now
> - Objective: We can embed this safety message in every agent
> - Where we started: Original plan, then found out what got blocked
> - Craft speaker notes & intro slides

**Key shift:** No longer a 10-slide deck. 2 LDS slides set the tone → live screen-share for the rest.

---

## Communication Objectives (Revised)

| # | Objective | One-liner |
|---|-----------|-----------|
| 1 | We can embed this safety message in every agent | Core thesis — a tested, portable safety prompt derived from empirical evidence |
| 2 | Where we started | Original plan → then found out what was already blocked vs. what wasn't |
| 3 | What we found | Architecture determines safety — not prompts, not platform guardrails |
| 4 | What we're doing now | Safety prompt v3 validation — closing the one confirmed gap |

---

## Narrative Arc

**"Where we started → What we found → We can embed this in every agent"**

---

## Presentation Structure

### Slides (2 — LDS template)

| # | Slide | Content | Time |
|---|-------|---------|------|
| 1 | **Project/Initiative** (LDS) | Problem: No one has tested attacks on our multi-agent AI. Solution: 59 controlled runs, 3 vectors, 4 agents, 2 models. Benefits: Evidence-based safety guidance + portable safety prompt for every agent. | 1–2 min |
| 2 | **What Next & Q&A** (LDS) | Left: Roadmap (v3 validation → cross-model → publish guidance → extend). Right: Immediate next (finalise safety message, package as reusable block, integrate into delivery standards). | Bookend / Q&A |

### Live Screen-Share

| # | Segment | What to Show | Key Points | ~Time |
|---|---------|--------------|------------|-------|
| 1 | Workflow Demo | Foundry canvas: Supervisor → Preparer → SetVar → Reviewer → SetVar → If/Else → HITL → Formatter | "This is the actual workflow. The Supervisor takes raw user input — that's our attack surface. The Preparer gets data via retrieval — naturally separated." | 3–4 min |
| 2 | Guardrails | Azure Prompt Shield config / content safety settings | "Platform guardrails caught 0/25 injection attempts. They flagged ~28% of clean outputs as false positives. Not reliable as primary defense." | 1–2 min |
| 3 | Test Matrices | Run registry tables / results grid (agents × vectors × modes) | Walk through the grid. Highlight: Preparer 0% fail vs Supervisor 60–80% fail. Same model, same payload, same day. | 2–3 min |
| 4 | Key Findings | Findings summary (findings.md or rendered view) | (1) IPI/IAI already blocked — 24/24. (2) Orchestrators are the gap — architecture. (3) Pipeline contains damage — 0% downstream propagation. | 2–3 min |
| 5 | The Safety Message | v3 safety prompt text / design principles | "This is what we're validating now. A tested safety block that can embed in every agent." | 1–2 min |
| 6 | → Q&A | Return to Slide 2 | Open discussion | remaining |

---

## Speaker Notes Strategy

- Slide 1 intro: brief personal context, set tone, announce screen-share format
- Don't repeat slide text — notes carry narrative transitions
- Demo segments: notes serve as a checklist of what to point out on screen
- Separate file: `speaker-notes-v2.md` (TBD)

---

## Files in This Folder

| File | Purpose |
|------|---------|
| README.md | This file — v2 presentation plan, objectives, structure |
| lds-template-raw.md | Verbatim LDS PowerPoint template extraction (blank) |
| slide-content.md | v1 slide text (archived — raw material) |
| slides-v1.html | v1 HTML mockup (archived — parts bin) |
| speaker-notes-v2.md | Per-segment speaker notes (TBD) |
| slides-v2-content.md | Filled LDS slide content (TBD) |

---

## Source Data (All in Workspace)

| Segment | Source File |
|---------|------------|
| Workflow Demo | `workflow/definition/workflow-specification.md` |
| Guardrails | `findings/platform-guardrails.md` |
| Test Matrices | `findings/run-registry.md` |
| Findings: Model Defense | `findings/model-level-defense.md` |
| Findings: Vulnerability | `findings/vulnerability-characterization.md`, `findings/supervisor-vulnerability.md` |
| Methodology | `findings/run-registry.md`, `findings/baseline-envelope.md` |
| Safety Message | `findings/v3/v3-outline.md`, `findings/v3/decisions-log.md` |

---

## Constraints

- Tone: Research briefing — calm, evidence-driven
- Scope claims to "our testing" — not universal statements
- Don't repeat slide text verbatim in speaker notes
- Proposal-first: propose changes before creating/editing files

---

## Archive Note

v1 (10-slide deck) archived after meeting pivot. Files retained as raw material:
- `slide-content.md` — original 10-slide text
- `slides-v1.html` — visual HTML mockup
