"""
Run Registry Calculator — Reusable Tool for Adding Runs

USAGE:
1. Update the NEW_RUNS section below with your new data
2. Run: python registry_calculator.py
3. Review the output for values to update in run-registry-v2.md

The script will:
- Show current state (from BASELINE)
- Calculate new totals after adding your runs
- Verify all math
- Output exactly what values to update in the registry
"""

# ==============================================================================
# CONFIGURATION — UPDATE THIS SECTION WHEN ADDING NEW RUNS
# ==============================================================================

# Current baseline (update this after each registry update to match the file)
BASELINE = {
    # Round 1 (frozen — don't change)
    "round1": {
        "claude_completions": 70,
        "claude_attempts": 87,
        "claude_flags": 13,
        "claude_errors": 4,
        "gpt_completions": 4,
        "gpt_attempts": 4,
        "gpt_flags": 0,
        "gpt_errors": 0,
    },
    # Round 2 (update this to match current registry state)
    "round2": {
        "gpt_establishment": {"completions": 10, "attempts": 21, "flags": 6, "errors": 5},
        "gpt_dpi_baseline_workflow": {"completions": 5, "attempts": 7, "flags": 2, "errors": 0},
        "gpt_dpi_baseline_supervisor": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "claude_attack_present_workflow": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "claude_attack_present_supervisor": {"completions": 5, "attempts": 8, "flags": 3, "errors": 0},
        "gpt_attack_present_workflow": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "gpt_attack_present_supervisor": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "claude_false_positive_workflow": {"completions": 5, "attempts": 8, "flags": 2, "errors": 1},
        "claude_false_positive_supervisor": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "gpt_false_positive_workflow": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
        "gpt_false_positive_supervisor": {"completions": 5, "attempts": 5, "flags": 0, "errors": 0},
    },
    # Archived runs (excluded from active count)
    "archived": 15,  # Establishment v1
    # Last update info
    "last_updated": "2026-06-08",
    "last_session_cumulative_completions": 134,
    "last_session_cumulative_attempts": 170,
}

# NEW RUNS TO ADD — Update this for each new testing session
NEW_RUNS = {
    # Set to True to run calculation, False to just verify current state
    "enabled": False,
    
    # Session info
    "session_date": "2026-06-05",
    "session_focus": "GPT False Positive Workflow",
    
    # Which category to add runs to (must match a key in BASELINE["round2"])
    "category": "gpt_false_positive_workflow",
    
    # New run data
    "completions": 0,  # Number of successful runs
    "attempts": 0,     # Total attempts (including guardrail blocks and errors)
    "flags": 0,        # Guardrail blocks
    "errors": 0,       # Network errors
    
    # Results (for registry update)
    "pass_count": 0,
    "fail_count": 0,
    "result_summary": "TBD",  # e.g., "5/5 PASS (0% FAIL)"
}

# SECOND BATCH — (configure as needed)
NEW_RUNS_2 = {
    "enabled": False,
    "session_date": "2026-06-05",
    "session_focus": "GPT False Positive Supervisor",
    "category": "gpt_false_positive_supervisor",
    "completions": 0,
    "attempts": 0,
    "flags": 0,
    "errors": 0,
    "pass_count": 0,
    "fail_count": 0,
    "result_summary": "TBD",
}

# ==============================================================================
# CALCULATION ENGINE — Don't modify below this line
# ==============================================================================

def calculate_round1_totals(r1):
    """Calculate Round 1 totals."""
    return {
        "completions": r1["claude_completions"] + r1["gpt_completions"],
        "attempts": r1["claude_attempts"] + r1["gpt_attempts"],
        "flags": r1["claude_flags"] + r1["gpt_flags"],
        "errors": r1["claude_errors"] + r1["gpt_errors"],
        "claude_completions": r1["claude_completions"],
        "claude_attempts": r1["claude_attempts"],
        "claude_flags": r1["claude_flags"],
        "claude_errors": r1["claude_errors"],
        "gpt_completions": r1["gpt_completions"],
        "gpt_attempts": r1["gpt_attempts"],
        "gpt_flags": r1["gpt_flags"],
        "gpt_errors": r1["gpt_errors"],
    }

