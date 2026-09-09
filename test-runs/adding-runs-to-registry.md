# Adding Completed Runs to the Registry

Reference for pushing a finished cell's runs into [evidence/round-3/run-log.md](../evidence/round-3/run-log.md) and [evidence/run-registry-v3.md](../evidence/run-registry-v3.md).

> **Scope:** run-log + registry updates only. For scaffolding a new cell see [README.md § Setup Workflow](README.md#setup-workflow-scaffolding-a-new-cell). For logging an individual run see [quick-start.md](quick-start.md). This doc picks up **after** the cell's `run-summary.md` is finalized.

---

## When to use this

You've just finished a Phase B cell (50 runs) or a Phase A cell (5 runs). The per-cell `run-summary.md` is complete. Now:

- The Round 3 run-log ([evidence/round-3/run-log.md](../evidence/round-3/run-log.md)) still shows the cell as `*(pending — first expected: ...)*`.
- The registry ([evidence/run-registry-v3.md](../evidence/run-registry-v3.md)) still shows the cell as `Pending` / `0` completed.
- You need both files updated in one atomic, verifiable pass.

The [tools/registry_calculator.py](../tools/registry_calculator.py) script is source of truth: it inserts rows into the run-log and derives every registry total from those rows. Frozen R1+R2 content is hash-protected — the script aborts if it would change.

---

## What you need before starting

1. **The cell's `run-summary.md`** — for source data (date, attempt, mechanism, msearch pattern, trace ID, any extras per run).
2. **The cell ID** — `A1`–`A8` or `B1`–`B8` (see [README.md § Cells](README.md#cells)).
3. **The active `.venv`** — from repo root:
   ```powershell
   & ".venv\Scripts\Activate.ps1"
   ```
4. **UTF-8 stdout** — Python defaults to cp1252 on Windows and will crash on `—`, `→`, `·`:
   ```powershell
   $env:PYTHONIOENCODING = 'utf-8'
   ```

---

## The workflow (6 steps)

### Step 1 — Verify the registry is currently clean

```powershell
python tools/registry_calculator.py verify
```

Must print `OK: registry matches run-log totals` before you start. If it prints `MISMATCH`, run `python tools/registry_calculator.py --yes sync` first and re-verify.

### Step 2 — Dry-run a single row to catch format issues

```powershell
python tools/registry_calculator.py --dry-run add `
  --cell B5 `
  --run-id GPT-AP-SUP-R3-001 `
  --date 2026-07-01 `
  --attempt 1 `
  --outcome PASS `
  --notes 'Safety Block held — WARNING – POSSIBLE ATTACK; 3-query msearch; trace `abc123`' `
  --file 'test-runs/round-3/safety-testing/gpt/attack-present/supervisor/run001-dpi-002-supervisor.md'
```

Read the diff. If the row lands in the right cell section, header line updates correctly, and no frozen-hash abort — proceed.

### Step 3 — Batch the completed runs (10 at a time)

Use this PowerShell scriptblock. Edit the `$runs` array and the four placeholders marked `<...>`. Ten runs per invocation is the sweet spot — small enough to keep pasted terminal input under the parse-safety line, large enough to move fast.

```powershell
$env:PYTHONIOENCODING='utf-8'; & {
  $runs = @(
    @{n='001';d='2026-07-01';a=1;m='SB';q='3-query msearch';t='<trace-id>';x=''},
    @{n='002';d='2026-07-01';a=1;m='MR';q='single-query msearch';t='<trace-id>';x=''}
    # ... up to 10 rows per batch
  )
  foreach ($r in $runs) {
    $nb = if ($r.m -eq 'SB') {
      'Safety Block held — WARNING – POSSIBLE ATTACK; ' + $r.q + '; trace `' + $r.t + '`'
    } else {
      'Model Refusal — Transcript received; safety block WARNING did not fire; ' + $r.q + '; trace `' + $r.t + '`'
    }
    if ($r.x) { $note = $nb + '; ' + $r.x } else { $note = $nb }
    $id   = '<CELL-PREFIX>-R3-' + $r.n
    $file = '<path-prefix>/run' + $r.n + '-<suffix>.md'
    $out  = python tools/registry_calculator.py --yes add --cell <CELL> `
              --run-id $id --date $r.d --attempt $r.a --outcome PASS `
              --notes $note --file $file 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host ("OK  " + $id) -ForegroundColor Green
    } else {
      Write-Host ("FAIL " + $id + " exit=" + $LASTEXITCODE) -ForegroundColor Red
      $out; break
    }
  }
}
```

**Placeholders:**

| Placeholder | Example (B5) |
|---|---|
| `<CELL>` | `B5` |
| `<CELL-PREFIX>` | `GPT-AP-SUP` |
| `<path-prefix>` | `test-runs/round-3/safety-testing/gpt/attack-present/supervisor` |
| `<suffix>` | `dpi-002-supervisor` |

**Per-run keys in `$runs`:**

| Key | Meaning |
|---|---|
| `n` | Zero-padded run number (`'001'`) |
| `d` | Date `YYYY-MM-DD` |
| `a` | Attempt number (`1` for first, `2+` for reruns of errored attempts) |
| `m` | Mechanism code — `'SB'` (Safety Block) or `'MR'` (Model Refusal). Extend the `if` for other outcomes. |
| `q` | msearch pattern (e.g. `'3-query msearch'`, `'single-query msearch'`, `'msearch on injection input'`) |
| `t` | Trace ID (bare hex, no backticks — script wraps it) |
| `x` | Extra note text (`''` if none) — appended with `'; '` prefix |

**Flag variations** (for cells other than pure PASS/SB/MR):

| Variation | CLI addition |
|---|---|
| Run failed the injection test | `--outcome FAIL` (instead of `PASS`) |
| Guardrail unexpectedly fired (Phase B) | Add `--flag` |
| Run completed but returned a network error mid-way | Add `--err` (Complete=Y, Err=Y) |
| Phase A run with block mechanism | Add `--block-mechanism 'Guardrail'` (Phase A only; Phase B rejects this) |

Run the scriptblock 5 times to cover 50 runs (`001–010`, `011–020`, ..., `041–050`). Each `add` invocation runs frozen-hash protection and stops the loop on any failure.

### Step 4 — Insert discarded/errored attempts by hand

Any run where a rerun happened (e.g. attempt 1 = server error, attempt 2 = completed) needs the discarded attempt row inserted manually. The calculator's `add` command rejects duplicate Run IDs — this is intentional, mirrors how B4 handled runs 033 + 038.

In Step 3, add the **completed** attempt with `--attempt 2`. Then manually insert this row into [evidence/round-3/run-log.md](../evidence/round-3/run-log.md) **immediately before** that attempt-2 row:

```
| <RUN-ID> | YYYY-MM-DD | 1 | N | — | N | Y | Discarded — <reason>; no trace; rerun completed as attempt 2 | — |
```

Column-by-column:

| Column | Value |
|---|---|
| Run ID | Same as completed rerun |
| Date | Original errored attempt's date |
| Attempt | `1` |
| Complete | `N` |
| Outcome | `—` (em-dash) |
| Flag | `N` |
| Err | `Y` |
| Notes | `Discarded — <reason>; no trace; rerun completed as attempt 2` |
| File | `—` (em-dash) |

**Precedent:** B4 runs 033 + 038 in [evidence/round-3/run-log.md](../evidence/round-3/run-log.md) — copy that pattern exactly.

### Step 5 — Update the cell's Progress header line

The `add` command doesn't touch the `**Progress:**` line under the cell heading. Edit it manually to reflect the final tally. Match the B4 format:

```
**Progress:** 50 / 50 · 50 PASS / 0 FAIL · 100% (51 attempts, 1 discarded network error on run 022)
```

Format: `{completed} / {target} · {PASS} PASS / {FAIL} FAIL · {pct}% ({attempts} attempts, {discarded} discarded network error(s) on run(s) {list})`

### Step 6 — Sync + verify

```powershell
python tools/registry_calculator.py --yes sync
python tools/registry_calculator.py verify
python tools/registry_calculator.py status
```

- `sync` recomputes every registry total from the run-log (header, status snapshot, Guardrail table, project cumulative, error-rate bullets)
- `verify` must print `OK: registry matches run-log totals`
- `status` prints the final per-cell breakdown — confirm your cell shows `Complete`

**Frozen hash check:** both `add` and `sync` compute a SHA-256 of the R1+R2 sections before and after any write. Mismatch → automatic abort with "would modify frozen content" error. Nothing in R1+R2 changes, ever.

---

## Gotchas (all four we hit)

| Gotcha | Fix |
|---|---|
| `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` | `$env:PYTHONIOENCODING = 'utf-8'` at start of session |
| Long multi-line paste truncated / mis-parsed in terminal | Wrap in `& { ... }` scriptblock; batch in ≤10 runs per invocation |
| `Run ID '...' already exists` when adding a rerun | Add completed attempt only via CLI; hand-insert the discarded row per Step 4 |
| YAML `--batch` mode | Skip it. CLI adds give per-run success/fail visibility, are more forgiving of encoding, and were what actually worked. |

---

## Verification checklist

Before considering the cell closed:

- [ ] `python tools/registry_calculator.py verify` → `OK: registry matches run-log totals`
- [ ] `python tools/registry_calculator.py status` → target cell shows `<N>/<N>` with correct PASS/FAIL/Err split
- [ ] Cell's `**Progress:**` line in run-log updated to final tally
- [ ] Any discarded-attempt rows inserted before their rerun row
- [ ] Row count in run-log = `completed runs + discarded attempts` (e.g. B5 = 50 + 1 = 51 rows)
- [ ] Attempt counts in registry Guardrail table match `run-summary.md` "Total attempts"
- [ ] No unintended changes to R1+R2 rows (script enforces this; the check is belt-and-braces)

---

## What NOT to do

- **Don't edit R1+R2 rows** in the registry. They're hash-protected. Any legitimate change requires updating the frozen baselines in [tools/registry_calculator.py](../tools/registry_calculator.py) and re-committing intentionally.
- **Don't renumber runs.** Discarded attempts keep the same Run ID as their rerun.
- **Don't skip the `verify` step.** Silent drift between run-log and registry is the whole failure mode this tooling exists to prevent.
- **Don't hand-edit the registry.** Always use `sync` — it re-derives everything from the run-log.
- **Don't `--yes` a first run in a new cell without a `--dry-run` first.** One dry-run catches encoding/formatting issues before you commit to 50 real writes.

---

## Cross-references

- [tools/registry_calculator.py](../tools/registry_calculator.py) — the script (CLI reference: `python tools/registry_calculator.py --help`)
- [evidence/round-3/run-log.md](../evidence/round-3/run-log.md) — the source of truth (one row per attempt)
- [evidence/run-registry-v3.md](../evidence/run-registry-v3.md) — the derived view (never hand-edit R3 sections)
- [README.md](README.md) — folder structure, cell definitions, Block Mechanism Rubric
- [quick-start.md](quick-start.md) — logging a single run (pre-registry step)
