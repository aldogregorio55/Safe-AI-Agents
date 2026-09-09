# Foundry Capture

Environment snapshot of the Azure AI Foundry workspace, taken as a precaution ahead of an anticipated May 15 2026 wipe. **Correction: that wipe never occurred — the environment remained live.** Everything needed to document and reconstruct the `safe-agents` workflow is captured here regardless.

## Why This Exists

The AI Agent Safety project runs a 4-agent pain point analysis workflow in Azure AI Foundry (Preview). At the time of capture, the sandbox environment was expected to be wiped on 15 May 2026 (this wipe did not end up happening). This folder preserves the full portal configuration — model deployments, agent settings, guardrails, resource metadata, and workflow state — so the environment can be documented in the final report and rebuilt if needed.

## Capture Checklist

| # | Area | Status | Files |
|---|------|--------|-------|
| 1 | Portal overview (resource, endpoints, IAM) | ✅ Done | `portal-overview.json`, IAM screenshot |
| 2 | Model deployments (GPT-5.4, Claude 4.6) | ✅ Done | screenshot |
| 3 | Agent configurations (Supervisor, Preparer, Reviewer, Formatter) | ✅ Done | `supervisor.md`, `preparer.md`, `reviewer.md`, `formatter.md` |
| 4 | Guardrail configurations (agent-level + deployment-level) | ✅ Done | screenshot |
| 5 | Workflow version & variables | ✅ Done | `workflow.md`, workflow screenshot |
| 6 | File uploads & vector stores | N/A | source files saved in `workflow/definition/` |
| 7 | Tracing (App Insights connection) | N/A | |
| 8 | Visual workflow screenshot | ✅ Done | screenshot |
| 9 | Establishment v2 runs 006–010 (raw outputs) | N/A | already captured in `test-runs/` |

## What's Already Saved Elsewhere

These items are captured in `workflow/definition/` and do not need portal export:

- Agent system prompts → `workflow/definition/agents/`
- Workflow YAML → `workflow/definition/workflow-final.yaml`
- JSON output schema → `workflow/definition/schemas/output-schema-v2.json`
- Pain point framework → `workflow/definition/framework-v2.md`
- Test transcript → `workflow/test-transcript.md`
- All test run outputs → `test-runs/`
- Build session logs → `workflow/documentation/`
- Platform guardrail docs → `workflow/platform/foundry-reference.md`
