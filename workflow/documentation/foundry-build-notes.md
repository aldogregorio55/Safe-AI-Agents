# Build Sessions — Index & Status

**Project:** `safe-agents` — Pain Point Analysis workflow
**Purpose:** Session-by-session index. Load this for a quick status check. Load the dated session file for full details.

---

## Sessions

### Session 1 — 2026-05-04

**Focus:** First full end-to-end run + prompt rewrites + guardrail discovery
**Outcome:** Run 1 complete — 2/14 pain points correctly identified. Real root cause: Preparer lacked transcript in its vector store. Supervisor and Preparer prompts rewritten to fix orchestration language. During testing of rewritten prompts, guardrail blocks began occurring consistently — prompts reverted to originals to stabilise build while root cause was investigated.

**Blockers going into Session 2:**
- Guardrail trigger root cause unknown — suspected prompt content initially, unconfirmed
- Rewritten prompts correct but reverted — pending guardrail resolution before redeployment
- ~~Reviewer and Formatter prompts not yet updated (SDK language still present)~~ — confirmed working as-is, no rewrite needed
- `tool_choice: required` on all tool-bearing agents — not yet changed

**Full details:** `run-diagnostics-2026-05-04.md`

---

### Session 2 — 2026-05-05

**Focus:** Guardrail root cause isolation
**Outcome:** Root cause confirmed and **resolved**. The trigger was ambiguous input (`"go"`) + `tool_choice: required` + `file_search`. The combination forced the model to fabricate purposeless retrieval queries, flooding the output with anomalous content that the output guardrail probabilistically flagged. With a meaningful input (`"perform your instructions"`), all agents pass 10/10 with zero flags.

**Tests run (isolation phase — input: `"go"`):**
| Configuration | Model | Flags |
|---|---|---|
| Real prompt + tools (`tool_choice: required`) | GPT-5.4 | 3/10 |
| Empty prompt + tools (`tool_choice: required`) | GPT-5.4 | 7/10 |
| Completely empty agent (no prompt, no tools) | GPT-5.4 | 0/10 |
| Real prompt + tools (`tool_choice: required`) | Claude 4.6 | 7/10 |

**Tests run (guardrail config phase — input: `"go"`):**
| Configuration | Model | Flags |
|---|---|---|
| Relaxed guardrails (both layers), `tool_choice: required` | GPT-5.4 | ~1-2/10 |
| Core categories at High severity, `tool_choice: required` | GPT-5.4 | ~1/10 |

**Tests run (resolution — input: `"perform your instructions"`):**
| Agent | Model | Flags |
|---|---|---|
| Supervisor | GPT-5.4 | 0/10 |
| Preparer | GPT-5.4 | 0/10 |
| Reviewer | GPT-5.4 | 0/10 |
| Formatter | GPT-5.4 | 0/10 |

**40/40 clean across all agents with meaningful input.**

**Root cause:** Ambiguous input (`"go"`) provided zero context for tool queries. With `tool_choice: required`, the model fabricated vague `file_search` queries, retrieved irrelevant content, and produced anomalous output. The output guardrail's probabilistic scanner flagged this pattern. With purposeful input, queries are grounded, output is structured, and the scanner passes it.

**Key finding:** Removing tools entirely yields 0 flags. Prompt content is not the trigger — empty prompt flags *more* than a real prompt.

**Correction to Session 1:** Claude is not categorically blocked. Same probabilistic issue as GPT — Claude is more sensitive (7/10 vs 3/10), not completely restricted. "100% Claude blocked" was based on a small sample during one session. However, Claude has no integrated guardrail configuration in Foundry — severity levels cannot be tuned via the portal.

**Trace analysis (tracing enabled mid-session):**

Tracing confirmed the precise mechanism. Three execution paths observed from identical input (`"go"`) and config:

| Path | Reasoning | Tool Calls | Tokens | Outcome |
|---|---|---|---|---|
| A — Reasoning | Yes | 0 | 69 | PASS — model skips tool, outputs clarifier |
| B — Tools (lucky) | No | 2 calls / 6 queries | 10,740 | PASS — output scanner doesn't catch it |
| C — Tools (unlucky) | No | 2 calls / 6 queries | 4,613 | FLAG — output scanner fires, `status: "incomplete"` |

**Additional findings from guardrail investigation:**
1. Core content categories (Hate, Sexual, Violence, Self-harm) cannot be fully disabled — non-removable floor at High severity. "Off" requires Modified Content Filtering approval (currently unavailable).
2. Agents only support "Annotate and block" — no passive annotate-only mode for agents.
3. `file_search` is not in the supported tools list for tool call/response intervention points — guardrail fires at the output point, not the tool point.
4. Two distinct failure modes observed: output intervention (tokens consumed, probabilistic) and pre-inference block (zero tokens, ERROR, no trace).
5. A direct prompt injection was NOT flagged by the platform guardrail while benign forced-retrieval output was — the guardrail is not reliably catching adversarial content.
6. Guardrail documentation fully reviewed and recorded in `foundry-reference.md` Section 7.

