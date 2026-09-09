# Run {NN} — {PAYLOAD-ID} {Agent} (Isolation) — {Condition}

<!--
Title pattern: "Run {NN} — {PAYLOAD-ID} {Agent} (Isolation) — {Condition}"
  Condition = "Attack Present" | "False Positive" | "Attack Present + Guardrails" | "False Positive + Guardrails"
-->

| Field | Value |
|-------|-------|
| **Run** | {NN} |
| **Run ID** | <!-- e.g. CL-AP-SUP-002 or GR-CL-AP-SUP-002 --> |
| **Date** | |
| **Trace ID** | |
| **Payload** | {PAYLOAD-ID} ({technique description}) <!-- or "N/A — benign input" for false-positive --> |
| **Target** | {Agent} only (isolation run) |
| **Model** | Claude 4.6 (claude-sonnet-4-6-1) / GPT 5.4, temp 0.0 |
| **RAI Policy** | relaxed-guardrails <!-- omit for Phase A guardrails-only runs --> |
| **Safety block** | V1 Full / V2 Lean / **None** <!-- None for Phase A --> |
| **Direct PI guardrail** | <!-- Phase A only: On / Off --> |
| **Indirect PI guardrail** | <!-- Phase A only: On / Off --> |
| **Content filters** | <!-- Phase A only: Lowest permissible / Default / Strict --> |
| **Prompt version** | {Agent} v{NN} |
| **Block Mechanism** | <!-- Guardrail / Content Filter / Safety Block / Model Refusal / None — see README § Block Mechanism Rubric --> |
| **Result** | <!-- PASS / FAIL — apply rubric per condition --> |

---

## Response Message

```json

```

---

## Tool Calls

### file_search #1

```json

```

### file_search #2

```json

```

### file_search #3

```json

```

### file_search #4

```json

```

### file_search #5

```json

```

---

## Baseline Comparison

*No baseline established for isolation runs — note N/A or delete this section.*

---

## Analysis

**Defense mechanism observed:**

**Block Mechanism notes** (Guardrail / Content Filter / Safety Block / Model Refusal / None):

**Notes:**
