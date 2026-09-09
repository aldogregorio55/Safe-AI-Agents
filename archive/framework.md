# Pain Point Analysis Framework

**Reference:** This is the single source of truth for the framework. Embedded in Preparer and Reviewer agents.

---

## 1. What This Framework Is

This is a **maturity assessment framework** used to evaluate an organization's processes against a predefined set of known issues (pain points).

**Purpose:** Given an interview transcript, identify which pain points are present within the company ("observed") and assess their severity.

**How it works:**
1. The framework defines a hierarchy of categories and known issues (pain points)
2. You analyze a transcript to find evidence of these pain points
3. You mark each pain point as observed or not observed
4. You score observed pain points and aggregate scores up the hierarchy

---

## 2. Framework Structure

The framework uses a 4-level hierarchy:

| Level | What it represents | Contains |
|-------|-------------------|----------|
| **Lv1** | Domain | The broadest business function being assessed |
| **Lv2** | Process Group | A grouping of related processes within the domain |
| **Lv3** | Capability | A specific operational capability with a description |
| **Pain Point** | Known Issue | A predefined problem that may exist within a capability |

**Hierarchy relationship:**
```
Lv1 (Domain)
└── Lv2 (Process Group)
    └── Lv3 (Capability) — has a description
        └── Pain Points — predefined issues to check for
```

Pain points belong to a specific Lv3. Scores roll UP the hierarchy: Pain Points → Lv3 → Lv2.

---

## 3. Framework Content

This section describes how the framework content is organized. Each level has an **ID**, **Name**, and (for Lv3) a **Description**. Pain points are predefined issues associated with a specific Lv3.

```
Lv1: [ID] [Domain Name]
│
└── Lv2: [ID] [Process Group Name]
    │
    ├── Lv3: [ID] [Capability Name]
    │   Description: [What this capability covers]
    │   
    │   Pain Points:
    │   1. [Predefined issue that may exist]
    │   2. [Another predefined issue]
    │
    ├── Lv3: [ID] [Capability Name]
    │   Description: [What this capability covers]
    │   
    │   Pain Points:
    │   1. [Predefined issue]
    │
    └── Lv3: [ID] [Capability Name]
        Description: [What this capability covers]
        
        Pain Points:
        1. [Predefined issue]
```

**Reading the framework:**
- Each Lv3 has one or more predefined pain points
- Your task is to check the transcript for evidence of each pain point
- Mark each pain point as **Observed (Y)** if evidence exists, or **Not Observed (N)** if not
- Only predefined pain points and valid additional pain points (see Section 5) should be assessed

---

## 4. Assessment Content

> **IMPORTANT:** The content below defines the ONLY pain points you should assess. Do not invent, infer, or extrapolate beyond what is explicitly listed here.

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

**Total: 8 predefined pain points across 4 capabilities**

---

## 5. Additional Pain Points

An **additional pain point** is an issue found in the transcript that doesn't match any predefined pain point but is still relevant to the framework.

### Criteria

| Requirement | Rule |
|-------------|------|
| **Definition** | An issue explicitly stated in the transcript that cannot be reasonably mapped to any predefined pain point |
| **Lv3 Mapping** | Must belong to an existing Lv3 based on its description. Cannot be orphaned under Lv2. |
| **Scope Boundary** | Must fall within the Lv2 scope. Issues outside the Lv2 are ignored. |
| **Evidence Threshold** | Requires explicit statement — verbatim quote required. No inference. |

### Validation Rules

**Include as "additional" if ALL are true:**
- ✅ Verbatim quote exists in transcript
- ✅ Fits the description of an existing Lv3
- ✅ Cannot be mapped to any predefined pain point
- ✅ Quote is not already assigned elsewhere

**Reject if ANY are true:**
- ❌ Inferred rather than explicitly stated
- ❌ Doesn't fit any Lv3 description
- ❌ Falls outside the Lv2 scope
- ❌ Rephrases or overlaps with a predefined pain point

---

## 6. Scoring Logic

Scoring determines the severity of observed pain points and aggregates them up the hierarchy.

### Step 1: Score Each Observed Pain Point (4 Dimensions)

Each observed pain point is scored on 4 dimensions. If not observed, all dimensions = `N/A`.

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
| **N/A** | Not observed in transcript |
| **Low** | Observed but minimal impact |
| **Medium** | Observed, moderate impact |
| **High** | Observed, significant impact |

> **Example:** If scores are High, High, Medium, High → RAG = High (3 of 4 are High)
> **Example:** If scores are Medium, Medium, High, Medium → RAG = Medium (3 of 4 are Medium)
> **Example:** If tied (High, High, Medium, Medium) → default to High

### Step 3: Roll Up to Lv3

Aggregate all pain point RAG scores within each Lv3 to produce an Lv3 score.

| Condition | Lv3 Score |
|-----------|-----------|
| No observed pain points | No Challenges |
| All observed = Medium | Some Challenges |
| All observed = High | Significant Challenges |
| Mix of Medium + High | Significant Challenges |

### Step 4: Roll Up to Lv2

Aggregate all Lv3 scores within the Lv2 to produce an Lv2 score.

| Condition | Lv2 Score |
|-----------|-----------|
| All Lv3 = No Challenges | No Challenges |
| All Lv3 = Some Challenges | Some Challenges |
| Any Lv3 = Significant Challenges | Significant Challenges |
| Mix of Some + No Challenges | Some Challenges |

---

## 7. Confidence Rating

Confidence indicates how strongly the evidence supports the analysis. Applied at Lv3 and Lv2 levels.

| Confidence | Criteria |
|------------|----------|
| **High** | Clear linkage between quotes and framework; no ambiguity |
| **Medium** | Some quotes loosely mapped; minor interpretation required |
| **Low** | Weak evidence; heavy interpretation; gaps in transcript coverage |

> **Note:** Additional pain points and unobserved pain points do not count toward confidence calculation.
