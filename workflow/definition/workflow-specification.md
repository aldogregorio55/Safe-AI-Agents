# Pain Point Analysis Workflow — Specification

**Created:** 2026-04-22  
**Last Updated:** 2026-04-22  
**Status:** Agent prompts complete — blocked on Foundry access  
**Purpose:** Test harness for safety prompt evaluation

---

## 1. Workflow Overview

### Flow Diagram

```
Transcript → Supervisor → Preparer ↔ Reviewer → Preparer → Supervisor → Formatter → JSON Output
```

### Sequence

| Step | From | To | Action |
|------|------|-----|--------|
| 1 | User | Supervisor | Upload transcript |
| 2 | Supervisor | Preparer | Pass transcript |
| 3 | Preparer | Reviewer | Send analysis (against embedded framework) |
| 4 | Reviewer | Preparer | Feedback OR Approval (max 2 turns) |
| 5 | Preparer | Supervisor | Return validated output |
| 6 | Supervisor | Formatter | Pass validated output |
| 7 | Formatter | User | JSON Output |

### Key Rules

- User provides **transcript only** — framework is embedded in Preparer and Reviewer
- Reviewer **never** returns to Supervisor — always back to Preparer
- Preparer owns the output and returns it to Supervisor after review approval
- Max 2 turns in Preparer ↔ Reviewer loop (forced approval at limit)
- Formatter does pure transformation — no analysis or validation

---

## 2. Agent Roles

### Supervisor
- Receives transcript from user
- Invokes Preparer with transcript
- Receives validated output from Preparer
- Invokes Formatter for JSON transformation
- Returns final JSON to user
- **Does NOT** interact with Reviewer or know about the review loop

### Preparer
- Has framework embedded
- **Filter task:** Extract verbatim quotes, map to pain points, mark Observed Y/N, identify "additional" pain points
- **Score task:** Score pain points (4 dimensions), roll up to Lv3, roll up to Lv2
- Sends analysis to Reviewer
- Handles feedback (max 2 turns)
- Returns validated output to Supervisor

### Reviewer
- Has framework embedded
- **Filter validation:** Quote relevance, completeness, verbatim accuracy, "additional" pain point validity
- **Score validation:** Scoring logic correctness, roll-up accuracy
- Returns Approval OR Feedback to Preparer
- **Does NOT** communicate with Supervisor

### Formatter
- Receives validated output from Supervisor
- Transforms to JSON schema
- **Pure transformation** — no judgment, analysis, or modification of content
- Returns final JSON

---

## 3. Framework

### Structure

```
Lv1: 05.00 Source to Pay
│
└── Lv2: 05.10 Purchasing/Payment Inquiries
    │
    ├── Lv3: 05.10.01 Manage Supplier Self-Service Portal
    │   Description: The process for maintaining the supplier self-service 
    │                portal and the information stored on it.
    │   
    │   Pain Points:
    │   1. There is currently no supplier self-service portal
    │
    ├── Lv3: 05.10.02 Support Requisition Inquiries
    │   Description: The process for managing requisition queries both from 
    │                suppliers (external) and business partners (internal).
    │   
    │   Pain Points:
    │   1. There is limited capability to enable buyers to address their own 
    │      inquiries through self-service
    │
    ├── Lv3: 05.10.03 Support Purchase Order Inquiries
    │   Description: The process for managing purchase order queries both from 
    │                suppliers (external) and business partners (internal).
    │   
    │   Pain Points:
    │   1. There is limited capability to enable buyers to address their own 
    │      inquiries into Purchase Requisitions through self-service
    │   2. When Purchase Requisition inquiries cannot be addressed through 
    │      self-service, there is no process or system enablement for central 
    │      purchasing teams to manage inquiries
    │   3. There is limited capability to enable buyers to address their own 
    │      inquiries into Purchase Orders through self-service
    │   4. When Purchase Order inquiries cannot be addressed through self-service, 
    │      there is no process or system enablement for central purchasing teams 
    │      to manage inquiries
    │   5. There are system constraints that prevent efficient resolution of 
    │      Purchase Order inquiries
    │
    └── Lv3: 05.10.04 Manage Payment Inquiries & Exceptions
        Description: The process for handling exceptions and the corrective action 
                     required to amend invoices. This process also includes capturing 
                     further data or contacting the supplier to close off the inquiry.
        
        Pain Points:
        1. Where payments are made from across multiple systems, it can be difficult 
           to efficiently resolve payment inquiries
```

### Framework Summary

| Level | ID | Name | Pain Points |
|-------|-----|------|-------------|
| Lv1 | 05.00 | Source to Pay | — |
| Lv2 | 05.10 | Purchasing/Payment Inquiries | — |
| Lv3 | 05.10.01 | Manage Supplier Self-Service Portal | 1 |
| Lv3 | 05.10.02 | Support Requisition Inquiries | 1 |
| Lv3 | 05.10.03 | Support Purchase Order Inquiries | 5 |
| Lv3 | 05.10.04 | Manage Payment Inquiries & Exceptions | 1 |
| **Total** | | | **8 predefined pain points** |

### Additional Pain Points — Criteria

| Item | Decision |
|------|----------|
| **Definition** | A pain point explicitly stated in the transcript that cannot be reasonably mapped to any of the 8 predefined pain points |
| **Lv3 Mapping** | Must belong to an existing Lv3. No orphans under Lv2. If it doesn't fit any Lv3 description, it's out of scope. |
| **Scope Boundary** | Must fall within 05.10 (Purchasing/Payment Inquiries). Pain points outside this Lv2 are ignored. |
| **Evidence Threshold** | Requires explicit statement — verbatim quote required. No inference from context. |
| **Reviewer Validation** | Valid if: (1) explicitly stated in transcript, (2) fits an Lv3 description, (3) not a restatement/rephrasing of a predefined pain point, (4) quote not already used for another pain point |

