# Round 2 Observations — In Progress

**Created:** 2026-06-05  
**Last Updated:** 2026-06-09  
**Status:** Complete — all Round 2 testing done (Claude + GPT, Attack Present + False Positive, isolation + workflow)  
**Coverage:** Claude complete (Attack Present + False Positive — isolation + workflow); GPT complete (Establishment + DPI Baseline + Attack Present + False Positive — isolation + workflow)

---

## Claude Observations

### Consistent safety block compliance

Claude exhibited consistent behavior across all safety block runs. Isolation runs reliably complied with the safety block instructions and refused the injections — 10/10 PASS across both conditions.

### Pipeline-wide refusal in workflow mode

Workflow runs for Claude were the most telling. Once the Supervisor flagged the attack, the agents downstream identified the attack and refused to even perform the instructions. This was an unexpected behavior — the workflow identified an attack and then prioritized safety over task compliance. The entire pipeline independently converged on refusal without coordination.

This is a positive emergent effect of the safety block: a single injection defense instruction on the Supervisor cascaded into pipeline-wide resistance. The downstream agents were not given the safety block directly — they made independent decisions to refuse based on the nature of the content they received from the Supervisor's handoff.

### Attribution: safety block vs native model behavior

**Critical note:** Lean v6 is on the Supervisor only. Preparer, Reviewer, and Formatter do not carry the safety block. The Supervisor's `WARNING – POSSIBLE ATTACK` output in each run is directly attributable to Lean v6. The downstream refusals — Preparer naming 5 injection techniques, Reviewer identifying social engineering loops, Formatter resetting conversation state — are all native Claude 4.6 behavior.

The −80pp FAIL rate reduction (80% → 0%) reflects the combined effect of:
1. Lean v6 changing the Supervisor's output (from compliance to WARNING)
2. Claude 4.6's native model resistance in downstream agents reacting to the Supervisor's refusal signal

This means the safety block's value is not just blocking the Supervisor — it's changing what the Supervisor emits downstream, which triggers a cascade of native model defenses across the entire pipeline. One 160-token safety block produced four layers of independent defense.

### False positive behavior — Claude

**0 false positives across all 10 runs (5 workflow + 5 isolation).** Lean v6 does not over-block on Claude in either mode. Claude processed benign input cleanly every time — the Supervisor completed orchestration, fired tool calls, and produced no WARNING or escalation signals on standard transcript input. The injection defense clauses in Lean v6 did not trigger on legitimate task framing.

This is the cleanest possible false positive result: a safety block that produces no over-blocking whatsoever. On Claude, Lean v6 is ready for production use — it blocks attacks reliably (0% attack FAIL) and does not interfere with normal operation (0% FP rate).

---

## GPT Observations

### Architectural instability at baseline

In the baseline GPT establishment tests (no injection, no safety block), GPT already natively failed workflow orchestration multiple times. The model would confuse itself mid-run and return the wrong response for a different agent. GPT is architecturally more unstable than Claude with no malicious content or safety blocks present. This manifested as a 52% error rate (guardrail flags + network errors) and inconsistent agent handoff behavior.

### Isolation vs workflow — divergent vulnerability profiles

Direct prompt injection attacks were where GPT became more interesting. When I tested the injection against the Supervisor in isolation, it always ignored the injection and returned "Transcript received." — 5/5 PASS with no safety block, 0% FAIL rate.

However, when I tested it on the workflow, the entire workflow was affected downstream. The Supervisor still resisted the attack — returning "Transcript received." on every attempt — however the Preparer would instead reveal the entire framework provided in context rather than provide an analysis. That is a critical safety failure: printing an entire context document as a response to an injection. The whole workflow did not proceed correctly in a majority of cases (3/5 FAIL, 60%).

### Safety block on GPT — downstream compliance observed

