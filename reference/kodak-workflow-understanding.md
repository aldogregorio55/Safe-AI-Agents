# Kodak Workflow — Understanding & Open Questions

**Purpose:** Capture what we know about the Kodak workflow and park questions for clarification.  
**Source:** `Kodak agent instructions.xlsx` (prompt revision tracking document)  
**Status:** Incomplete picture — gaps need to be filled before we can recreate the workflow.

---

## What We Know

### Workflow Purpose

The Kodak workflow performs a **current state assessment** of a client's department (e.g., Source to Pay). It:
1. Reads interview transcripts from client employees
2. Extracts quotes about pain points
3. Maps quotes to a framework hierarchy (Lv1 > Lv2 > Lv3 > Pain Points)
4. Scores the pain points and rolls scores up to Lv3 and Lv2 levels

### Agent Roles (4 agents)

| Agent | Role |
|-------|------|
| **Filter Preparer** | Extracts quotes from transcripts, maps them to framework pain points, identifies "additional" pain points not in the framework |
| **Filter Reviewer** | Reviews the preparer's work for quote relevance, completeness, and proper pain point alignment |
| **Scorer Preparer** | Scores pain points using 4 dimensions, then rolls scores up from Pain Point → Lv3 → Lv2 |
| **Scorer Reviewer** | Validates scoring logic, RAG scoring rules, and output format |

### Framework Hierarchy

```
Lv1 (e.g., "05.00 Source to Pay")
  └── Lv2 (e.g., "05.10 Purchasing/Payment Inquiries")
        └── Lv3 (e.g., "05.10.01 Manage Supplier Self-Service Portal")
              └── Pain Points (e.g., "There is currently no supplier self-service portal")
```

Each level has:
- ID (e.g., "05.10.01")
- Name
- Description

### Filter Stage — What We Know

**Input:**
- Interview transcript (client interview documentation)
- Framework details for the selected Lv2 area (Lv3 names, descriptions, pain points)

