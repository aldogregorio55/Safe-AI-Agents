#!/usr/bin/env python3
"""
Registry Calculator v3 — Round 3 run-log → registry derivation tool.

Source of truth: evidence/round-3/run-log.md
Derived view:    evidence/run-registry-v3.md (R3 sections only)

Frozen sections (R1+R2 summary, scoring key, platform config, prompt versions,
pointers, update rules, file status, diff summary, and R1+R2 rows of the
Guardrail & Error Tracking table) are hash-protected. Script aborts and
restores from backup if frozen content would be modified.

Commands:
    add      Append new runs (CLI or batch YAML); recompute registry
    verify   Recompute from run-log; compare to registry; exit 0/1
    status   Print current derived totals; no writes

Global flags:
    --dry-run    Show diff, never write
    --yes        Skip confirmation prompt
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import sys
from dataclasses import dataclass
from datetime import date as Date, datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # only required for --batch


# ============================================================================
# CONSTANTS
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT       = SCRIPT_DIR.parent
REGISTRY   = ROOT / "evidence" / "run-registry-v3.md"
RUN_LOG    = ROOT / "evidence" / "round-3" / "run-log.md"

# Single source of truth for cell metadata. Adding cells requires only this dict.
CELLS: dict[str, dict] = {
    "A1": {"phase": "A", "model": "Claude Sonnet 4.6.1", "cond": "Attack",    "mode": "Sup isolation", "block": "Guardrails", "target": 5,  "mcode": "CL",  "ccode": "AP", "mdcode": "SUP"},
    "A2": {"phase": "A", "model": "Claude Sonnet 4.6.1", "cond": "Attack",    "mode": "Workflow",      "block": "Guardrails", "target": 5,  "mcode": "CL",  "ccode": "AP", "mdcode": "WF"},
    "A3": {"phase": "A", "model": "Claude Sonnet 4.6.1", "cond": "No Attack", "mode": "Sup isolation", "block": "Guardrails", "target": 5,  "mcode": "CL",  "ccode": "FP", "mdcode": "SUP"},
    "A4": {"phase": "A", "model": "Claude Sonnet 4.6.1", "cond": "No Attack", "mode": "Workflow",      "block": "Guardrails", "target": 5,  "mcode": "CL",  "ccode": "FP", "mdcode": "WF"},
    "A5": {"phase": "A", "model": "GPT 5.4",             "cond": "Attack",    "mode": "Sup isolation", "block": "Guardrails", "target": 5,  "mcode": "GPT", "ccode": "AP", "mdcode": "SUP"},
    "A6": {"phase": "A", "model": "GPT 5.4",             "cond": "Attack",    "mode": "Workflow",      "block": "Guardrails", "target": 5,  "mcode": "GPT", "ccode": "AP", "mdcode": "WF"},
    "A7": {"phase": "A", "model": "GPT 5.4",             "cond": "No Attack", "mode": "Sup isolation", "block": "Guardrails", "target": 5,  "mcode": "GPT", "ccode": "FP", "mdcode": "SUP"},
    "A8": {"phase": "A", "model": "GPT 5.4",             "cond": "No Attack", "mode": "Workflow",      "block": "Guardrails", "target": 5,  "mcode": "GPT", "ccode": "FP", "mdcode": "WF"},
    "B1": {"phase": "B", "model": "Claude Sonnet 4.6.1", "cond": "Attack",    "mode": "Sup isolation", "block": "v6",         "target": 50, "mcode": "CL",  "ccode": "AP", "mdcode": "SUP"},
    "B2": {"phase": "B", "model": "Claude Sonnet 4.6.1", "cond": "Attack",    "mode": "Workflow",      "block": "v6",         "target": 50, "mcode": "CL",  "ccode": "AP", "mdcode": "WF"},
    "B3": {"phase": "B", "model": "Claude Sonnet 4.6.1", "cond": "No Attack", "mode": "Sup isolation", "block": "v6",         "target": 50, "mcode": "CL",  "ccode": "FP", "mdcode": "SUP"},
    "B4": {"phase": "B", "model": "Claude Sonnet 4.6.1", "cond": "No Attack", "mode": "Workflow",      "block": "v6",         "target": 50, "mcode": "CL",  "ccode": "FP", "mdcode": "WF"},
    "B5": {"phase": "B", "model": "GPT 5.4",             "cond": "Attack",    "mode": "Sup isolation", "block": "v6",         "target": 50, "mcode": "GPT", "ccode": "AP", "mdcode": "SUP"},
    "B6": {"phase": "B", "model": "GPT 5.4",             "cond": "Attack",    "mode": "Workflow",      "block": "v6",         "target": 50, "mcode": "GPT", "ccode": "AP", "mdcode": "WF"},
    "B7": {"phase": "B", "model": "GPT 5.4",             "cond": "No Attack", "mode": "Sup isolation", "block": "v6",         "target": 50, "mcode": "GPT", "ccode": "FP", "mdcode": "SUP"},
    "B8": {"phase": "B", "model": "GPT 5.4",             "cond": "No Attack", "mode": "Workflow",      "block": "v6",         "target": 50, "mcode": "GPT", "ccode": "FP", "mdcode": "WF"},
}

VALID_OUTCOMES    = {"PASS", "FAIL", "DISRUPTED"}
VALID_BLOCK_MECHS = {"Guardrail", "Content Filter", "Safety Block", "Model Refusal", "None"}
VALID_YN          = {"Y", "N"}

RUN_ID_PHASE_A_RE = re.compile(r"^GR-(CL|GPT)-(AP|FP)-(SUP|WF)-(\d{3})$")
RUN_ID_PHASE_B_RE = re.compile(r"^(CL|GPT)-(AP|FP)-(SUP|WF)-R3-(\d{3})$")
CELL_HEADER_RE    = re.compile(r"^### (A[1-8]|B[1-8]) — ")

# Frozen R1+R2 baselines (verbatim from v2; used to compute cumulative totals).
# These mirror the rows in the Guardrail table that the script never edits.
FROZEN_R1_CLAUDE = {"completions": 70, "attempts": 87, "flags": 13, "errors": 4}
FROZEN_R1_GPT    = {"completions": 4,  "attempts": 4,  "flags": 0,  "errors": 0}
FROZEN_R2_CLAUDE = {"completions": 20, "attempts": 26, "flags": 5,  "errors": 1}
FROZEN_R2_GPT    = {"completions": 40, "attempts": 53, "flags": 8,  "errors": 5}
FROZEN_TOTAL = {"completions": 134, "attempts": 170, "flags": 26, "errors": 10}
FROZEN_TOTAL_FAILURES = 26 + 10  # 36

PROJECT_TARGET_TOTAL = 574  # R1 + R2 active (134) + R3 (440)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RunRecord:
    run_id: str
    cell: str
    date: str
    model: str
    attempt: int
    complete: str          # "Y" / "N"
    outcome: str           # PASS / FAIL / DISRUPTED, or "" if complete=N
    block_mechanism: str   # Phase A only; "" for Phase B
    flag: str              # "Y" / "N"
    err: str               # "Y" / "N"
    notes: str
    file: str

    def to_log_row(self) -> str:
        """Format row for run-log: 10 cols for Phase A, 9 cols for Phase B."""
        phase = CELLS[self.cell]["phase"]
        if phase == "A":
            # Phase A: Run ID | Date | Attempt | Complete | Outcome | Block Mechanism | Flag | Err | Notes | File
            return (f"| {self.run_id} | {self.date} | {self.attempt} | {self.complete} "
                    f"| {self.outcome} | {self.block_mechanism} | {self.flag} | {self.err} "
                    f"| {self.notes} | {self.file} |")
        else:
            # Phase B: Run ID | Date | Attempt | Complete | Outcome | Flag | Err | Notes | File
            return (f"| {self.run_id} | {self.date} | {self.attempt} | {self.complete} "
                    f"| {self.outcome} | {self.flag} | {self.err} "
                    f"| {self.notes} | {self.file} |")


@dataclass
class CellTotals:
    completed: int = 0
    pass_count: int = 0
    fail_count: int = 0
    disrupted: int = 0
    attempts: int = 0
    flags: int = 0
    network_errs: int = 0

    @property
    def errors(self) -> int:
        return self.flags + self.network_errs

    def pass_rate_str(self) -> str:
        if self.completed == 0:
            return "—"
        pct = round(100 * self.pass_count / self.completed)
        return f"{self.pass_count}/{self.completed} ({pct}%)"

    def add(self, other: "CellTotals") -> "CellTotals":
        return CellTotals(
            completed=self.completed + other.completed,
            pass_count=self.pass_count + other.pass_count,
            fail_count=self.fail_count + other.fail_count,
            disrupted=self.disrupted + other.disrupted,
            attempts=self.attempts + other.attempts,
            flags=self.flags + other.flags,
            network_errs=self.network_errs + other.network_errs,
        )


# ============================================================================
# RUN-LOG PARSING
# ============================================================================

PLACEHOLDER_RE = re.compile(r"^\|\s*\*\(")  # rows like "| *(no runs yet — ...)* |"
TABLE_ROW_RE   = re.compile(r"^\|.*\|\s*$")
TABLE_SEP_RE   = re.compile(r"^\|[\s\-:|]+\|\s*$")


def load_run_log() -> tuple[list[RunRecord], list[str]]:
    """Read RUN_LOG, return (run records, full file lines).
    
    Run-log format:
    - Phase A tables: 10 columns (Run ID | Date | Attempt | Complete | Outcome | Block Mechanism | Flag | Err | Notes | File)
    - Phase B tables: 9 columns  (Run ID | Date | Attempt | Complete | Outcome | Flag | Err | Notes | File)
    - Cell and Model are inferred from section headers like '### A1 — Claude Sonnet 4.6.1 · ...'
    """
    if not RUN_LOG.exists():
        die(f"Run log not found: {RUN_LOG}")
    lines = RUN_LOG.read_text(encoding="utf-8").splitlines()
    records: list[RunRecord] = []
    current_phase: Optional[str] = None
    current_cell: Optional[str] = None
    in_table = False

    for line in lines:
        if line.startswith("## Phase A"):
            current_phase = "A"; current_cell = None; in_table = False; continue
        if line.startswith("## Phase B"):
            current_phase = "B"; current_cell = None; in_table = False; continue
        if line.startswith("## ") and current_phase:
            current_phase = None; current_cell = None; in_table = False; continue
        
        # Detect cell headers like "### A1 — Claude Sonnet 4.6.1 · Attack (DPI-002) · Supervisor isolation · Guardrails"
        cell_match = CELL_HEADER_RE.match(line)
        if cell_match:
            current_cell = cell_match.group(1)
            in_table = False
            continue
        
        if current_phase is None or current_cell is None:
            continue
        if TABLE_SEP_RE.match(line):
            in_table = True; continue
        if not in_table:
            continue
        if not TABLE_ROW_RE.match(line):
            in_table = False; continue
        if PLACEHOLDER_RE.match(line):
            continue
        
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        
        try:
            if current_phase == "A":
                # Phase A: 10 columns with Block Mechanism
                if len(cols) != 10:
                    die(f"Phase A row expected 10 cells, got {len(cols)}:\n  {line}")
                rec = RunRecord(
                    run_id=cols[0],
                    cell=current_cell,
                    date=cols[1],
                    model=CELLS[current_cell]["model"],
                    attempt=int(cols[2]) if cols[2] else 1,
                    complete=cols[3],
                    outcome=cols[4],
                    block_mechanism=cols[5],
                    flag=cols[6],
                    err=cols[7],
                    notes=cols[8],
                    file=cols[9],
                )
            else:
                # Phase B: 9 columns without Block Mechanism
                if len(cols) != 9:
                    die(f"Phase B row expected 9 cells, got {len(cols)}:\n  {line}")
                rec = RunRecord(
                    run_id=cols[0],
                    cell=current_cell,
                    date=cols[1],
                    model=CELLS[current_cell]["model"],
                    attempt=int(cols[2]) if cols[2] else 1,
                    complete=cols[3],
                    outcome=cols[4],
                    block_mechanism="",  # Phase B has no block mechanism column
                    flag=cols[5],
                    err=cols[6],
                    notes=cols[7],
                    file=cols[8],
                )
        except (ValueError, KeyError) as e:
            die(f"Error parsing run-log row: {line}\n  {e}")
        records.append(rec)
    return records, lines


# ============================================================================
# AGGREGATION
# ============================================================================

def aggregate(records: list[RunRecord]) -> dict[str, CellTotals]:
    totals = {cid: CellTotals() for cid in CELLS}
    for r in records:
        if r.cell not in totals:
            continue
        t = totals[r.cell]
        # Each row in the run-log represents exactly one attempt (discarded
        # runs and reruns are separate rows). Do not use r.attempt here — it's
        # a sequence counter, not an attempt count for that row.
        t.attempts += 1
        if r.flag == "Y":
            t.flags += 1
        if r.err == "Y":
            t.network_errs += 1
        if r.complete == "Y":
            t.completed += 1
            if r.outcome == "PASS":
                t.pass_count += 1
            elif r.outcome == "FAIL":
                t.fail_count += 1
            elif r.outcome == "DISRUPTED":
                t.disrupted += 1
    return totals


def phase_sum(totals: dict[str, CellTotals], phase: str) -> CellTotals:
    out = CellTotals()
    for cid, t in totals.items():
        if CELLS[cid]["phase"] == phase:
            out = out.add(t)
    return out


def model_sum(totals: dict[str, CellTotals], model: str) -> CellTotals:
    out = CellTotals()
    for cid, t in totals.items():
        if CELLS[cid]["model"] == model:
            out = out.add(t)
    return out


def status_for(cell: str, t: CellTotals) -> str:
    target = CELLS[cell]["target"]
    if t.completed == 0:
        return "Pending"
    if t.completed >= target:
        return "Complete"
    return "In Progress"


# ============================================================================
# VALIDATION
# ============================================================================

def validate_run(r: RunRecord, existing_ids: set[str]) -> list[str]:
    errs: list[str] = []
    if r.cell not in CELLS:
        errs.append(f"Unknown cell '{r.cell}' (valid: {', '.join(CELLS)})")
        return errs
    meta = CELLS[r.cell]

    if meta["phase"] == "A":
        m = RUN_ID_PHASE_A_RE.match(r.run_id)
        if not m:
            errs.append(f"Run ID '{r.run_id}' does not match Phase A pattern "
                        f"GR-<CL|GPT>-<AP|FP>-<SUP|WF>-NNN")
        elif (m.group(1) != meta["mcode"] or m.group(2) != meta["ccode"]
              or m.group(3) != meta["mdcode"]):
            errs.append(f"Run ID '{r.run_id}' codes do not match cell {r.cell} "
                        f"(expected GR-{meta['mcode']}-{meta['ccode']}-{meta['mdcode']}-NNN)")
    else:
        m = RUN_ID_PHASE_B_RE.match(r.run_id)
        if not m:
            errs.append(f"Run ID '{r.run_id}' does not match Phase B pattern "
                        f"<CL|GPT>-<AP|FP>-<SUP|WF>-R3-NNN")
        elif (m.group(1) != meta["mcode"] or m.group(2) != meta["ccode"]
              or m.group(3) != meta["mdcode"]):
            errs.append(f"Run ID '{r.run_id}' codes do not match cell {r.cell} "
                        f"(expected {meta['mcode']}-{meta['ccode']}-{meta['mdcode']}-R3-NNN)")

    if r.run_id in existing_ids:
        errs.append(f"Run ID '{r.run_id}' already exists")

    if r.model != meta["model"]:
        errs.append(f"Model '{r.model}' does not match cell {r.cell} model '{meta['model']}'")

    if meta["phase"] == "A":
        if r.block_mechanism not in VALID_BLOCK_MECHS:
            errs.append(f"Phase A cell {r.cell} requires --block-mechanism in "
                        f"{sorted(VALID_BLOCK_MECHS)}")
    else:
        if r.block_mechanism:
            errs.append(f"Phase B cell {r.cell} must not have --block-mechanism "
                        f"(got '{r.block_mechanism}')")

    if r.complete not in VALID_YN:
        errs.append(f"complete must be Y or N (got '{r.complete}')")
    if r.flag not in VALID_YN:
        errs.append(f"flag must be Y or N (got '{r.flag}')")
    if r.err not in VALID_YN:
        errs.append(f"err must be Y or N (got '{r.err}')")

    if r.complete == "Y":
        if r.outcome not in VALID_OUTCOMES:
            errs.append(f"complete=Y requires outcome in {sorted(VALID_OUTCOMES)} "
                        f"(got '{r.outcome}')")
    else:
        if r.outcome:
            errs.append(f"complete=N requires empty outcome (got '{r.outcome}')")

    if r.attempt < 1:
        errs.append(f"attempt must be >= 1 (got {r.attempt})")

    try:
        datetime.strptime(r.date, "%Y-%m-%d")
    except ValueError:
        errs.append(f"date '{r.date}' is not YYYY-MM-DD")

    return errs


def validate_capacity(new_records: list[RunRecord],
                      existing_totals: dict[str, CellTotals]) -> list[str]:
    errs: list[str] = []
    new_completed: dict[str, int] = {c: 0 for c in CELLS}
    for r in new_records:
        if r.cell in new_completed and r.complete == "Y":
            new_completed[r.cell] += 1
    for cid, add in new_completed.items():
        if add == 0:
            continue
        future = existing_totals[cid].completed + add
        if future > CELLS[cid]["target"]:
            errs.append(f"Cell {cid} capacity exceeded: "
                        f"{existing_totals[cid].completed} + {add} = {future} "
                        f"(target {CELLS[cid]['target']})")
    return errs


# ============================================================================
# INPUT PARSING (CLI + YAML)
# ============================================================================

def build_cli_run(args: argparse.Namespace) -> RunRecord:
    if not args.cell or args.cell not in CELLS:
        die(f"--cell required and must be one of {', '.join(CELLS)}")
    meta = CELLS[args.cell]
    return RunRecord(
        run_id=args.run_id or "",
        cell=args.cell,
        date=args.date or "",
        model=meta["model"],
        attempt=args.attempt or 1,
        complete="N" if args.incomplete else "Y",
        outcome="" if args.incomplete else (args.outcome or ""),
        block_mechanism=args.block_mechanism or "",
        flag="Y" if args.flag else "N",
        err="Y" if args.err else "N",
        notes=args.notes or "",
        file=args.file or "",
    )


def parse_batch_yaml(path: Path) -> list[RunRecord]:
    if yaml is None:
        die("PyYAML not installed. Run: pip install pyyaml")
    if not path.exists():
        die(f"Batch file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "runs" not in data:
        die("Batch YAML must be a mapping with a top-level 'runs' list")
    default_date = data.get("date", "")
    out: list[RunRecord] = []
    for i, raw in enumerate(data["runs"], 1):
        if not isinstance(raw, dict):
            die(f"Batch run #{i} is not a mapping")
        cell = raw.get("cell")
        if cell not in CELLS:
            die(f"Batch run #{i}: unknown or missing cell '{cell}'")
        meta = CELLS[cell]
        complete = str(raw.get("complete", "Y")).upper()
        out.append(RunRecord(
            run_id=str(raw.get("run_id", "")),
            cell=cell,
            date=str(raw.get("date", default_date)),
            model=meta["model"],
            attempt=int(raw.get("attempt", 1)),
            complete=complete,
            outcome=str(raw.get("outcome", "")) if complete == "Y" else "",
            block_mechanism=str(raw.get("block_mechanism", "")),
            flag="Y" if str(raw.get("flag", "N")).upper() == "Y" else "N",
            err="Y" if str(raw.get("err", "N")).upper() == "Y" else "N",
            notes=str(raw.get("notes", "")),
            file=str(raw.get("file", "")),
        ))
    return out


# ============================================================================
# REGISTRY RENDERING
# ============================================================================

def render_status_snapshot_rows(totals: dict[str, CellTotals]) -> list[str]:
    rows: list[str] = []
    for cid in list(CELLS):
        m = CELLS[cid]; t = totals[cid]
        rows.append(
            f"| {cid} | {m['model']} | {m['cond']} | {m['mode']} | {m['block']} "
            f"| {m['target']} | {t.completed} | {t.pass_count} | {t.fail_count} "
            f"| {t.errors} | {t.pass_rate_str()} | {status_for(cid, t)} |"
        )
    pa = phase_sum(totals, "A"); pb = phase_sum(totals, "B")
    tot = pa.add(pb)
    rows.append(
        f"| **Phase A subtotal** | | | | | **40** | **{pa.completed}** "
        f"| **{pa.pass_count}** | **{pa.fail_count}** | **{pa.errors}** | — | |"
    )
    rows.append(
        f"| **Phase B subtotal** | | | | | **400** | **{pb.completed}** "
        f"| **{pb.pass_count}** | **{pb.fail_count}** | **{pb.errors}** | — | |"
    )
    rows.append(
        f"| **Round 3 TOTAL** | | | | | **440** | **{tot.completed}** "
        f"| **{tot.pass_count}** | **{tot.fail_count}** | **{tot.errors}** | — | |"
    )
    return rows


def render_r3_guardrail_rows(totals: dict[str, CellTotals]) -> list[str]:
    """R3 region between '*— Round 3 (live) —*' and '*— Project cumulative —*'."""
    rows: list[str] = ["| *— Round 3 (live) —* | | | | | | |"]
    for cid in list(CELLS):
        t = totals[cid]
        rows.append(
            f"| R3 | {cid} | {CELLS[cid]['model']} | {t.completed} "
            f"| {t.attempts} | {t.flags} | {t.network_errs} |"
        )
    r3_cl = model_sum(totals, "Claude Sonnet 4.6.1")
    r3_gpt = model_sum(totals, "GPT 5.4")
    r3_tot = r3_cl.add(r3_gpt)
    rows.append(
        f"| **R3 subtotal — Claude** | | **Claude Sonnet 4.6.1** "
        f"| **{r3_cl.completed}** | **{r3_cl.attempts}** | **{r3_cl.flags}** | **{r3_cl.network_errs}** |"
    )
    rows.append(
        f"| **R3 subtotal — GPT** | | **GPT 5.4** "
        f"| **{r3_gpt.completed}** | **{r3_gpt.attempts}** | **{r3_gpt.flags}** | **{r3_gpt.network_errs}** |"
    )
    rows.append(
        f"| **R3 TOTAL** | | "
        f"| **{r3_tot.completed}** | **{r3_tot.attempts}** | **{r3_tot.flags}** | **{r3_tot.network_errs}** |"
    )
    return rows


def render_cumulative_rows(totals: dict[str, CellTotals]) -> list[str]:
    r3_cl = model_sum(totals, "Claude Sonnet 4.6.1")
    r3_gpt = model_sum(totals, "GPT 5.4")
    cl_comp = FROZEN_R1_CLAUDE["completions"] + FROZEN_R2_CLAUDE["completions"] + r3_cl.completed
    cl_att  = FROZEN_R1_CLAUDE["attempts"]    + FROZEN_R2_CLAUDE["attempts"]    + r3_cl.attempts
    cl_flg  = FROZEN_R1_CLAUDE["flags"]       + FROZEN_R2_CLAUDE["flags"]       + r3_cl.flags
    cl_err  = FROZEN_R1_CLAUDE["errors"]      + FROZEN_R2_CLAUDE["errors"]      + r3_cl.network_errs
    gp_comp = FROZEN_R1_GPT["completions"]    + FROZEN_R2_GPT["completions"]    + r3_gpt.completed
    gp_att  = FROZEN_R1_GPT["attempts"]       + FROZEN_R2_GPT["attempts"]       + r3_gpt.attempts
    gp_flg  = FROZEN_R1_GPT["flags"]          + FROZEN_R2_GPT["flags"]          + r3_gpt.flags
    gp_err  = FROZEN_R1_GPT["errors"]         + FROZEN_R2_GPT["errors"]         + r3_gpt.network_errs
    tot_comp = cl_comp + gp_comp
    tot_att  = cl_att  + gp_att
    tot_flg  = cl_flg  + gp_flg
    tot_err  = cl_err  + gp_err
    return [
        "| *— Project cumulative —* | | | | | | |",
        f"| **CUMULATIVE — Claude** | | | **{cl_comp}** | **{cl_att}** | **{cl_flg}** | **{cl_err}** |",
        f"| **CUMULATIVE — GPT** | | | **{gp_comp}** | **{gp_att}** | **{gp_flg}** | **{gp_err}** |",
        f"| **PROJECT CUMULATIVE** | | | **{tot_comp}** | **{tot_att}** | **{tot_flg}** | **{tot_err}** |",
    ]


def render_error_rate_bullets(totals: dict[str, CellTotals]) -> list[str]:
    tot = phase_sum(totals, "A").add(phase_sum(totals, "B"))
    r3_failures = tot.flags + tot.network_errs
    r3_attempts = tot.attempts
    if r3_attempts == 0:
        r3_line = "- Round 3: TBD (computed once Attempts > 0)"
    else:
        pct = round(100 * r3_failures / r3_attempts, 1)
        r3_line = (f"- Round 3: {pct}% ({r3_failures} failures in {r3_attempts} attempts "
                   f"— {tot.flags} guardrail + {tot.network_errs} network)")
    cum_failures = FROZEN_TOTAL_FAILURES + r3_failures
    cum_attempts = FROZEN_TOTAL["attempts"] + r3_attempts
    cum_pct = round(100 * cum_failures / cum_attempts, 1) if cum_attempts else 0.0
    cum_flags = FROZEN_TOTAL["flags"] + tot.flags
    cum_errs  = FROZEN_TOTAL["errors"] + tot.network_errs
    cum_line = (f"- **Project cumulative:** {cum_pct}% ({cum_failures} failures "
                f"in {cum_attempts} attempts — {cum_flags} guardrail + {cum_errs} network)")
    return [
        "- Round 1: 18.7% (17 failures in 91 attempts)",
        "- Round 2: 24.1% (19 failures in 79 attempts)",
        r3_line,
        cum_line,
    ]


def render_header_lines(totals: dict[str, CellTotals]) -> dict[str, str]:
    pa = phase_sum(totals, "A").completed
    pb = phase_sum(totals, "B").completed
    r3 = pa + pb
    cumul = FROZEN_TOTAL["completions"] + r3
    today = Date.today().isoformat()
    return {
        "**Last updated:**": f"**Last updated:** {today}",
        "**Round 3 progress:**": f"**Round 3 progress:** Phase A {pa}/40 | Phase B {pb}/400 | Round 3 {r3}/440",
        "**Project cumulative:**": (
            f"**Project cumulative:** 134 (R1+R2 frozen) + {r3} (R3) = {cumul} / {PROJECT_TARGET_TOTAL} planned"
        ),
    }


# ============================================================================
# REGISTRY WRITE (line-range replacement)
# ============================================================================

def find_line(lines: list[str], predicate) -> int:
    for i, ln in enumerate(lines):
        if predicate(ln):
            return i
    return -1


def replace_registry_regions(text: str, totals: dict[str, CellTotals]) -> str:
    lines = text.splitlines()

    # 1. Header lines (prefix match — single-line replacements)
    header_updates = render_header_lines(totals)
    for prefix, new_line in header_updates.items():
        idx = find_line(lines, lambda ln, p=prefix: ln.startswith(p))
        if idx < 0:
            die(f"Could not find header line starting with: {prefix}")
        lines[idx] = new_line

    # 2. Status Snapshot table
    snap_h = find_line(lines, lambda ln: ln.strip() == "## Round 3 Status Snapshot")
    if snap_h < 0:
        die("Could not find '## Round 3 Status Snapshot' heading")
    snap_end = next((i for i in range(snap_h + 1, len(lines)) if lines[i].strip() == "---"), -1)
    if snap_end < 0:
        die("Could not find end of Status Snapshot section")
    first_data = next((i for i in range(snap_h, snap_end)
                       if re.match(r"^\|\s*A1\s*\|", lines[i])), -1)
    last_data = next((i for i in range(snap_h, snap_end)
                      if lines[i].startswith("| **Round 3 TOTAL**")), -1)
    if first_data < 0 or last_data < 0:
        die("Could not locate Status Snapshot data rows")
    new_snap_rows = render_status_snapshot_rows(totals)
    lines[first_data:last_data + 1] = new_snap_rows

    # 3. Guardrail table — R3 region + cumulative region
    grd_h = find_line(lines, lambda ln: ln.strip().startswith("## Guardrail & Error Tracking"))
    if grd_h < 0:
        die("Could not find Guardrail & Error Tracking heading")
    grd_end = next((i for i in range(grd_h + 1, len(lines)) if lines[i].strip() == "---"), -1)
    if grd_end < 0:
        die("Could not find end of Guardrail section")
    r3_marker = next((i for i in range(grd_h, grd_end)
                      if "*— Round 3 (live) —*" in lines[i]), -1)
    cum_marker = next((i for i in range(grd_h, grd_end)
                       if "*— Project cumulative —*" in lines[i]), -1)
    if r3_marker < 0 or cum_marker < 0:
        die("Could not find R3 / cumulative markers in Guardrail table")
    last_cum = cum_marker
    for i in range(cum_marker + 1, grd_end):
        if TABLE_ROW_RE.match(lines[i]):
            last_cum = i
        else:
            break
    new_r3 = render_r3_guardrail_rows(totals)
    new_cum = render_cumulative_rows(totals)
    lines[r3_marker:last_cum + 1] = new_r3 + new_cum

    # 4. Error rates bullet list
    er_h = find_line(lines, lambda ln: ln.strip() == "**Error rates:**")
    if er_h < 0:
        die("Could not find '**Error rates:**' marker")
    bullet_start = er_h + 1
    bullet_end = bullet_start
    while bullet_end < len(lines) and lines[bullet_end].lstrip().startswith("- "):
        bullet_end += 1
    if bullet_end - bullet_start != 4:
        die(f"Expected 4 error-rate bullets, found {bullet_end - bullet_start}")
    lines[bullet_start:bullet_end] = render_error_rate_bullets(totals)

    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


# ============================================================================
# RUN-LOG WRITE (append into per-cell tables)
# ============================================================================

def insert_runs_into_log(log_lines: list[str], new_runs: list[RunRecord]) -> str:
    """Insert new runs into their respective cell tables in the run-log.
    
    Each cell (A1–A8, B1–B8) has its own table section starting with a header
    like '### A1 — Claude Sonnet 4.6.1 · Attack (DPI-002) · ...'.
    Runs are inserted after the last existing data row, or replace the placeholder
    row if the table is empty.
    """
    out = list(log_lines)
    
    # Group runs by cell
    runs_by_cell: dict[str, list[RunRecord]] = {}
    for r in new_runs:
        runs_by_cell.setdefault(r.cell, []).append(r)
    
    # Process cells in reverse order (B8 → A1) so earlier insertions don't shift later indices
    for cell_id in reversed(list(CELLS.keys())):
        if cell_id not in runs_by_cell:
            continue
        cell_runs = runs_by_cell[cell_id]
        
        # Find the cell's section header (e.g., "### A1 — Claude Sonnet 4.6.1 · ...")
        cell_header_idx = find_line(out, lambda ln, c=cell_id: CELL_HEADER_RE.match(ln) and ln.startswith(f"### {c} "))
        if cell_header_idx < 0:
            die(f"Cell {cell_id} header not found in run-log")
        
        # Find the table separator (|---|---| line) after the cell header
        sep_idx = -1
        for i in range(cell_header_idx + 1, min(cell_header_idx + 20, len(out))):
            if TABLE_SEP_RE.match(out[i]):
                sep_idx = i
                break
        if sep_idx < 0:
            die(f"Table separator not found for cell {cell_id}")
        
        # Scan rows after separator to find last data row or placeholder
        i = sep_idx + 1
        last_data_idx = -1
        placeholder_idx = -1
        while i < len(out) and TABLE_ROW_RE.match(out[i]):
            if PLACEHOLDER_RE.match(out[i]):
                placeholder_idx = i
            else:
                last_data_idx = i
            i += 1
        
        # Generate new row strings
        new_rows = [r.to_log_row() for r in cell_runs]
        
        # Insert: after last data row, or replace placeholder, or after separator
        if last_data_idx >= 0:
            out[last_data_idx + 1:last_data_idx + 1] = new_rows
        elif placeholder_idx >= 0:
            out[placeholder_idx:placeholder_idx + 1] = new_rows
        else:
            out[sep_idx + 1:sep_idx + 1] = new_rows
    
    return "\n".join(out) + "\n"


# ============================================================================
# FROZEN HASH PROTECTION
# ============================================================================

def strip_editable_regions(text: str) -> str:
    """Replace editable spans with stable placeholders so frozen content can
    be hashed regardless of edits."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if (ln.startswith("**Last updated:**") or
                ln.startswith("**Round 3 progress:**") or
                ln.startswith("**Project cumulative:**")):
            out.append("<<EDITABLE_HEADER>>"); i += 1; continue
        if ln.strip() == "## Round 3 Status Snapshot":
            out.append(ln); i += 1
            out.append("<<EDITABLE_STATUS_SNAPSHOT>>")
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            continue
        if ln.strip().startswith("## Guardrail & Error Tracking"):
            out.append(ln); i += 1
            while i < len(lines) and "*— Round 3 (live) —*" not in lines[i]:
                if lines[i].strip() == "---":
                    break
                out.append(lines[i])
                i += 1
            out.append("<<EDITABLE_R3_GUARDRAIL_AND_CUMULATIVE>>")
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            continue
        if ln.strip() == "**Error rates:**":
            out.append(ln); i += 1
            out.append("<<EDITABLE_ERROR_RATES>>")
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                i += 1
            continue
        out.append(ln); i += 1
    return "\n".join(out)


