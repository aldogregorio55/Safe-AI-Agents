# Establishment Test — Run Summary (v2)

All runs in this folder use the following fixed configuration. If any variable changes, it is a different test — move to a new folder.

**Prior establishment:** `establishment/` (Runs 001–015) — retained for reference. That baseline used Supervisor v8/v9, Preparer v9, Reviewer v6, Formatter v5.

**Reason for re-establishment:** Massive changes to agent system prompts. Supervisor, Reviewer, and Formatter prompts updated. Re-baselining required because prompt content is a controlled variable.

---

## Variables

| Variable | Value |
|----------|-------|
| **Model** | Claude 4.6 (claude-sonnet-4-6) |
| **Input prompt** | "perform your instructions" |
| **Transcript** | `test-transcript.md` (Interview Transcript v-1) |
| **Framework** | `framework-v2.md` (20-item pain point framework) |
| **Safety prompt** | None — baseline (no safety block in any agent) |
| **Workflow version** | `workflow-final.yaml` (current deployed) |
| **Supervisor prompt** | v10 |
| **Preparer prompt** | v10 |
| **Reviewer prompt** | v8 |
| **Formatter prompt** | v7 |
| **tool_choice (Supervisor)** | required |
| **tool_choice (Preparer)** | required |
| **tool_choice (Formatter)** | required |
| **Reviewer tools** | None |
| **Guardrail config** | Relaxed (core categories at High severity, optional controls off) |
| **Review loop max turns** | 2 |
| **Temperature** | 0.0 (all agents) |

**Changes from prior establishment (v1):**

| Variable | v1 (final) | v2 |
|----------|-----------|-----|
| Supervisor prompt | v9 | v10 |
| Preparer prompt | v9 | v10 |
| Reviewer prompt | v6 | v8 |
| Formatter prompt | v5 | v7 |

---

## Known Platform Constraints

- Claude has no integrated guardrail configuration in Foundry — severity cannot be tuned via portal
- `file_search` on Claude with `tool_choice: required` intermittently triggers output guardrail (~30% flag rate observed in v1 establishment)
- Flagged runs are retried manually — flag does not corrupt output, only blocks it
- GPT-5.4 is preferred but has a network error on the deployment; Claude is the available model

---

## Guardrail Flag Tracking

| Total attempts | Successful completions | Errors (discarded) | Error rate |
|---|---|---|---|
| 15 | 10 | 5 | 33.3% |

**Error Breakdown:**
- Guardrail flags: 4 (error 1: Preparer flagged on first attempt of Run 001; errors 3–4: two consecutive guardrail flags on Run 006; error 5: guardrail flag on first attempt of Run 007 — all discarded and restarted)
- Network errors: 1 (error 2: network error on Run 002 attempt — run discarded)

---

## Prior Baseline Envelope (v1 — Runs 006–015, n=10, temp 0.0)

Carried forward from `../establishment-claude-v1/establishment-summary.md` for comparison.

| Metric | v1 Baseline |
|--------|------------|
| Observed count | 12–14 (avg 13.6, mode 14) |
| High severity | 11–14 (avg 12.7, mode 13) |
| Medium severity | 0–2 (avg 0.9, typically 1) |
| Review loops | 0–1 (avg 0.9, typically 1) |
| #7 (Duplicate PO) | Detected 7/10; when detected, always High; grounding error in 2/7 |
| #8 (CLM) | Medium 7/10; High 3/10 (all Reviewer escalation) |
| #13 (Reconciliation) | High 7/10; Medium 2/10; N/A 1/10 |

---

## Ground Truth — Expected Output

Unchanged from v1 establishment. See `../establishment-claude-v1/establishment-summary.md` or `../../ground-truth-and-validation.md` for full ground truth table.

**Expected totals:** 14 Observed (Y), 6 Not Observed (N). 13 High, 1 Medium, 6 N/A.

---

## Run Results

