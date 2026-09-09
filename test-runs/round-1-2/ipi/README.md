# IPI — Test Outputs

Outputs from indirect prompt injection tests (payload embedded in transcript).

---

## Folder Structure

```
ipi/
  ipi-001/       → IPI-001 (delimiter spoofing) runs
  ipi-002/       → IPI-002 (YAML frontmatter) runs
  ipi-003/       → IPI-003 (markdown comment + ICLR) runs
  ipi-004/       → IPI-004 (few-shot poisoning) runs
```

---

## Naming Convention

**Pattern:** `run{NN}-{payload-id}-{target}-{date}.md`  
Add `-safety` suffix for runs with safety prompt active.

Examples:
- `run01-ipi-001-preparer-2026-05-14.md` — Preparer isolation, no safety
- `run01-ipi-001-workflow-2026-05-14.md` — workflow run, no safety
- `run01-ipi-001-preparer-safety-2026-05-14.md` — Preparer isolation, safety block active

---

## Legacy Files

- `ipi-001-preparer-2026-05-07.md` — v1 overt jailbreak test (pre-v2 payloads, kept for reference)
