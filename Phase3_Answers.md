# Phase 3 - Loop Engineering: Answers

Models: `smollm:135m` (demo 1), `llama3.2` (others) | Folder: `D:\Week_05`

---

## Demo 1 - One call vs a loop (`demo_02.py`)

**Run 1 - no output limit.** The single call took **402.8 s** and produced **18,426 words**: one sentence repeated hundreds of times (and it invented a "faucet"). Validation said `Valid: True`.

**Run 2 - with `num_predict: 150`** (log: `phase3_demo1_output.txt`)

| | A: single call | B: bounded retry loop |
|---|---|---|
| Words | 130 | 118 |
| Calls | 1 | 1 (passed on attempt 1) |
| Time | 2.74 s | about 1.3 s (the pasted output was cut off; check `phase3_demo1_output.txt` for the exact value) |

Both summaries repeated sentences and invented details ("faulty faucet", kitchen "floor").

**Run 3 - forced failure (`MIN_WORDS = 400`)** (log: `phase3_demo1_fail_output.txt`)

| | A | B |
|---|---|---|
| Calls | 1 | 3 (word counts 132, 106, 108) |
| Valid | False | False |
| Time | 1.4 s | 8.8 s |

B's last attempt contradicted the claim ("the homeowner has no photos", "damage was minor").

1. **Termination condition:** a valid summary (at least 40 words) or `MAX_ATTEMPTS = 3`.
2. **Calls allowed:** A = 1, B = at most 3.
3. **Valid output:** returned immediately with the call count and latency.
4. **Invalid on every attempt:** after 3 attempts it stops and returns the last output marked `Valid: False` ("Validation failed after 3 attempts"). It does not loop forever, and the last output must not be trusted.
5. **Does the loop guarantee a correct summary?** No. It only guarantees the word-count rule. Run 1 passed with 18,426 words of repetition.

Also: an output limit is itself a resource budget (slide 10).

---

## Demo 2 - State machine (`demo_2 2.py`)

States: `START -> GENERATE -> VALIDATE -> FAILURE -> DONE`. The summary had **38 words** (minimum 40), so validation failed, although the content was accurate. With no retry configured, the machine ends in DONE and discards a nearly correct result.

---

## Demo 3 - Validation-retry loop (`demo_3 2.py`)

| Attempt | Words | Result |
|---|---|---|
| 1 | 39 | Fail |
| 2 | 35 | Fail (shorter after feedback) |
| 3 | 35 | Fail (identical to attempt 2) |

Stopped with "FAILED: maximum of 3 attempts reached. The last output must not be treated as validated." The feedback did not help, because models count words poorly, and attempt 3 repeated the same output (a loop should detect no progress and stop early). All three summaries were accurate. A better design asks for something the model can follow (for example a number of sentences) or accepts a range.

---

## Demo 4 - Generate, critique, revise (`demo_4 1.py`)

The draft was accurate. The critique had 3 incorrect points out of 4: it called the cause "an omitted fact" (the claim gives no cause, and the draft already listed it as missing), said the extent of damage and repair cost were "not identified" (they were), and said the draft "implies a claim for coverage" (it did not). The revision did not follow the wrong critique and kept the supported facts, mostly reformatting the draft ("cause is unknown" is a slight wording drift). Extra calls gave almost no improvement here. A critique can be wrong (slide 26); prefer deterministic checks (slide 7).

**`Prompt_3` test** (draft: "all required documents submitted, claim should be approved"; source: photographs provided, no repair estimate):

| Criterion | Model said | Correct? |
|---|---|---|
| 1 Facts follow from input | Treated the source's sentences as draft statements; never flagged "all required documents" | Wrong |
| 2 Invents information | Said the draft assumes no estimate was supplied | Wrong (missed the real invention) |
| 3 Unauthorized decision | Yes | Correct |
| 4 Corrections | Remove photographs, reword estimate, remove approval, suggest review | Mostly wrong (deleting a true fact), but removing the approval is right |

Only 1 of 4 criteria was right. A loop following this critique blindly would delete a true fact and keep a false one.

---

## Demo 5 - Evaluator-optimizer (`demo_5 1.py`)

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Real word count | 30 | 42 |
| Evaluator's word_count | 39 | 56 |
| Evaluator `passed` | true | true |
| Code check (40 to 80) | Failed | Passed |

The evaluator miscounted both times, and in attempt 1 said `passed: true` for a number (39) below its own minimum. The independent check in code rejected attempt 1 and the loop retried. Attempt 2 added editorial phrases ("crucial piece of evidence") but the evaluator reported no unsupported claims. Acceptance is not proof of correctness. Machine-checkable rules belong in code.

---

## Demo 6 - Plan-execute-observe (`demo_6 1.py`)

Actions: `extract_facts`, `identify_missing_information`, `identify_missing_information` (repeated), `classify_claim`, then finished. The repeat overwrote the missing-information list (7 items became 5 with different wording, from an identical prompt). The loop is limited by `MAX_STEPS = 4` and a completion check; it finished exactly on step 4. One more repeat would have exhausted the budget before classification, so duplicate-action detection is advisable. The classification added an unsupported phrase ("seeking compensation"). The model only chose from a fixed action list and the code executed it.

---

## Demo 7 - Budgets (`demo_7 1.py`)

Call 1: 34 words (rejected, feedback sent). Call 2: 71 words (accepted). Calls made: 2 of 3. Elapsed: 29.54 s of 90 s. Termination reason: validation succeeded. The feedback worked because the prompt asked for a range (40 to 80) and the feedback stated the count. The accepted summary still contained unsupported statements ("seeking compensation", "a decision on coverage ... will be made").

---

## Demo 8 - Retry with backoff (`demo_8 1.py`)

Attempt 1 failed (wait 0.66 s), attempt 2 failed (wait 1.20 s), attempt 3 succeeded. Delay = 0.5 x 2^(attempt-1) plus 0 to 0.2 s jitter, capped at 4 s; budget `MAX_ATTEMPTS = 4`.

Retry: network timeout (bounded), rate limit (with backoff). Do not retry: invalid input, unauthorized action, model unavailable or misconfigured. Schema violations get a bounded repair or controlled failure. Format retries do not fix wrong content. For operations with side effects, retries can duplicate the action (idempotency, human approval).

---

## Demo 9 - Observability (`demo_9.py`, `demo24_events.jsonl`)

Report: status success, 1 call, 44 words, total latency 12.15 s (includes model load). The log has `run_started`, `model_call_completed` and `run_finished` events with timestamps, attempt, latency, word count and validation result, so it shows what happened and why it stopped. On errors it logs only the error type, not the claim text, to avoid exposing sensitive information.