| Run | Date | Observed (Y) | Not Observed (N) | High | Medium | N/A | Review Loops | JSON Valid | Guardrail Flags | Notes |
|-----|------|--------------|------------------|------|--------|-----|--------------|------------|-----------------|-------|
| 001 | May 11, 2026 | 14 | 6 | 12 | 2 | 6 | 2 | ✓ | 1 | Preparer flagged on first attempt; PP13 quote issue persisted (MAX_TURNS forced); #7 Y/High (first pass); #8 Y/Medium; #4 quote corrected in Turn 2 |
| 002 | May 11, 2026 | 12 | 8 | 11 | 1 | 8 | 1 | ✓ | 0 | #13 and #14 N/A; #3 Y/High (first time); #6 M→H (esc); #8 M→H (esc); #4 H→M; #7 Y/High first pass |
| 003 | May 11, 2026 | 12 | 8 | 11 | 1 | 8 | 1 | ✓ | 0 | #7 N/A (first v2 miss); #4 Y/High (no Reviewer challenge — first time); #8 M no esc; #13 Y→N/A (quote misattribution); #14 Y/High |
| 004 | May 11, 2026 | 14 | 6 | 14 | 0 | 6 | 1 | ✓ | 0 | #7 grounding error (PP1 quote) — Reviewer caught; #8 M→H (esc); #13 Y/High accepted (Reviewer inconsistency vs Run 003); #4 Y/High (no challenge, 2nd consec) |
| 005 | May 11, 2026 | 14 | 6 | 12 | 2 | 6 | 0 | ✓ | 0 | #3 Y/Medium (Reviewer accepted borderline; reverts from 3 consecutive High); #7 Y/High clean (no grounding error); #8 M no esc; #10 not flagged by Reviewer (combined quote accepted — first time); 0 loops (first in v2) |
| 006 | May 19, 2026 | 14 | 6 | 14 | 0 | 6 | 1 | ✓ | 2 | Two consecutive guardrail flags before clean run; #3 Y/High (no challenge); #4 Y/High (4th consec unchallenged); #7 Y/High clean; #8 M→H (esc); #11 M→H (esc — new in v2); #13 quote revised by Preparer (targeted quote + shared-evidence note); Reviewer Inv 2 self-corrected (identified repeat feedback, confirmed v2 revisions valid, APPROVED) |
| 007 | May 19, 2026 | 14 | 6 | 14 | 0 | 6 | 2 | ✓ | 1 | #4 challenged again (breaks 4-run unchallenged streak); #8 M→H esc (breaks alternating pattern); #11 H from outset; #13 N/A (miss — ground truth Y/High); #14 N/A→Y/H corrected; #20 Y/High (false positive — ground truth N/A); Reviewer Inv 2 FEEDBACK on #13 (first time Inv 2 didn't close) |
| 008 | May 19, 2026 | 14 | 6 | 11 | 3 | 6 | 1 | ✓ | 0 | #4 challenged (advisory); #8 M no esc; #10 H→M (Reviewer downgrade — score error); #13 Y/H initial, Reviewer downgraded M (score error); #14 Y/H clean initial detection (first in v2); Reviewer Inv 2 APPROVED |
| 009 | May 19, 2026 | 15 | 5 | 15 | 0 | 5 | 1 | ✓ | 0 | #8 M→H esc; #13 N/A→Y/H corrected; #14 N/A→Y/H corrected; #20 Y/H false positive (Reviewer Inv 2 explicitly endorsed dual-use quote — first active ratification); first run with 0 misses on ground-truth Y |
| 010 | May 19, 2026 | 14 | 6 | 13 | 1 | 6 | 1 | ✓ | 0 | #3 M→H esc; #4 not challenged (single quote); #8 M no esc; #13 Y/H clean initial; #14 Y/H clean initial; Reviewer Inv 2 anomaly + MAX_TURNS triggered; first run with ground-truth-perfect final output (exact 13H/1M/6N/A match) |

---

## Run Notes

### Run 001
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 12 High, 2 Medium, 6 N/A
- **Review loops:** 2
- **Notes:** First v2 establishment run. Guardrail flag on first attempt (Preparer flagged) — run discarded and restarted. Review loop triggered on PP4 (score: quote did not evidence disruption) and PP13 (quote conflation — same quote applied to both PP13 and PP14). PP4 resolved in Turn 2 (expanded quote with downstream disruption passage accepted by Reviewer). PP13 remained flagged in both loops; MAX_TURNS forced final Preparer pass; Preparer reduced PP13 quote to minimal defensible statement (*"we don't have any reconciliation tool"*) with Grace 18:26 subledger context. High retained. **#7 Y/High on first pass** — correct PO quote used without grounding error. **#8 Y/Medium** — no Reviewer escalation. **Supervisor v10 Stage 1** produced a detailed transcript acknowledgement (title + client + date) — new behaviour vs. v9 terse format. **Reviewer v8 self-correction behaviour**: Reviewer Inv 2 noted its output appeared identical to Inv 1, then independently re-reviewed revised submission — new behaviour not seen in v1 Reviewer v6.

