# Does claim checking survive different wording?

The fact ledger answered all 96 fixed-template claims correctly in the previous diagnostic. This study keeps the ledger and verdict policy unchanged while asking whether different wording preserves that result.

## What changed

Each request now contains three ways of stating one proposition: the original wording, a direct paraphrase and an alternative phrasing. Numerical alternatives use negation such as “not below three,” “not at least 25%” and “neither zero nor negative.” Health and causal claims use active or passive rephrasing without assuming that “not unhealthy” means “healthy.” All three questions share the same facts and reference, with their field positions shuffled.

The old one-of-each-verdict pattern disappears. The request contains neither that balance nor the names of the wording variants. Jev receives the same independent Choice instructions and criteria as before. The new original-wording response is the control; earlier responses remain separate because the request grouping and proposition mix have changed.

## Measurements and references

The study reuses all 32 inspected service cards from 16 public recordings. Its 152 propositions comprise:

- All 96 earlier typed propositions.
- One claim about recorded span counts per card, adding 32 propositions.
- One eligible measured-zero direction claim on each qualifying card, adding 24 propositions. Source measurements remain unchanged.

For example, an eligible signed change of zero makes “not greater than zero” supported and “greater than zero” contradicted. A missing trace mapping supplies no count, so a claim that both windows record at least five spans is unanswerable. A supplied count below five contradicts that claim. No observed trace card has a recorded zero count; zero tests here use actual metric changes, not invented spans.

The frozen typed-proposition evaluator supplies references. A single reference applies to all three wordings. Claims are authored templates checked against the proposition before inference, not genuine analyst reports or specialist-reviewed judgments. Three wordings and three rounds do not create nine independent examples. The selected service cards and opposite propositions also remain correlated.

## Frozen diagnostic checks

A committed plan precedes preparation; the exact-request protocol precedes inference. Three rounds permit 456 calls and 1,368 answers. Requests run serially, without retries or warmup.

For each application and round, both alternative wordings must reach 90% accuracy for every reference class, display no wrong verdict of any class, correctly display at least half the supported references, and match or exceed the fresh original-wording control's correct count. All calls must succeed. The inherited display boundary remains 0.70 and is not calibrated reliability. Original-wording errors stay visible even if the alternatives pass.

Results separate the earlier propositions, recorded-count claims and actual-zero claims. Wrong support, wrong contradiction, unknown-to-decisive answers and changes across wordings remain visible. Earlier ML predicts incident origin and is unscored for this task. The reference evaluator is exact by construction; it does not parse unrestricted text.

No fresh telemetry is downloaded. All 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves remain unopened. This is a language diagnostic on inspected evidence, not fresh generalization or operational validation.


## Results

All 456 calls succeed, returning 1,368 valid answers. The largest request contains 7,830 bytes; the largest recorded input uses 2,315 tokens. Both alternative wordings pass every frozen check in both applications.

| Application and wording | Correct verdicts, rounds 1 / 2 / 3 | Displayed verdicts, all correct | Correct displayed support | Withheld verdicts |
|---|---|---|---|---|
| Train Ticket, original | 93 / 93 / 93 of 93 | 91 / 93 / 91 | 28 / 28 / 28 of 28 | 2 / 0 / 2 |
| Train Ticket, direct paraphrase | 93 / 93 / 93 of 93 | 93 / 93 / 93 | 28 / 28 / 28 of 28 | 0 / 0 / 0 |
| Train Ticket, alternative | 93 / 93 / 93 of 93 | 93 / 92 / 93 | 28 / 28 / 28 of 28 | 0 / 1 / 0 |
| Online Boutique, original | 59 / 59 / 59 of 59 | 56 / 57 / 56 | 17 / 17 / 17 of 18 | 3 / 2 / 3 |
| Online Boutique, direct paraphrase | 59 / 59 / 59 of 59 | 58 / 58 / 58 | 18 / 18 / 18 of 18 | 1 / 1 / 1 |
| Online Boutique, alternative | 59 / 59 / 59 of 59 | 59 / 58 / 58 | 18 / 18 / 18 of 18 | 0 / 1 / 1 |