def frozen_hash(text: str) -> str:
    return hashlib.sha256(strip_editable_regions(text).encode("utf-8")).hexdigest()


# ============================================================================
# DIFF + CONFIRM + WRITE
# ============================================================================

def unified_diff(old: str, new: str, label: str) -> str:
    return "".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"{label} (current)", tofile=f"{label} (proposed)", n=2,
    ))


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    try:
        ans = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans == "y"


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    tmp.replace(path)


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

def cmd_add(args: argparse.Namespace) -> int:
    existing, log_lines = load_run_log()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    pre_hash = frozen_hash(registry_text)

    if args.batch:
        new_runs = parse_batch_yaml(Path(args.batch))
    else:
        new_runs = [build_cli_run(args)]
    if not new_runs:
        die("No runs to add")

    existing_ids = {r.run_id for r in existing}
    all_errs: list[str] = []
    for r in new_runs:
        errs = validate_run(r, existing_ids)
        if errs:
            all_errs.append(f"[{r.run_id or '<no id>'}] " + "; ".join(errs))
        existing_ids.add(r.run_id)
    cap_errs = validate_capacity(new_runs, aggregate(existing))
    all_errs.extend(cap_errs)
    if all_errs:
        print("Validation failed:", file=sys.stderr)
        for e in all_errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    combined_totals = aggregate(existing + new_runs)
    proposed_log = insert_runs_into_log(log_lines, new_runs)
    proposed_reg = replace_registry_regions(registry_text, combined_totals)
    post_hash = frozen_hash(proposed_reg)
    if pre_hash != post_hash:
        print("ABORT: proposed registry would modify frozen content.", file=sys.stderr)
        print(f"  pre-hash:  {pre_hash}", file=sys.stderr)
        print(f"  post-hash: {post_hash}", file=sys.stderr)
        return 2

    cur_log = "\n".join(log_lines) + "\n"
    print(unified_diff(cur_log, proposed_log, "run-log.md"))
    print(unified_diff(registry_text, proposed_reg, "run-registry-v3.md"))
    print(f"\nNew runs to add: {len(new_runs)}")
    for r in new_runs:
        outcome = r.outcome if r.complete == "Y" else "INCOMPLETE"
        print(f"  + {r.run_id} ({r.cell}) -> {outcome}")

    if args.dry_run:
        print("\n--dry-run set; no changes written.")
        return 0
    if not confirm("\nApply changes?", args.yes):
        print("Aborted; no changes written.")
        return 0
    atomic_write(REGISTRY, proposed_reg)
    atomic_write(RUN_LOG, proposed_log)
    final_hash = frozen_hash(REGISTRY.read_text(encoding="utf-8"))
    if final_hash != pre_hash:
        print("CRITICAL: post-write frozen-hash mismatch. Manual review required.",
              file=sys.stderr)
        return 3
    print(f"Wrote {len(new_runs)} run(s). Frozen content verified unchanged.")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    existing, _ = load_run_log()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    totals = aggregate(existing)
    proposed = replace_registry_regions(registry_text, totals)
    # Header "Last updated" will always differ if rerun on a different day —
    # normalize that line out of the comparison so verify is meaningful.
    def strip_last_updated(t: str) -> str:
        return re.sub(r"^\*\*Last updated:\*\*.*$", "<<LAST_UPDATED>>", t, flags=re.M)
    if strip_last_updated(proposed) == strip_last_updated(registry_text):
        print("OK: registry matches run-log totals.")
        return 0
    print("MISMATCH: registry does not match run-log totals.", file=sys.stderr)
    print(unified_diff(registry_text, proposed, "run-registry-v3.md"))
    return 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync registry from run-log totals (no new runs added)."""
    existing, _ = load_run_log()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    pre_hash = frozen_hash(registry_text)
    
    totals = aggregate(existing)
    proposed_reg = replace_registry_regions(registry_text, totals)
    post_hash = frozen_hash(proposed_reg)
    
    if pre_hash != post_hash:
        print("ABORT: proposed registry would modify frozen content.", file=sys.stderr)
        print(f"  pre-hash:  {pre_hash}", file=sys.stderr)
        print(f"  post-hash: {post_hash}", file=sys.stderr)
        return 2
    
    # Check if any changes needed
    def strip_last_updated(t: str) -> str:
        return re.sub(r"^\*\*Last updated:\*\*.*$", "<<LAST_UPDATED>>", t, flags=re.M)
    if strip_last_updated(proposed_reg) == strip_last_updated(registry_text):
        print("Registry already in sync with run-log.")
        return 0
    
    print(unified_diff(registry_text, proposed_reg, "run-registry-v3.md"))
    print(f"\nRegistry will be updated to reflect {len(existing)} runs from run-log.")
    
    if args.dry_run:
        print("\n--dry-run set; no changes written.")
        return 0
    if not confirm("\nApply changes?", args.yes):
        print("Aborted; no changes written.")
        return 0
    
    atomic_write(REGISTRY, proposed_reg)
    final_hash = frozen_hash(REGISTRY.read_text(encoding="utf-8"))
    if final_hash != pre_hash:
        print("CRITICAL: post-write frozen-hash mismatch. Manual review required.",
              file=sys.stderr)
        return 3
    print("Registry synced. Frozen content verified unchanged.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    existing, _ = load_run_log()
    totals = aggregate(existing)
    print(f"Round 3 status — {len(existing)} runs in log\n")
    print(f"{'Cell':5} {'Phase':5} {'Comp':>5}/{'Tgt':<3} {'PASS':>5} {'FAIL':>5} "
          f"{'Err':>4} {'Status':<20}")
    for cid in CELLS:
        t = totals[cid]; m = CELLS[cid]
        print(f"{cid:5} {m['phase']:5} {t.completed:>5}/{m['target']:<3} "
              f"{t.pass_count:>5} {t.fail_count:>5} {t.errors:>4} "
              f"{status_for(cid, t):<20}")
    pa = phase_sum(totals, "A"); pb = phase_sum(totals, "B")
    print(f"\nPhase A: {pa.completed}/40   Phase B: {pb.completed}/400   "
          f"Round 3: {pa.completed + pb.completed}/440")
    return 0


# ============================================================================
# MAIN
# ============================================================================

def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--dry-run", action="store_true", help="Show diff but never write")
    p.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add new run(s)")
    p_add.add_argument("--batch", help="Path to batch YAML file")
    p_add.add_argument("--run-id")
    p_add.add_argument("--cell", choices=list(CELLS.keys()))
    p_add.add_argument("--date", help="YYYY-MM-DD")
    p_add.add_argument("--attempt", type=int, default=1)
    p_add.add_argument("--outcome", choices=sorted(VALID_OUTCOMES))
    p_add.add_argument("--block-mechanism", choices=sorted(VALID_BLOCK_MECHS))
    p_add.add_argument("--flag", action="store_true", help="Guardrail flag fired")
    p_add.add_argument("--err", action="store_true", help="Network error occurred")
    p_add.add_argument("--incomplete", action="store_true",
                       help="Run did not complete (sets Complete=N, outcome blank)")
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--file", default="")
    p_add.set_defaults(func=cmd_add)

    p_ver = sub.add_parser("verify", help="Recompute and compare to registry")
    p_ver.set_defaults(func=cmd_verify)

    p_sync = sub.add_parser("sync", help="Sync registry from run-log totals")
    p_sync.set_defaults(func=cmd_sync)

    p_stat = sub.add_parser("status", help="Print derived totals")
    p_stat.set_defaults(func=cmd_status)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