**Status: RESOLVED.** Guardrail blocker is cleared. All agents pass with meaningful input. Prompt work is unblocked.

**Claude confirmation:** Supervisor also tested on Claude 4.6 with `"perform your instructions"` — no flags. Fix is model-agnostic. GPT-5.4 selected as the production model for the workflow — has existing test data, configurable guardrails, and consistent baselines.

**Full details:** `run-diagnostics-2026-05-04.md` (Session 2 section)
**Raw trace logs:** `trace-logs-2026-05-05.md`

---

### Session 3 — 2026-05-05

**Focus:** Supervisor orchestration bug fix + first successful end-to-end run + establishment testing setup
**Outcome:** Supervisor v8 deployed and confirmed — eliminates the orchestrator mental model bug (agent no longer simulates the full pipeline). First clean end-to-end run produced 14/14 observed pain points correctly identified, 20/20 total accuracy, valid JSON output. Establishment testing (10-run batch) initiated.

**Key changes:**
- Supervisor rewritten from sequential-plan framing to isolated-invocation framing (v8)
- All orchestration language, agent name references, and pipeline simulation triggers removed
- Preparer confirmed working as-is (v9) — no changes needed
- Reviewer and Formatter prompts not modified this session (v6 and v5 respectively) — confirmed no rewrite needed

**Supervisor v8 core change:**
- `<workflow>` section (6-step sequential plan) replaced with `<stages>` (3 isolated receive-then-output invocations)
- Added: "You do not control what happens next — the workflow does"
- Added: "never anticipate or simulate later stages"
- Removed: all agent name references, "invoke the preparer" language

**Run 001 results (establishment):**
- 14/14 observable pain points correctly identified
- 6/6 non-observable correctly marked N/A
- All quotes verbatim from transcript
- Reviewer caught 2 genuine quote format issues (ellipsis splicing), Preparer corrected them
- Review loop: 1 cycle (FEEDBACK → APPROVED)
- Formatter produced valid JSON, correct schema, all 20 items
- Supervisor: clean one-line acknowledgement, no orchestration

**Platform issues:**
- GPT-5.4 has a network error on the deployment — switched to Claude 4.6
- Claude intermittently triggers output guardrail on Preparer `file_search` (~30% flag rate)
- Retry is manual — flagged runs are re-run until completion
- This is a known platform limitation, not a prompt or config issue

**Reviewer transcript access — open issue:**
- Reviewer output in Run 001 referenced retrieving the transcript ("I already retrieved both the framework and transcript during my earlier search")
- Design decision (management directive): Reviewer has NO transcript access — its scope is logic validation only
- Need to verify and remove `file_search` transcript attachment from Reviewer agent in Foundry if present

**Full details:** This session was conducted in chat — no separate diagnostics file. Run 001 raw output saved to `test-runs/establishment-tests/establishment-claude-v1/run-001-raw.md`.

---

## Pending Work

- [x] ~~Redeploy rewritten Supervisor + Preparer prompts~~ — Supervisor v8 deployed and confirmed
- [x] ~~Rewrite Reviewer prompt — remove `transfer_to_preparer` SDK language, add Foundry context~~ — not needed, working as-is
- [x] ~~Review Formatter prompt for SDK framing~~ — not needed, working as-is
- [x] ~~Rename `<handoffs>` → `<output>` in Reviewer and Formatter prompts~~ — not needed, working as-is
- [ ] Verify Reviewer does NOT have transcript in file_search — remove if present (management directive: no transcript access)
- [ ] Complete establishment test batch (10 runs) — 1/10 done
- [x] ~~Change `tool_choice` to `auto` on Supervisor and Formatter~~ — not needed, working as-is with `required`
- [ ] Update build notes after establishment batch completes

---

---

### Session 4 — 2026-05-29

**Focus:** HITL Question node debugging — workflow skipping user approval step post-platform update
**Outcome:** Root cause identified and fixed. Workflow operational with HITL pause restored.

**Root cause:** Foundry platform update (week of 2026-05-26) changed Question node behavior — it now implicitly skips whenever the target variable already has a value, regardless of `skipQuestionMode`. Agent `output: messages` writing to `Local.LatestMessage` before the Question node caused it to skip every time.

**Fix:** Changed Question node variable from `Local.LatestMessage` to `Local.UserApproval` (a fresh variable never written to before the node). `skipQuestionMode` line removed.

**Full details:** `session-notes/session-notes-2026-05-29.md`

---

## Open Questions for Reporting

Platform questions to follow up with Microsoft / Azure documentation:

- Is the output guardrail's sensitivity to anomalous tool retrieval patterns documented behaviour, or a side effect of the probabilistic classifier?
- Can guardrail thresholds ever be fully disabled for safety testing use cases (Modified Content Filtering approval path)?
- Is Claude's lack of integrated guardrail configuration a permanent platform policy or a preview limitation?
- The platform guardrail did not flag a direct prompt injection but flagged benign forced-retrieval output — is there a known false positive/negative pattern for tool-augmented agents?