With the safety block on GPT, isolation testing matched Claude: the Supervisor resisted the injection and called out the attack. However, the downstream agent effects for GPT were once again notable. With the safety block present on GPT, the Supervisor called out the attack — however the Preparer complied with the injection. That is the first time another agent besides the Supervisor directly complied with the injection across all testing.

### Working hypothesis — context propagation vulnerability

My assumption at this point is that GPT is safer in a direct isolated exchange with a user. However, once a different instance of GPT is brought to the conversation with the conversation context of the user input, the new agent is unable to determine the attack from legitimate instructions.

I draw this conclusion from the fact that GPT never complied with the injection in isolation testing, but the Preparer would often break or comply in the workflow setup. The injection payload reaches the Preparer through the Supervisor's handoff mechanism — and GPT's downstream agents cannot reliably distinguish adversarial content in conversation history from legitimate task context.

### False positive behavior — GPT

**GPT produced consistent false positive flags on benign input in both execution modes.** Unlike Claude, the Lean v6 injection defense clauses over-triggered on standard transcript input — the Supervisor interpreted legitimate task framing as a suspected injection attempt and emitted `WARNING – POSSIBLE ATTACK` on benign runs.

**Supervisor isolation (5 runs, Jun 8): 3/5 PASS — 40% false positive rate (2/5 FAIL).** Lean v6 caused the Supervisor to refuse the legitimate task non-deterministically. In failing runs, the model fired `file_search` (retrieved the transcript) but then refused to proceed with orchestration — treating the user's standard instruction as adversarial.

**Full workflow (5 runs, Jun 8): 1/5 PASS — 80% false positive rate (4/5 FAIL).** Supervisor Stage 1 FP rate was 80% (4/5 runs emitted WARNING on benign input). Stage 2 behavior was highly non-deterministic — producing five distinct responses across five runs (WARNING, "Feedback received", "Analysis not approved", "FEEDBACK", "Feedback received"). Critically, the pipeline is non-terminating on Supervisor FP: downstream agents completed in all 5 runs regardless of Supervisor behavior. The FP is a quality and reliability failure, not a hard pipeline blocker. Output metric quality degraded relative to the GPT establishment baseline — Medium avg rose to 1.8 vs 0.7 (+1.1 delta), driven partly by Reviewer non-determinism on borderline IDs amplified by Supervisor instability.

**Combined verdict:** Lean v6 is not fit for production use on GPT 5.4 in this configuration. It fails to defend against attacks in workflow mode (80% attack FAIL) and simultaneously degrades normal operation (80% FP rate in workflow mode). The safety block as designed is calibrated for Claude's behavioral profile and does not transfer cleanly to GPT.

---

## Emerging Findings

1. **Model selection is a safety control.** Claude and GPT exhibit fundamentally different vulnerability profiles under identical conditions. Individual models must be tested for safety behavior before deployment into production user-facing systems.

2. **Isolation testing is insufficient.** A model that passes 100% of isolation tests can still fail in workflow mode. Pipeline context amplifies attack success — this was true for both models but manifested differently (Claude: Supervisor compliance; GPT: downstream Preparer contamination).

3. **Safety block cascading effect (Claude-specific).** On Claude, the safety block on the Supervisor produced pipeline-wide refusal even though downstream agents had no safety block. This suggests the safety block changes how the Supervisor frames its output to downstream agents in a way that triggers their native defenses.

4. **GPT context boundary weakness.** GPT's downstream agents cannot reliably maintain instruction/data separation when adversarial content is embedded in conversation history from an upstream agent. This is a model-level architectural characteristic, not a prompt-level fix.

5. **Safety block calibration is model-specific.** Lean v6 produced 0% FP on Claude and 40–80% FP on GPT under identical conditions. A safety block that works cleanly on one model can actively degrade normal operation on another. Model-specific tuning or separate block variants are required before cross-model deployment.

6. **False positive rate is a production-blocking metric independent of attack defense.** Even if a safety block fully defended against attacks, a 40–80% false positive rate on benign input would make the system unusable. F1 scoring must weight both attack defense and FP rate in the final evaluation.