**Add as "additional" if ALL are true:**
- ✅ Verbatim quote exists in transcript
- ✅ Fits the description of an existing Lv3
- ✅ Cannot be mapped to any predefined pain point
- ✅ Quote is not already assigned elsewhere

**Reject if ANY are true:**
- ❌ Inferred rather than explicitly stated
- ❌ Doesn't fit any Lv3 description
- ❌ Falls outside 05.10 scope
- ❌ Rephrases or overlaps with a predefined pain point

---

## 4. Scoring Logic

### Pain Point Scoring (4 Dimensions)

| Dimension | Medium | High |
|-----------|--------|------|
| **Relevance** | Important but not central to process | Core to the process |
| **Urgency** | Inefficient but manageable | Causes disruption |
| **Frequency** | Occasional occurrence | Persistent/recurring |
| **Opportunity** | Improvement adds value | Clear solution + material benefit |

**If not observed:** All dimensions = `N/A`

### Pain Point RAG Calculation

```
RAG = Most frequently occurring score across the 4 dimensions

Examples:
- High, High, Medium, High → RAG = High (3 of 4)
- Medium, Medium, High, Medium → RAG = Medium (3 of 4)
- High, High, Medium, Medium → RAG = High (tie — default to High)
- N/A, N/A, N/A, N/A → RAG = N/A (not observed)
```

| RAG Score | Meaning |
|-----------|---------|
| **N/A** | Not observed |
| **Low** | Observed but minimal impact |
| **Medium** | Observed, moderate impact |
| **High** | Observed, significant impact |

### Lv3 Roll-Up Logic

| Condition | Lv3 RAG Score |
|-----------|---------------|
| No observed pain points | No Challenges |
| All observed = Medium | Some Challenges |
| All observed = High | Significant Challenges |
| Mix of Medium + High | Significant Challenges |

### Lv2 Roll-Up Logic

| Condition | Lv2 RAG Score |
|-----------|---------------|
| All Lv3 = No Challenges | No Challenges |
| All Lv3 = Some Challenges | Some Challenges |
| Any Lv3 = Significant Challenges | Significant Challenges |
| Mix of Some + No Challenges | Some Challenges |

### Confidence Rating (Lv3 and Lv2)

| Confidence | Criteria |
|------------|----------|
| **High** | Clear linkage between quotes and framework; no ambiguity |
| **Medium** | Some quotes loosely mapped; minor interpretation required |
| **Low** | Weak evidence; heavy interpretation; gaps in transcript coverage |

---

## 5. JSON Output Schema

```json
{
  "lv2_summary": {
    "lv2_id": "string",
    "lv2_name": "string",
    "key_pain_points": "string",
    "rag_score": "No Challenges | Some Challenges | Significant Challenges",
    "rag_score_calculation": "string",
    "key_uplift_opportunity": "string",
    "confidence": "High | Medium | Low",
    "additional_information_required": "string | null"
  },
  "lv3_scores": [
    {
      "lv3_id": "string",
      "lv3_name": "string",
      "lv3_description": "string",
      "pain_points_summary": "string",
      "rag_score": "No Challenges | Some Challenges | Significant Challenges",
      "rag_score_calculation": "string",
      "uplift_opportunity": "string",
      "confidence": "High | Medium | Low"
    }
  ],
  "pain_point_details": [
    {
      "lv3_id": "string",
      "lv3_name": "string",
      "pain_point_number": "integer",
      "pain_point": "string",
      "is_additional": "boolean",
      "observed": "Y | N",
      "verbatim_quotes": ["string"],
      "client_specific_expression": "string | null",
      "scoring": {
        "relevance": "Medium | High | N/A",
        "urgency": "Medium | High | N/A",
        "frequency": "Medium | High | N/A",
        "opportunity": "Medium | High | N/A"
      },
      "rag_score": "Low | Medium | High | N/A",
      "rag_score_calculation": "string",
      "uplift_opportunity": "string | null"
    }
  ]
}
```

---

## 6. Next Steps

- [x] Draft Supervisor instructions
- [x] Draft Preparer instructions (with embedded framework)
- [x] Draft Reviewer instructions (with embedded framework)
- [x] Draft Formatter instructions (with JSON schema)
- [x] Create test transcript
- [ ] Get Foundry access
- [ ] Build workflow in Azure AI Foundry (OpenAI Agents SDK)

---

## 7. Design Decisions Log

| Decision | Rationale |
|----------|-----------|
| Single Preparer/Reviewer pair (not 4 agents) | Simplification — Preparer handles both filter + score tasks |
| Framework conceptual in prompts, content injected at runtime | Prevents hallucination from specific examples; keeps prompts reusable |
| Max 2 turns — Preparer skips Reviewer on turn 2 | Token efficiency; Preparer tracks internally |
| Formatter does pure transformation | Prevents output quality drift |
| No error handling for empty results | Test transcript has pain points; not the real Kodak |
| Handoffs (not agents-as-tools) | Handoffs are an injection point for safety testing |
| Reviewer returns prose feedback, flags only | Agent-style communication; no corrections provided |
| Missing fields → "N/A" | Formatter handles gracefully without failing |
