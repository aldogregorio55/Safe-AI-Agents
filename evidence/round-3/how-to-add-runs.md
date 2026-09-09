# How to Add Round 3 Runs

**Tool:** [tools/registry_calculator.py](../../tools/registry_calculator.py)
**Rule:** Use `add`. One command updates both the run-log and the registry. Never edit either file by hand.

---

## Single run

```powershell
python tools\registry_calculator.py add `
  --run-id CL-FP-WF-R3-051 --cell B4 --date 2026-07-02 --outcome PASS `
  --notes "Clean run; trace abc123" `
  --file test-runs/round-3/safety-testing/claude/false-positive/workflow/run051-clean-workflow.md
```

## Batch (recommended for 25+ runs)

Write `batch.yaml`:

```yaml
date: 2026-07-02
runs:
  - { run_id: CL-FP-WF-R3-051, cell: B4, outcome: PASS, notes: "trace abc", file: "test-runs/.../run051-clean-workflow.md" }
  - { run_id: CL-FP-WF-R3-052, cell: B4, outcome: PASS, notes: "trace def", file: "test-runs/.../run052-clean-workflow.md" }
```

Then:

```powershell
python tools\registry_calculator.py add --batch batch.yaml
```

---

## Flags you'll actually use

| Flag | Meaning |
|---|---|
| `--flag` | Guardrail fired |
| `--err` | Network error (creates a row that counts in error totals) |
| `--incomplete` | Complete=N (discarded row, no outcome). For discarded attempts + rerun, log two rows: one with `--incomplete --err`, one for the successful rerun with `--attempt 2` |
| `--block-mechanism Guardrail\|Model Refusal\|None` | **Required for Phase A**, forbidden for Phase B |
| `--dry-run` | Preview only, no writes |
| `--yes` | Skip confirmation prompt |

---

## Rules the tool enforces

1. **Run IDs must match the cell's pattern.** `CL-FP-WF-R3-051` for cell B1 will be rejected. See conventions in [planning/v4/round-3-overview.md § 9](../../planning/v4/round-3-overview.md#9-run-id-conventions).
2. **Cell capacity is enforced.** B4 is at 50/50 — another B4 `add` will be rejected.
3. **Frozen R1+R2 content is hash-protected.** Tool aborts before writing if anything outside R3 regions would change.
4. **Duplicate run IDs are rejected.**

---

## The one exception: `sync`

Only when rows were written to the run-log outside the tool (e.g. by a scaffolder or by hand) and the registry needs to catch up. If you always use `add`, you never need `sync`.

```powershell
python tools\registry_calculator.py sync
```

---

## Read-only checks (safe anytime)

```powershell
python tools\registry_calculator.py status   # per-cell totals to console
python tools\registry_calculator.py verify   # exits 1 if registry drifted from run-log
```

---

## Bottom line

For B5–B8 (GPT cells), write a batch YAML per cell as you go, run `add --batch`, done. Both files stay in sync automatically.
