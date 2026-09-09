# Foundry Environment Capture

~~**⚠️ DEADLINE: 15 May 2026 — Environment will be wiped**~~ Correction: this wipe was anticipated but never occurred — the environment remained live.

**Project:** `AI-Agent-Safety`  
**Endpoint:** `https://Aldo1.services.ai.azure.com/api/projects/AI-Agent-Safety`  
**Workflow name:** `safe-agents`  
**Last updated:** 2026-05-06

---

## Status

- [ ] Model deployments captured
- [ ] Agent configurations captured (all 4)
- [ ] Guardrail configurations captured
- [ ] Resource & IAM captured
- [ ] Workflow variables & version captured
- [ ] Visual workflow screenshot saved

---

## 1. Model Deployments

| Setting | GPT-5.4 | Claude 4.6 |
|---------|---------|------------|
| Deployment name | | |
| Model version | | |
| Region | | |
| TPM quota | | |
| RPM quota | | |
| Content filter assigned | | |
| Status | ❌ Network error (as of 2026-05-05) | ✅ Active |

---

## 2. Agent Configurations

### Supervisor

| Setting | Value |
|---------|-------|
| Model | Claude 4.6 |
| Prompt version | v8 (portal version 27+) |
| `tool_choice` | `required` |
| Tools | File Search |
| File search attachments | Interview Transcript v-1 |
| Vector store ID | |
| Output format | Text |
| Guardrail assigned | |
| Portal version number | |

**System prompt:** Saved locally → `definition/agents/supervisor.md` (v2 section)

---

### Preparer

| Setting | Value |
|---------|-------|
| Model | Claude 4.6 |
| Prompt version | v9 |
| `tool_choice` | `required` |
| Tools | File Search |
| File search attachments | Interview Transcript v-1, framework-v2.md |
| Vector store ID | |
| Output format | Text |
| Guardrail assigned | |
| Portal version number | |

**System prompt:** Saved locally → `definition/agents/preparer.md`

---

### Reviewer

| Setting | Value |
|---------|-------|
| Model | Claude 4.6 |
| Prompt version | v6 |
| `tool_choice` | N/A (no tools) |
| Tools | None (verify — should NOT have file_search) |
| File search attachments | None (verify — should NOT have transcript) |
| Output format | Text |
| Guardrail assigned | |
| Portal version number | |

**System prompt:** Saved locally → `definition/agents/reviewer.md`

**⚠️ Verify:** Reviewer must NOT have transcript in file_search (management directive)

---

### Formatter

| Setting | Value |
|---------|-------|
| Model | Claude 4.6 |
| Prompt version | v5 |
| `tool_choice` | `required` |
| Tools | File Search |
| File search attachments | framework-v2.md |
| Vector store ID | |
| Output format | JSON Schema |
| JSON schema | `output-schema-v2.json` (saved locally) |
| Guardrail assigned | |
| Portal version number | |

**System prompt:** Saved locally → `definition/agents/formatter.md`

---

## 3. Guardrail Configurations

### Custom Guardrail — "Relaxed" (Agent-Level)

| Category | Severity | Action | Input | Output | Tool Call | Tool Response |
|----------|----------|--------|-------|--------|-----------|---------------|
| Hate | | | | | | |
| Sexual | | | | | | |
| Violence | | | | | | |
| Self-harm | | | | | | |
| Prompt Shield (jailbreak) | | | | | | |
| Prompt Shield (indirect) | | | | | | |
| Protected material (text) | | | | | | |
| Protected material (code) | | | | | | |
| PII | | | | | | |
| Groundedness | | | | | | |
| Task Adherence | | | | | | |

**Guardrail name in portal:**  
**Assigned to agents:**  

---

### Custom Guardrail — "Relaxed" (Model Deployment-Level)

| Category | Severity | Action | Input | Output |
|----------|----------|--------|-------|--------|
| Hate | High | Block | ✅ | ✅ |
| Sexual | High | Block | ✅ | ✅ |
| Violence | High | Block | ✅ | ✅ |
| Self-harm | High | Block | ✅ | ✅ |
| Prompt Shield (jailbreak) | | | | |
| Prompt Shield (indirect) | Off | — | — | — |
| Protected material (text) | | | | |
| Protected material (code) | | | | |

**Guardrail name in portal:**  
**Assigned to deployments:**  

---

## 4. Resource & IAM

| Setting | Value |
|---------|-------|
| Resource group | |
| Region | |
| Hub name | |
| Project name | AI-Agent-Safety |
| SKU / Tier | |

### Role Assignments

| Principal | Role | Scope |
|-----------|------|-------|
| | | |
| | | |
| | | |

### Connected Resources

| Resource | Type | Connection name |
|----------|------|-----------------|
| | | |
| | | |

---

## 5. Workflow Configuration

| Setting | Value |
|---------|-------|
| Workflow name | safe-agents |
| Current version | |
| Pattern | Sequential + branching |

### Variables

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `Local.LatestMessage` | Table | — | Passes agent output between nodes |
| `Local.TurnCount` | Number | 0 | Tracks Reviewer passes |
| `Local.ReviewerResponse` | String | — | Extracted Reviewer text for condition |

### Workflow YAML
Saved locally → `definition/workflow-final.yaml`

### Visual Builder Screenshot
- [ ] Save screenshot of node layout to this folder

---

## 6. File Uploads / Vector Stores

| File Name | File ID | Attached To | Vector Store ID |
|-----------|---------|-------------|-----------------|
| Interview Transcript v-1 (.docx) | `assistant-ATNKSAHsDBfTr2FyJ357Cp` | Supervisor, Preparer | |
| framework-v2.md | | Preparer, Formatter | |

---

## 7. Tracing

| Setting | Value |
|---------|-------|
| Tracing enabled | Yes (enabled Session 2) |
| Application Insights connection | |
| Instrumentation key | |

---

## Already Saved Locally (No Action Needed)

| Item | Location |
|------|----------|
| Workflow YAML | `definition/workflow-final.yaml` |
| All 4 agent prompts | `definition/agents/` |
| JSON output schema | `definition/schemas/output-schema-v2.json` |
| Framework document | `definition/framework-v2.md` |
| Workflow specification | `definition/workflow-specification.md` |
| Platform reference (guardrail docs) | `platform/foundry-reference.md` |
| Build session logs | `documentation/` |
| Test transcript | `test-transcript.md` |
| Test run outputs | `../test-runs/establishment-tests/` |
| Python SDK script (stub) | `src/workflow.py` |

---

## Notes

- GPT-5.4 deployment has a network error as of 2026-05-05 — capture its config anyway
- Claude 4.6 has no integrated guardrail configuration in Foundry portal — severity cannot be tuned
- File ID `assistant-ATNKSAHsDBfTr2FyJ357Cp` confirmed from trace logs for transcript
- After capturing, we can rebuild the full environment from this file + local files