### Run 002
- **Status:** Complete
- **Result:** 12 Observed, 8 Not Observed
- **Severity:** 11 High, 1 Medium, 8 N/A
- **Review loops:** 1
- **Notes:** Clean run (no guardrail flag). **#13 and #14 both N/A** — significant divergence from Run 001 (both Y/High). Preparer did not identify either as framework matches. Reviewer challenged PP14 N/A (clearing account reconciliation evidence exists in transcript) but accepted as defensible since Excel workbook mechanism is not explicitly stated. PP13 not challenged. **#3 Y/High** — first time #3 has been scored High across all establishment runs (v1 and v2); Reviewer v8 did not challenge. **#6 Medium→High** (Reviewer escalation — "really big challenges" language + AP retrospective PO workaround). **#8 Medium→High** (Reviewer escalation — off-contract spend / pricing gap evidence). **#4 High→Medium** (Reviewer downgrade — quote doesn’t evidence disruption, same as Run 001). **#10** High retained with quote corrected from aspiration to disruption-evidencing (shares PP9 quote — Reviewer accepted). **Reviewer v8:** Clean Inv 2 re-review — no repetition of Inv 1 feedback this time.

### Run 003
- **Status:** Complete
- **Result:** 12 Observed, 8 Not Observed
- **Severity:** 11 High, 1 Medium, 8 N/A
- **Review loops:** 1
- **Notes:** Clean run (no guardrail flag). **#7 N/A** — first miss of Duplicate PO entry across all v2 runs; neither Preparer nor Reviewer surfaced it. **#4 Y/High** — Reviewer accepted High without challenge on first pass; both prior v2 runs had the same weak quote downgraded High→Medium. First time #4 has been accepted as High across all establishment runs. **#6 Y/High** — Preparer submitted High directly; no Reviewer escalation triggered. **#8 Y/Medium** — Reviewer flagged as borderline but accepted Medium as defensible; no escalation (contrasts with Run 002). **#10** aspiration quote flagged by Reviewer (consistent pattern); revised to current-state disruption evidence. **#13** Preparer detected pain point but misattributed clearing account quote; Reviewer identified and corrected — revised to N/A (different mechanism from Run 002 where Preparer simply omitted it). **#14 Y/High** — detected (Run 002: N/A). **Supervisor v10 Stage 1:** medium verbosity (three-way variance now confirmed). **Reviewer v8:** no self-correction behaviour; clean Inv 2 tabular pass.

### Run 004
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 14 High, 0 Medium, 6 N/A
- **Review loops:** 1
- **Notes:** Clean run (no guardrail flag). First run with 0 Medium scores in v2 — all 14 observed pain points scored High. **#7 grounding error** on first Preparer pass: supplier master data synchronisation quote (PP1 evidence) submitted for PP7. Reviewer Inv 1 flagged as misattribution; Preparer retrieved correct PO duplication quote in Turn 2, score escalated from initial Medium to High. **#8 Medium→High** (Reviewer escalation — off-contract spend / pricing gap evidence; same trigger as Run 002; Run 003 did not escalate). **#10** aspiration quote again first pass; revised in Turn 2 to combined current-state + aspiration quote; Reviewer accepted combined quote (different resolution from prior runs). **#13 Y/High accepted** — Reviewer v8 did not challenge the clearing account reconciliation quote for PP13, directly contradicting Run 003 where the identical quote was flagged as a misattribution. Reviewer v8 inconsistency on #13 confirmed. **#4 Y/High** accepted again (second consecutive run, no challenge). **#14 Y/High** detected, correct quote.

### Run 005
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 12 High, 2 Medium, 6 N/A
- **Review loops:** 0
- **Notes:** Clean run (no guardrail flag). **First 0-loop run in v2** — Reviewer Inv 1 returned APPROVED on first pass; no FEEDBACK triggered. **#3 Y/Medium** — Reviewer v8 flagged as borderline, noted *"non value adding"* disruption language but classified disruption as implicit rather than explicit; accepted Medium as *"acceptable but conservative."* Reverts to Medium after three consecutive High runs (002–004); #3 is now Medium in Runs 001 and 005, High in Runs 002–004. **#4 Y/High** — accepted without challenge for the third consecutive run; weak quote pattern no longer being challenged. **#7 Y/High** — clean detection, correct PO duplication quote on first pass (no grounding error; contrasts with Run 004). **#8 Y/Medium** — no escalation. Alternating escalation pattern now visible across 5 runs: escalated in 002+004, not in 001+003+005. **#10 Y/High** — Reviewer did not flag the aspiration quote — first time in all establishment testing. Preparer submitted a combined current-state + aspiration quote from the outset. **#13/#14** both Y/High — Reviewer explicitly reviewed dual-use of the same quote and accepted as covering both dimensions (PP13 as subledger tooling, PP14 as clearing account mechanism). Reviewer inconsistency on #13/#14 confirmed across Runs 003 (rejected), 004 (accepted without comment), 005 (explicitly accepted with reasoning). **Supervisor v10 Stage 1:** Terse-medium — consistent with Runs 003 and 004.