def calculate_round2_totals(r2):
    """Calculate Round 2 totals by model."""
    claude_cats = ["claude_attack_present_workflow", "claude_attack_present_supervisor", 
                    "claude_false_positive_workflow", "claude_false_positive_supervisor"]
    gpt_cats = ["gpt_establishment", "gpt_dpi_baseline_workflow", "gpt_dpi_baseline_supervisor", 
                "gpt_attack_present_workflow", "gpt_attack_present_supervisor", 
                "gpt_false_positive_workflow", "gpt_false_positive_supervisor"]
    
    claude = {"completions": 0, "attempts": 0, "flags": 0, "errors": 0}
    gpt = {"completions": 0, "attempts": 0, "flags": 0, "errors": 0}
    
    for cat in claude_cats:
        for key in ["completions", "attempts", "flags", "errors"]:
            claude[key] += r2[cat][key]
    
    for cat in gpt_cats:
        for key in ["completions", "attempts", "flags", "errors"]:
            gpt[key] += r2[cat][key]
    
    return {
        "claude_completions": claude["completions"],
        "claude_attempts": claude["attempts"],
        "claude_flags": claude["flags"],
        "claude_errors": claude["errors"],
        "gpt_completions": gpt["completions"],
        "gpt_attempts": gpt["attempts"],
        "gpt_flags": gpt["flags"],
        "gpt_errors": gpt["errors"],
        "completions": claude["completions"] + gpt["completions"],
        "attempts": claude["attempts"] + gpt["attempts"],
        "flags": claude["flags"] + gpt["flags"],
        "errors": claude["errors"] + gpt["errors"],
    }

def calculate_cumulative(r1, r2):
    """Calculate cumulative totals."""
    return {
        "claude_completions": r1["claude_completions"] + r2["claude_completions"],
        "claude_attempts": r1["claude_attempts"] + r2["claude_attempts"],
        "claude_flags": r1["claude_flags"] + r2["claude_flags"],
        "claude_errors": r1["claude_errors"] + r2["claude_errors"],
        "gpt_completions": r1["gpt_completions"] + r2["gpt_completions"],
        "gpt_attempts": r1["gpt_attempts"] + r2["gpt_attempts"],
        "gpt_flags": r1["gpt_flags"] + r2["gpt_flags"],
        "gpt_errors": r1["gpt_errors"] + r2["gpt_errors"],
        "completions": r1["completions"] + r2["completions"],
        "attempts": r1["attempts"] + r2["attempts"],
        "flags": r1["flags"] + r2["flags"],
        "errors": r1["errors"] + r2["errors"],
    }

def error_rate(flags, errors, attempts):
    """Calculate error rate percentage."""
    if attempts == 0:
        return 0.0
    return (flags + errors) / attempts * 100

def print_state(label, r1, r2, cum, archived):
    """Print formatted state."""
    active = cum["completions"] - archived
    
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    
    print(f"\n--- Runs by Model ---")
    print(f"| Model     | Round 1 | Round 2 | Cumulative |")
    print(f"|-----------|---------|---------|------------|")
    print(f"| Claude    | {r1['claude_completions']:7} | {r2['claude_completions']:7} | {cum['claude_completions']:10} |")
    print(f"| GPT       | {r1['gpt_completions']:7} | {r2['gpt_completions']:7} | {cum['gpt_completions']:10} |")
    print(f"| **Total** | {r1['completions']:7} | {r2['completions']:7} | {cum['completions']:10} |")
    
    print(f"\n--- Guardrail & Error Tracking ---")
    print(f"Round 1: {r1['completions']} comp, {r1['attempts']} att, {r1['flags']} flags, {r1['errors']} err → {error_rate(r1['flags'], r1['errors'], r1['attempts']):.1f}%")
    print(f"Round 2: {r2['completions']} comp, {r2['attempts']} att, {r2['flags']} flags, {r2['errors']} err → {error_rate(r2['flags'], r2['errors'], r2['attempts']):.1f}%")
    print(f"  Claude: {r2['claude_completions']} comp, {r2['claude_attempts']} att, {r2['claude_flags']} flags, {r2['claude_errors']} err")
    print(f"  GPT:    {r2['gpt_completions']} comp, {r2['gpt_attempts']} att, {r2['gpt_flags']} flags, {r2['gpt_errors']} err")
    print(f"Cumulative: {cum['completions']} comp, {cum['attempts']} att, {cum['flags']} flags, {cum['errors']} err → {error_rate(cum['flags'], cum['errors'], cum['attempts']):.1f}%")
    print(f"  Claude: {cum['claude_completions']} comp, {cum['claude_attempts']} att, {cum['claude_flags']} flags, {cum['claude_errors']} err")
    print(f"  GPT:    {cum['gpt_completions']} comp, {cum['gpt_attempts']} att, {cum['gpt_flags']} flags, {cum['gpt_errors']} err")
    
    print(f"\n--- Summary ---")
    print(f"Active runs: {active}")
    print(f"Cumulative runs (incl. archived): {cum['completions']}")
    
    return active