Every reference class and every data stratum is correct throughout. Train Ticket has 28 supported, 30 contradicted and 35 unanswerable propositions; Online Boutique has 18, 20 and 21. All 32 recorded-count claims and 24 measured-zero claims receive correct verdicts under all wordings and rounds. No unknown reference becomes a decisive answer.

All wordings agree on each verdict, so there are no accuracy fixes or regressions against the fresh control. Wording changes probabilities and withholding. The original wording withholds twelve correct verdicts across both applications and three rounds; direct and alternative phrasing each withhold three. Every displayed verdict is correct, including contradictions and unknowns. Display consistency still varies, and probabilities remain uncalibrated.

## What the actual input changes show

**A policy label versus an explicit comparison.** For Online Boutique adservice, memory's eligible absolute scaled change is 0.88630394. CLL-ac0f839a7407 compares these equivalent statements:

- Original: “The mem metric does not meet the material-change policy.”
- Direct: “Under the declared eligibility policy, the absolute scaled change of mem is less than 3.”
- Alternative: “Under the declared eligibility policy, the magnitude of the mem signed change is not at least three.”

All answers are supported. The original wording receives 0.59 / 0.58 / 0.51 and stays withheld; the direct wording receives 0.85 / 0.95 / 0.98 and the alternative receives 0.97 / 0.96 / 0.93. Both alternatives display in every round. The ledger and numerical rule are identical. An explicit comparator is a useful wording candidate here; the experiment does not explain the model's internal reasoning or prove that higher probability means greater reliability.

**Negation near a numerical boundary.** For Train Ticket ts-admin-basic-info-service, CLL-022b700dac53, the ledger records a −23.93% uncovered-median duration change. “Meets the material duration-change policy,” “at least 25% in absolute relative magnitude” and “not below 25%” are contradicted in every round. Decreases count toward magnitude; this one remains below the inclusive boundary. The earlier arithmetic-reading failure does not return with these wordings.

**Unknown counts versus an observed count.** Emailservice, CLL-76e05248ecd9, records 140 before spans and four after spans. “Neither recorded window count is below five” is contradicted, along with its other two wordings. On cards with no mapped trace, both positive and negative count assertions remain unanswerable. Absence does not become a fabricated count of zero.

**A real measured zero.** Train Ticket ts-preserve-other-mongo, CLL-b09f8317ec8c, has socket medians of two in both windows, zero scaled change and zero missingness. “Not positive,” “zero or negative” and “not greater than zero” are supported in every round. An observed zero remains a usable number. Recorded-zero span behavior is covered by unit checks only; no hosted trace card supplies that condition.

## What this establishes

The bounded claim task survives these specific paraphrases and numerical negations without verdict regressions. Explicit comparison wording also improves displayed coverage on this panel. This strengthens the case for keeping numerical calculations in code and using Jev for a clearly scoped written judgment.

It does not establish unrestricted report understanding, fresh-incident generalization or added value over a parser for these templates. The variants remain deliberately equivalent and explicit, share a ledger, and come from controlled application faults. They do not cover mixed reports, implicit service references, conflicting statements or specialist operational policy. No untouched data was consumed.

## Next experiment

The next useful diagnostic is a short report containing several independently scored claims and more than one service. Keep the numerical ledger and verdict definitions fixed, identify each claim's service explicitly, and distinguish a correct atomic judgment from a correct whole report. Freeze the text, references, display rule and budget before calls. This would test a report-reading task while preserving the numerical findings above.

A later fresh-telemetry confirmation requires its own allocation and frozen evaluation plan. Passing this diagnostic opens none of the protected recordings. Inspect [the wording explorer](http://127.0.0.1:8769/claim-language) to compare actual statements, references and responses.

The short-report diagnostic is now complete. Direct questions retain correct judgments, while numbered report lookup repeats two withheld errors. See [the report-reading study](public-report-reading.md) for the exact input change and the separate claim-binding experiment to try next.