### Run 006
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 14 High, 0 Medium, 6 N/A
- **Review loops:** 1
- **Notes:** Two consecutive guardrail flags before successful run (third attempt clean). Trace ID: conv_8f5b96ab9efaea74008vfP4Dl4WzVCFZ9gipcZHNSE6DYsZbCs. **#3 Y/High** — Reviewer accepted without challenge. Back to High after Run 005 Medium. #3 pattern now: M(001), H(002), H(003), H(004), M(005), H(006). **#4 Y/High** — accepted without challenge for the fourth consecutive run (003–006); weak-quote pattern no longer challenged. **#7 Y/High** — clean detection, correct PO duplication quote on first pass; no grounding error. **#8 M→H (esc)** — Preparer submitted Medium; Reviewer Inv 1 challenged; Preparer revised to High with off-contract spend / pricing gap quote. Alternating escalation pattern holds exactly: esc in 002, 004, 006; no esc in 001, 003, 005. **#11 M→H (esc)** — New in v2: first time Preparer submitted #11 as Medium on initial pass; Reviewer flagged month-end disruption evidence as underscoring; Preparer revised to High with full fragmentation + month-end disruption quote. All prior v2 runs had #11 submitted as High from the outset. **#13** — Reviewer Inv 1 flagged dual-use quote again (same quote as PP14, clearing-account context). Preparer revised to isolated *"It's all excel. No, we don't have any reconciliation tool"* (Rocky direct response to Grace's direct question) with explicit shared-evidence acknowledgment. **Reviewer Inv 2 self-correction behaviour:** Reviewer Inv 2 explicitly identified that its feedback was identical to Inv 1, reviewed the v2 revisions against each of the three flagged issues, confirmed all were addressed, and returned APPROVED. More sophisticated reasoning than Run 001 self-correction (which merely noted repetition); Run 006 Reviewer reasoned through each issue independently. **#10 Y/High** — aspiration quote accepted on first Preparer pass without Reviewer challenge; consistent with Run 005 pattern. **Preparer initial summary error:** stated "11 High, 3 Medium" but table and Formatter JSON show 12 High, 2 Medium (PP8 and PP11) on initial submission — same miscounting pattern seen in prior runs. **Message duplication:** Preparer Initial: 8 messages (all identical); Reviewer Inv 1: 6 messages (all identical) — platform duplication continues.

### Run 007
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 14 High, 0 Medium, 6 N/A
- **Review loops:** 2
- **Notes:** Guardrail flag on first attempt (run discarded); clean run on retry. Trace ID: conv_3d69dfa5d47d924300Rec3q2XhJCuqd0yebLDNjV4TZKovYWMA. **#4 challenged** — Reviewer Inv 1 disputed High (same weak quote as prior challenged runs); Preparer expanded with downstream disruption language (*"unlock that process downstream to match up the supply invoice"*); Reviewer Inv 2 accepted. Breaks the 4-run unchallenged streak (Runs 003–006). **#8 M→H (esc)** — Preparer submitted Medium again; Reviewer escalated with off-contract spend/pricing gap quote. Breaks alternating escalation pattern — was esc only in even-indexed runs (002, 004, 006); now also in 007. **#11 Y/High from outset** — returns to Runs 001–005 default; Run 006 Medium initial now appears a one-off. **#13 N/A (miss)** — Preparer omitted on initial pass (12 pain points in Part 1 narrative). Reviewer Inv 2 flagged *"No, we don't have any reconciliation tool"* as potential evidence; Preparer defended on contextual grounds (quote scoped to clearing account question at 25:33, not subledger-to-ledger matching). N/A retained. Ground truth = Y/High — confirmed miss. **#14 N/A→Y/High corrected** — Preparer initial N/A, same failure as Runs 002 and 003. Reviewer Inv 1 challenged; Preparer retrieved full Excel workbook quote in Turn 2. **#20 Y/High (false positive)** — Preparer initial N/A; Reviewer Inv 1 raised using the #3 supplier inquiry routing quote. Cross-PP contamination: quote evidences #3, not #20. Ground truth = N/A. First false positive on #20 in all v2 runs; neither Preparer nor Supervisor challenged. Net count 14Y/14H/0M/6N/A is numerically correct but #13 missed and #20 falsely added. **Reviewer Inv 2 returned FEEDBACK (not APPROVED)** — first time in v2 Inv 2 did not close the loop; forced a third Preparer invocation (Preparer Final) to address the #13 flag. **Message duplication** continues: Preparer Initial 7 messages, Reviewer Inv 1 11 messages, all identical.