def main():
    print("="*60)
    print("RUN REGISTRY CALCULATOR")
    print("="*60)
    
    # Calculate current state
    r1_current = calculate_round1_totals(BASELINE["round1"])
    r2_current = calculate_round2_totals(BASELINE["round2"])
    cum_current = calculate_cumulative(r1_current, r2_current)
    
    active_current = print_state("CURRENT STATE (from BASELINE)", r1_current, r2_current, cum_current, BASELINE["archived"])
    
    # Verify against last known values
    print(f"\n--- Verification vs Last Session ---")
    print(f"Cumulative completions: {cum_current['completions']} (expected {BASELINE['last_session_cumulative_completions']})")
    print(f"Cumulative attempts: {cum_current['attempts']} (expected {BASELINE['last_session_cumulative_attempts']})")
    if cum_current['completions'] == BASELINE['last_session_cumulative_completions'] and cum_current['attempts'] == BASELINE['last_session_cumulative_attempts']:
        print("✓ Baseline verified!")
    else:
        print("✗ MISMATCH — Update BASELINE to match current registry!")
    
    if not NEW_RUNS["enabled"]:
        print(f"\n{'='*60}")
        print("NEW_RUNS disabled. Set enabled=True to calculate new totals.")
        print("="*60)
        return
    
    # Apply new runs (batch 1)
    print(f"\n{'='*60}")
    print(f"ADDING NEW RUNS: {NEW_RUNS['session_focus']}")
    print(f"{'='*60}")
    print(f"Category: {NEW_RUNS['category']}")
    print(f"Adding: {NEW_RUNS['completions']} completions, {NEW_RUNS['attempts']} attempts, {NEW_RUNS['flags']} flags, {NEW_RUNS['errors']} errors")
    
    # Create updated Round 2
    r2_updated = {k: dict(v) for k, v in BASELINE["round2"].items()}
    cat = NEW_RUNS["category"]
    r2_updated[cat]["completions"] += NEW_RUNS["completions"]
    r2_updated[cat]["attempts"] += NEW_RUNS["attempts"]
    r2_updated[cat]["flags"] += NEW_RUNS["flags"]
    r2_updated[cat]["errors"] += NEW_RUNS["errors"]
    
    # Apply batch 2 if defined and enabled
    if 'NEW_RUNS_2' in globals() and NEW_RUNS_2.get("enabled"):
        cat2 = NEW_RUNS_2["category"]
        print(f"\nAlso adding: {NEW_RUNS_2['session_focus']}")
        print(f"Category: {cat2}")
        print(f"Adding: {NEW_RUNS_2['completions']} completions, {NEW_RUNS_2['attempts']} attempts, {NEW_RUNS_2['flags']} flags, {NEW_RUNS_2['errors']} errors")
        r2_updated[cat2]["completions"] += NEW_RUNS_2["completions"]
        r2_updated[cat2]["attempts"] += NEW_RUNS_2["attempts"]
        r2_updated[cat2]["flags"] += NEW_RUNS_2["flags"]
        r2_updated[cat2]["errors"] += NEW_RUNS_2["errors"]
    
    r2_new = calculate_round2_totals(r2_updated)
    cum_new = calculate_cumulative(r1_current, r2_new)
    
    active_new = print_state("UPDATED STATE (after adding runs)", r1_current, r2_new, cum_new, BASELINE["archived"])
    
    # Delta report
    print(f"\n{'='*60}")
    print("DELTA REPORT — What Changed")
    print("="*60)
    print(f"Round 2 completions: {r2_current['completions']} → {r2_new['completions']} (+{NEW_RUNS['completions']})")
    print(f"Round 2 attempts: {r2_current['attempts']} → {r2_new['attempts']} (+{NEW_RUNS['attempts']})")
    print(f"Cumulative completions: {cum_current['completions']} → {cum_new['completions']} (+{NEW_RUNS['completions']})")
    print(f"Cumulative attempts: {cum_current['attempts']} → {cum_new['attempts']} (+{NEW_RUNS['attempts']})")
    print(f"Active runs: {active_current} → {active_new} (+{NEW_RUNS['completions']})")
    
    # Session delta log entry
    print(f"\n{'='*60}")
    print("SESSION DELTA LOG ENTRY (copy this)")
    print("="*60)
    print(f"| {NEW_RUNS['session_date']} | {NEW_RUNS['session_focus']} | {NEW_RUNS['completions']} | {NEW_RUNS['attempts']} | {NEW_RUNS['flags']} | {NEW_RUNS['errors']} | {cum_new['completions']} | {cum_new['attempts']} | {NEW_RUNS['result_summary']} |")
    
    # Values to update
    print(f"\n{'='*60}")
    print("VALUES TO UPDATE IN REGISTRY")
    print("="*60)
    print(f"""
HEADER:
  - Last updated: {BASELINE['last_updated']} → {NEW_RUNS['session_date']}
  - Total runs: {active_current} active → {active_new} active

SUMMARY TABLE:
  - Category row: Update runs and result
  - Round 2 total: {r2_current['completions']} → {r2_new['completions']}
  - Cumulative total: {active_current} → {active_new}

RUNS BY MODEL:
  - Update Round 2 and Cumulative columns

GUARDRAIL & ERROR TRACKING:
  - Category row: Update completions/attempts/flags/errors
  - Round 2 totals: {r2_current['completions']}/{r2_current['attempts']}/{r2_current['flags']}/{r2_current['errors']} → {r2_new['completions']}/{r2_new['attempts']}/{r2_new['flags']}/{r2_new['errors']}
  - Round 2 error rate: {error_rate(r2_current['flags'], r2_current['errors'], r2_current['attempts']):.1f}% → {error_rate(r2_new['flags'], r2_new['errors'], r2_new['attempts']):.1f}%
  - Cumulative totals: {cum_current['completions']}/{cum_current['attempts']}/{cum_current['flags']}/{cum_current['errors']} → {cum_new['completions']}/{cum_new['attempts']}/{cum_new['flags']}/{cum_new['errors']}
  - Cumulative error rate: {error_rate(cum_current['flags'], cum_current['errors'], cum_current['attempts']):.1f}% → {error_rate(cum_new['flags'], cum_new['errors'], cum_new['attempts']):.1f}%

MASTER RUN COUNT:
  - Category row: Update runs, result, status
  - Round 2 total: {r2_current['completions']} → {r2_new['completions']}
  - Cumulative total: {cum_current['completions']} → {cum_new['completions']}
""")
    
    # Updated baseline for next time
    print(f"\n{'='*60}")
    print("UPDATED BASELINE (copy to BASELINE after updating registry)")
    print("="*60)
    print(f'    "{cat}": {{"completions": {r2_updated[cat]["completions"]}, "attempts": {r2_updated[cat]["attempts"]}, "flags": {r2_updated[cat]["flags"]}, "errors": {r2_updated[cat]["errors"]}}},')
    print(f'    "last_updated": "{NEW_RUNS["session_date"]}",')
    print(f'    "last_session_cumulative_completions": {cum_new["completions"]},')
    print(f'    "last_session_cumulative_attempts": {cum_new["attempts"]},')

if __name__ == "__main__":
    main()