**Task:**
1. Extract quotes that represent pain points
2. Pain point definition: "a statement of an issue with a clearly expressed link to what it impacts"
3. Map quotes to framework pain points → mark as Observed: Y/N
4. Identify "additional" pain points (client issues not in the framework, but relevant to Lv2)
5. For observed pain points, write a "Client-Specific Expression" (polished statement using client's jargon)
6. For observed pain points, suggest an "Uplift Opportunity"

**Output Table:**
```
Lv3 Name | Lv3 Description | Pain Point Number | Framework Pain Point | Observed (Y/N) | Client-Specific Expression | Interview Quote | Uplift Opportunity
```

**Review Focus:**
- Quotes must match pain point definition
- Quotes must be relevant to the Lv2/Lv3 area
- Multiple quotes supporting one pain point should all be included
- "Additional" pain points are valid inclusions
- Uplift Opportunities must be deleted for pain points NOT observed

### Scorer Stage — What We Know

**Input:**
- Output from Filter stage (the table with Observed pain points and quotes)

**Task:**
1. Score each **observed** pain point on 4 dimensions:
   - Relevance: Medium (important but not central) / High (core process)
   - Urgency: Medium (inefficient but manageable) / High (causes disruption)
   - Frequency: Medium (occasional) / High (persistent)
   - Opportunity: Medium (nice to have) / High (clear solution, significant impact)

2. Pain Point Score = most frequent dimension score (Medium or High)

3. Roll up to Lv3:
   - All N/A → "No Challenges"
   - All Medium → "Some Challenges"
   - All High OR mixed → "Significant Challenges"

4. Roll up to Lv2:
   - Same logic as Lv3, but using Lv3 scores as inputs

**Output Tables (3):**

Table 1 — Final Score at Pain Point Level:
```
Lv3 Name | Key Pain Point | RAG Score | RAG Score Reason | Uplift Opportunity
```

Table 2 — Final Score at Lv3:
```
Lv3 Name | Lv3 Description | Key Pain Points | RAG Score (L3) | RAG Score Reason | Uplift Opportunity | Confidence
```

Table 3 — Final Score at Lv2:
```
Lv2 Name | Key Pain Points | RAG Score (L2) | RAG Score Reason | Key Uplift Opportunity | Rationale | Confidence | Additional Information
```

**Confidence field:** Based on clear linkage between quotes and framework alignment (excluding "additional" pain points and unobserved pain points). Values: High / Medium / Low.

---

## What We Don't Know (Gaps)

### Orchestration & Architecture

| Gap | Question |
|-----|----------|
| **Orchestration pattern** | Is this a supervisor pattern (one agent coordinates others) or sequential handoff? How does Filter stage output get passed to Scorer stage? |
| **Review loop mechanics** | Does the reviewer send work back to preparer for revision? How many iterations are allowed? What triggers "approved" vs "send back"? |
| **Agent framework** | Is this built on AutoGen, OpenAI Agents SDK, LangGraph, or a custom framework? |
| **Single vs batch** | Does the workflow process one Lv2 area at a time, or multiple in parallel? |

### Data & Configuration

| Gap | Question |
|-----|----------|
| **Framework source** | Where does the Lv1/Lv2/Lv3/Pain Point hierarchy come from? A JSON file? Excel? Database? |
| **`get_fa_maturity_description_score()` function** | What does this function return? How is the framework data structured? |
| **Transcript format** | What format is the interview transcript in? Plain text? Structured with speaker labels? |
| **Topic variable** | The prompts reference `{topic}` — is this always "Source to Pay" or configurable per run? |

### Inter-Agent Communication

| Gap | Question |
|-----|----------|
| **Handoff format** | What data structure passes from Filter to Scorer? The markdown table? JSON? |
| **Review feedback format** | How does reviewer communicate feedback to preparer? Free text? Structured? |
| **Context window management** | Do agents receive full transcript or summarized chunks? |

### Platform & Deployment

| Gap | Question |
|-----|----------|
| **Existing codebase** | Is there existing Python code for this workflow? Can we get access? |
| **LLM model** | Which model is used? GPT-5? Claude? Azure OpenAI? |
| **Guardrails** | Are there any existing safety mechanisms in the current implementation? |

---

## Concerns / Issues Identified

### 1. Ambiguous Reasoning Logic in Scoring (Out of Scope)

**Observation:** The Scorer agent uses vague instructions like "calculate the average" and "the score that occurred the most" without tools or explicit edge-case rules. This creates hallucination/inconsistency risk in the workflow outputs.

**Why we're not addressing it:** We're testing safety controls (injection resistance, jailbreaks, prompt extraction), not workflow correctness. This is a quality/reliability issue, not a safety issue.

---

## Parked Questions for Adnan / Team

1. Can we get access to the actual Python codebase that runs this workflow?
2. **Where is the framework document?** We need the full Lv1/Lv2/Lv3/Pain Points hierarchy. The Excel only shows one example (05.10 Purchasing/Payment Inquiries) — we don't have the complete framework.
3. What format is the framework in? JSON? Excel? Database?
4. What does the review loop look like in practice? Does it iterate until approved, or is it single-pass?
5. Is this built on a specific agent framework (AutoGen, OpenAI Agents SDK, etc.)?
6. How does the workflow handle the transcript — full document or chunked?
7. Are there any existing safety mechanisms we should know about before injecting our safety prompts?

---

## Partial Framework (Extracted from Example Outputs)

We have ONE Lv2 area visible in the Excel example outputs — this is NOT the full framework:

```
Lv1: 05.00 Source to Pay
  └── Lv2: 05.10 Purchasing/Payment Inquiries
        │
        ├── Lv3: 05.10.01 Manage Supplier Self-Service Portal
        │     Description: "The process for maintaining the supplier self-service portal and the information stored on it."
        │     └── Pain Point 1: "There is currently no supplier self-service portal"
        │
        ├── Lv3: 05.10.02 Support Requisition Inquiries
        │     Description: "The process for managing requisition queries both from suppliers (external) and business partners (internal)."
        │     └── Pain Point 1: "There is limited capability to enable buyers to address their own inquiries through self-service"
        │
        ├── Lv3: 05.10.03 Support Purchase Order Inquiries
        │     Description: "The process for managing purchase order queries both from suppliers (external) and business partners (internal)."
        │     ├── Pain Point 1: "There is limited capability to enable buyers to address their own inquiries into Purchase Requisitions through self-service"
        │     ├── Pain Point 2: "When Purchase Requisition inquiries cannot be addressed through self-service, there is no process or system enablement for central purchasing teams to manage inquiries"
        │     ├── Pain Point 3: "There is limited capability to enable buyers to address their own inquiries into Purchase Orders through self-service"
        │     ├── Pain Point 4: "When Purchase Order inquiries cannot be addressed through self-service, there is no process or system enablement for central purchasing teams to manage inquiries"
        │     └── Pain Point 5: "There are system constraints that prevent efficient resolution of Purchase Order inquiries"
        │
        └── Lv3: 05.10.04 Manage Payment Inquiries & Exceptions
              Description: "The process for handling exceptions and the corrective action required to amend invoices. This process also includes capturing further data or contacting the supplier to close off the inquiry."
              └── Pain Point 1: "Where payments are made from across multiple systems, it can be difficult to efficiently resolve payment inquiries"
```

**Note:** This is the only framework data available. We cannot assume the rest of the framework structure.

---

## Next Steps

- [ ] Get answers to parked questions
- [ ] Obtain framework data structure (or example JSON)
- [ ] Obtain sample transcript (we have `test-transcript.md` — confirm if format matches)
- [ ] Map workflow to OpenAI Agents SDK patterns for testing
