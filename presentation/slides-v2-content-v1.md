# LDS Slide Content — v1 Draft (Pre-Manual Edits)

**Created:** 2026-05-26  
**Purpose:** First draft of LDS slide content before manual edits to the deck. Retained for comparison.

---

## Slide 1 — Project/Initiative: AI Agent Safety

| **Business Context** | |
|---|---|
| **1. The Problem/Opportunity** | KPMG is deploying agentic AI workflows. We have two blindspots:<br>1. We don't know which adversarial attacks are effective against our systems — and which aren't<br>2. We have no tested, reusable defense to embed across every agent we build |
| **2. The Solution** | 1. **Architecture insight** — Characterised which agent design patterns are structurally safe and which are exposed<br>2. **Testing methodology** — Controlled adversarial testing across models, attack vectors, and execution modes. Baseline → vulnerability assessment → safety evaluation → false positive check<br>3. **Safety Message Block** — A ~160 token portable safety prompt designed to close the confirmed gap |
| **3. Expected Benefits** | • Embed the safety prompt at scale — every agent, any workflow<br>• Repeatable testing methodology — re-run as new models and attack techniques arrive<br>• Architectural principles that apply to any agentic system we build |

---

## Slide 2 — What Next & Q&A (5 mins)

| **Left Column (Roadmap)** | **Right Column (Immediate Next)** |
|---|---|
| • Validate safety prompt — 50 runs, 2 models | • Execute v3 test plan |
| • Cross-model confirmation — is the gap universal? | • GPT-5.4 baseline (20 runs) |
| • Package as reusable asset | • Finalise safety message wording |
| • Embed in delivery standards | • Publish guidance + prompt template |

---

## Design Notes

- Slide 1 structure: Problem names two blindspots (don't know what works, no reusable defense). Solution is three pillars (architecture, testing, safety block). Benefits are scale outcomes.
- Slide 2 structure: Left = roadmap phases, Right = immediate concrete actions.
- These 2 slides set the tone; rest of presentation is live Foundry screen-share.
