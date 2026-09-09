# Workflow Update Status — 2026-04-23

## Completed

- [x] Created `framework-v2.md` — simplified flat structure (placeholders only)
- [x] Updated `framework-v2.md` — applied meeting feedback (2026-04-27)
  - Removed agent instructions from framework (evidence standard, "Assess ONLY" directive)
  - Added pain point definition and observed pain point definition to Section 3
  - Renamed sections to match corporate framework conventions
  - Removed "How This Framework Was Created" subsection
  - Renamed "RAG Status" → "Framework Scoring" with escalating approach description
- [x] Updated `output-schema-v2.json` — `rag_status` → `score_status`, 1-12 → 1-20
- [x] Drafted updated prompts for all 4 agents (in chat, not yet committed to files)

## Decisions to Confirm with Team

1. **Reviewer transcript access:** Reviewer needs the transcript to verify verbatim quotes. Proposed approach: Preparer passes the transcript along with its analysis in the handoff to Reviewer. Alternative: upload transcript as a knowledge source to Reviewer in Foundry. **Decision: Try handoff approach first — confirm with team.**

2. **HITL mechanism:** Supervisor presents validated analysis to user for approval before sending to Formatter. Implementation depends on Azure AI Foundry capabilities — needs testing.

3. **Framework delivery:** Framework will be uploaded as context/knowledge source in Azure AI Foundry for Preparer and Reviewer.

4. **Open wording decisions:**
   - Scoring bullet in Preparer/Reviewer: "definitions" vs "approach"
   - Preparer handoff says "after turn 2" but review loop says "on turn 3" — same meaning, wording could be tighter

## Parked for Agent Instructions

The following was removed from the framework and should be incorporated into agent prompts (Preparer + Reviewer):

**Evidence Standard**

A pain point is marked Observed (Y) only when:
- A verbatim quote from the transcript explicitly supports its presence
- The evidence is directly stated — not inferred from context

If no verbatim evidence exists, mark as Not Observed (N).

## Pending Updates

### Agent Prompts

**Preparer (preparer.md)**
| Section | Action |
|---------|--------|
| `<task>` | Simplify to: (1) identify observed Y/N, (2) assign RAG |
| `<framework>` | Remove hierarchy explanation entirely |
| `<additional_pain_points>` | Remove entire section |
| `<scoring>` | Remove 4 dimensions, roll-ups, confidence — replace with simple RAG rule |
| `<output_format>` | Remove Lv2/Lv3 summaries — just list pain points with Y/N + RAG |

**Reviewer (reviewer.md)**
| Section | Action |
|---------|--------|
| `<task>` | Simplify to: validate Y/N correctness + RAG assignment |
| `<framework>` | Remove hierarchy explanation |
| `<additional_pain_point_criteria>` | Remove entire section |
| `<scoring_reference>` | Remove — replace with simple RAG reference |

**Supervisor & Formatter** — minimal changes (no scoring logic)

### JSON Schema
- Simplify output structure to match new framework
- Remove Lv2/Lv3 summary sections
- Remove 4-dimension scoring fields
- Remove confidence fields

### workflow-specification.md
- Update framework section to match v2
- Update scoring logic section
- Remove roll-up documentation

## Notes

- Framework v2 is a knowledge base file — minimal, no instructions
- Agent behavior/validation logic stays in agent prompts, not framework
- RAG criteria: N/A (not observed), Medium (observed), High (observed + causes disruption)