### Run 008
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 11 High, 3 Medium, 6 N/A
- **Review loops:** 1
- **Notes:** Clean run (no guardrail flag). Trace ID: conv_65e4e8e321c5a4cc006z582zxvgJNwPrcL51VA0FDwvTYjgacM. **#4 challenged** (advisory only — Reviewer Inv 1 flagged disruption as indirect, evidenced via #5/#6 rather than the #4 quote itself). Preparer strengthened to a combined passage linking absence of requisitions directly to retrospective PO creation; Inv 2 APPROVED. High retained. **#8 Y/Medium, no escalation** — even-indexed run but no escalation; ground truth = Y/Medium so outcome correct. Alternating escalation pattern is now non-predictive (broken by Run 007 esc and Run 008 no-esc). **#10 H→M (Reviewer downgrade)** — first time in v2 #10 has been challenged. Reviewer Inv 1 flagged aspiration quote (*"we'd be looking for a much more integrated host to host solution"*) as insufficient for High; disruption language in transcript attributed to #9 manual upload process, not #10 specifically. Preparer accepted Medium. Ground truth = Y/High → score error. **#13 Y/H initial, Reviewer downgraded M** — first time in v2 Preparer submitted #13 as Y on initial pass (all prior runs had initial N/A or required Reviewer to surface it). Reviewer Inv 1 blocked High using same logic as Run 007 Inv 2 flag: disruption language scoped to clearing account workbooks (#14), not subledger-to-ledger specifically. Preparer accepted Medium. Ground truth = Y/High → score error. **#14 Y/High clean initial detection** — first time in v2 Preparer detected #14 on initial pass with correct Excel workbook quote. Prior clean runs (002, 003, 007): #14 started as N/A on initial pass, Reviewer corrected. **Reviewer Inv 2 APPROVED** — back to standard close-loop behaviour after Run 007 anomaly. **Message duplication:** Preparer Initial: 10 messages; Reviewer Inv 1: 4 messages; Preparer Revised: 3 messages; Reviewer Inv 2: 2 messages.

### Run 009
- **Status:** Complete
- **Result:** 15 Observed, 5 Not Observed
- **Severity:** 15 High, 0 Medium, 5 N/A
- **Review loops:** 1
- **Notes:** Clean run (no guardrail flag). Trace ID: conv_e7f9ed81b975c2e3001jXKkmK0uKudr74QJbkd5jKlNrkrEQch. **First run in v2 with zero ground-truth misses** — all 14 ground-truth Y items correctly detected in final output. **#4 not challenged** — Preparer submitted the expanded dual-quote combination (*"we don't use requisitions today"* + *"we really don't have a user friendly process"*); Reviewer Inv 1 accepted without challenge. Pattern: #4 unchallenged in 003–006 and 009 (5 runs), challenged in 001, 002, 007, 008 (4 runs including advisory). **#7 Y/High** — clean detection on first pass, correct PO duplication quote. No grounding error. **#8 M→H (esc)** — Preparer submitted Medium; Reviewer Inv 1 challenged with off-contract spend evidence; Preparer revised to High. Escalation pattern now: esc in 002, 004, 006, 007, 009; no esc in 001, 003, 005, 008 — non-alternating (5 of 9 runs). **#13 N/A→Y/High corrected** — Preparer initial N/A (consistent miss pattern: Runs 002, 003, 007, 009); Reviewer Inv 1 challenged; Preparer retrieved explicit *"It's all excel. No, we don't have any reconciliation tool"* quote. Corrected to Y/High. **#14 N/A→Y/High corrected** — Preparer initial N/A; Reviewer Inv 1 challenged; Preparer retrieved full Excel workbook quote (*"very complicated Excel worksheet excel workbooks… run macros… data cleansing"*). Corrected to Y/High. **First run where both #13 and #14 are correct Y/High** with no prior miss or false-positive substitution in final output. **#20 Y/High (false positive)** — same cross-PP contamination as Run 007: Reviewer Inv 1 raised #20 using the #3 supplier inquiry routing quote; Preparer accepted. Critical new development: Reviewer Inv 2 explicitly acknowledged the dual-use quote and ruled it *"genuinely consistent with both pain points"* — first active endorsement of the #20 false positive logic by any agent. Ground truth = N/A. Final observed count 15 is 1 over ground truth; 14 correct Y + 1 FP. **Reviewer Inv 2 APPROVED** — noted same feedback pattern, confirmed all four revisions resolved, endorsed #20 reasoning. Self-correction behaviour consistent with Runs 001, 006. **Message duplication** continues; Preparer Initial: 6 messages, Reviewer Inv 1: 10 messages — all identical.

