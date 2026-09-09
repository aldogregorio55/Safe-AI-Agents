# Session Notes — 2026-05-29

**Focus:** Debugging HITL Question node — workflow skipping user approval step  
**Outcome:** Root cause identified and fixed. Workflow operational.

---

## Issue

After a Foundry platform update earlier this week, the `Question` node in the `supervisor_review → Question → Formatter` sequence stopped pausing for user input. The workflow printed the "Is this acceptable?" prompt as part of the Supervisor's response and immediately invoked the Formatter without waiting for user input.

---

## Debugging Steps

| Test | Result |
|------|--------|
| Minimal workflow — Question node only | ✅ Paused as expected |
| Agent + `autoSend: true` + Question node (fresh variable) | ✅ Paused as expected |
| Agent + `output: messages` + Question node with `skipQuestionMode` | ❌ Skipped — variable pre-populated |
| Agent + `output: messages` + Question node without `skipQuestionMode` | ❌ Still skipped |
| Agent + `output: messages` + Question node using fresh variable (`Local.UserApproval`) | ✅ Paused as expected |

---

## Root Cause

The Foundry platform update changed Question node behavior. It now **implicitly skips** whenever the target variable already has a value — regardless of the `skipQuestionMode` setting. Previously, a variable populated by an agent's `output: messages` did not count as "has a value" for this check. After the update it does.

**`skipQuestionMode: SkipOnFirstExecutionIfVariableHasValue` is now effectively the default behavior and cannot be overridden.**

---

## Fix Applied

Changed the Question node to use a fresh variable (`Local.UserApproval`) that is never written to before the node is reached. The Formatter still receives `Local.LatestMessage` (which contains the analysis), so nothing downstream was affected.

**Before:**
```yaml
    - kind: Question
      variable: Local.LatestMessage
      id: node-1777524890260
      entity: StringPrebuiltEntity
      skipQuestionMode: SkipOnFirstExecutionIfVariableHasValue
      prompt: Is this acceptable?
```

**After:**
```yaml
    - kind: Question
      variable: Local.UserApproval
      id: node-1777524890260
      entity: StringPrebuiltEntity
      prompt: Is this acceptable?
```

---

## Additional Finding — TurnCount Clarification

A 3-Reviewer-pass run was observed and initially flagged as a bug. Confirmed correct behavior:

- `TurnCount` starts at `=0`, condition is `>= 2`
- This allows **2 genuine Reviewer feedback cycles** before force-exit
- A run with 3 Reviewer passes = Preparer needed 2 corrections — working as designed

**TurnCount remains at `=0`.**

---

## Files Updated

- `workflow/definition/workflow-final.yaml` — Question node variable changed to `Local.UserApproval`, `skipQuestionMode` removed