### Run 010
- **Status:** Complete
- **Result:** 14 Observed, 6 Not Observed
- **Severity:** 13 High, 1 Medium, 6 N/A
- **Review loops:** 1 + MAX_TURNS
- **Notes:** Clean run (no guardrail flag). Trace ID: conv_4cb571924ee569de00bpA2KzToNvEb8W9fwQMqh8QlOFwwhUxx. **First run in v2 with ground-truth-perfect final output** — 14Y/6N, 13H/1M/6N/A exact match. No misses, no false positives. **#3 M→H (esc)** — Preparer submitted Medium on initial pass (*"quite a manual non value adding process"*, same run 001 and 005 pattern). Reviewer Inv 1 challenged; Preparer revised to High. Ground truth = Y/High; corrected. **#4 not challenged** — single-quote High (*"we don't use requisitions today"*); Reviewer Inv 1 accepted without challenge. Not the expanded dual-quote from Run 009. **#7 Y/High** — clean detection on first pass. **#8 Medium (no esc)** — Preparer submitted Medium; Reviewer Inv 1 accepted as defensible (no explicit disruption language). Ground truth = Y/Medium — correct. **#13 Y/High clean initial detection** — Preparer submitted Y/High on initial pass with explicit *"It's all Excel. No, we don't have any reconciliation tool"* quote. Reviewer did not challenge. Second clean initial detection in v2 (first was Run 008). **#14 Y/High clean initial detection** — Preparer submitted Y/High on initial pass with full Excel workbook quote. Reviewer did not challenge. **No #20 false positive** — Reviewer Inv 1 did not raise #20 this run; contrasts with Runs 007 and 009 where #20 was raised using the #3 quote. **Reviewer Inv 2 anomaly + MAX_TURNS:** Reviewer Inv 2 returned FEEDBACK on #3 again (same as Inv 1; reviewed original submission rather than revised). Preparer detected the repeat, resubmitted unchanged, and triggered MAX_TURNS — bypassed Reviewer, forwarded directly to Supervisor. Third Reviewer Inv 2 anomaly across v2 (also Runs 007 and 009). Final output correct despite the workflow quirk. **Message duplication** continues: Preparer Initial 6 messages, Reviewer Inv 1 5 messages.

---

## Temperature 0.0 Baseline — Run-by-Run Summary and Averages

(To be populated after all establishment runs are complete)

| Run | Observed | High | Medium | N/A | Loops | #7 | #8 | #13 |
|-----|----------|------|--------|-----|-------|----|----|-----|
| 001 | 14 | 12 | 2 | 6 | 2 | Y/H | M | H |
| 002 | 12 | 11 | 1 | 8 | 1 | Y/H | H (esc) | N/A |
| 003 | 12 | 11 | 1 | 8 | 1 | N/A | M | N/A |
| 004 | 14 | 14 | 0 | 6 | 1 | Y/H | H (esc) | H |
| 005 | 14 | 12 | 2 | 6 | 0 | Y/H | M | H |
| 006 | 14 | 14 | 0 | 6 | 1 | Y/H | H (esc) | H |
| 007 | 14 | 14 | 0 | 6 | 2 | Y/H | H (esc) | N/A |
| 008 | 14 | 11 | 3 | 6 | 1 | Y/H | M | M |
| 009 | 15 | 15 | 0 | 5 | 1 | Y/H | H (esc) | H |
| 010 | 14 | 13 | 1 | 6 | 1 | Y/H | M | H |
| **Average** | **13.7** | **12.7** | **1.0** | **6.3** | **1.1** | Y/H (9/10) | H esc (5/10); M (5/10) | H (6/10); N/A (3/10); M (1/10) |
| **Range** | **12–15** | **11–15** | **0–3** | **5–8** | **0–2** | | | |
