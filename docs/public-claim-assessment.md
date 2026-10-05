# Can Jev judge a written claim against telemetry?

This diagnostic tests a narrower task than cause selection: does the supplied evidence support a written statement, contradict it, or leave it unanswerable? The previous study exposed numerical reading errors. Here, code can make the arithmetic explicit while Jev matches a statement to the resulting facts.

## Data and references

The study reuses 32 service cards from 16 inspected public RCAEval recordings: ten Train Ticket and six Online Boutique recordings. Each card has three constructed statements, one per verdict. A deterministic hash selects a decidable proposition and its opposite, then an unanswerable proposition, and shuffles their positions. This balance stays out of the requests.

Statements cover metric magnitude, signed direction, duration change and recorded span counts. Unanswerable statements include insufficient measurements, service health and incident causality. For example, a socket change of −3 with both missing fractions at 20% supports “The socket metric meets the material-change policy” and contradicts its opposite. At 21% missing, either statement becomes unanswerable under the declared policy. A missing trace mapping supplies no count; an explicitly recorded zero supplies a count. Neither proves health or cause.

A separate evaluator calculates references from typed propositions and original observations. It is exact by construction, not a parser for unrestricted reports. The earlier fitted ML predicts an originating service and cannot be scored against this different target. No new ML model is trained.

These are authored test statements: fixed templates applied to public measurements. They are not authentic incident reports, specialist-reviewed judgments or held-out incidents. Opposite statements, repeated cards and repeated rounds remain correlated. Balanced templates can create shortcuts that real reports do not offer.

## The input comparison

Both inputs receive identical statements and policy definitions. Each of three independent Choice questions asks for one verdict; the questions cannot see one another’s replies.

- **Observations:** original metrics, missing fractions, spans and durations for one service.
- **Fact ledger:** the same original measurements, with metric eligibility, absolute scaled changes and eligible duration arithmetic made explicit. It retains trace observations and missing values. It contains no claim-specific verdict, injected answer or material/quiet classification.

For an eligible signed change of −3, the ledger adds `absolute_scaled_change: 3` and `eligible_for_change_policy: true`. For duration 100 → 75 microseconds with five spans in each window, it adds `relative_change: -0.25`. With four ending spans, eligibility becomes false and the calculated change remains null. This lets code handle arithmetic while Jev handles the written claim.

## Frozen diagnostic checks

The plan precedes preparation; a committed protocol fixes every request before inference. Three rounds compare both inputs: 192 calls and 576 individual answers. Calls run serially without retries or warmup.

The ledger is the predeclared candidate. Each application and round must reach 90% accuracy for every reference class, display no false supported statement, display at least half of supported references correctly, and match or exceed observations-only total accuracy. All calls must succeed. A selected-answer probability of at least 0.70 controls display; it is an inherited diagnostic boundary, not calibrated reliability.

Passing these author-set checks does not open protected data or establish operational fitness. All 22 RE3 evaluation cases, nine remaining RE3 reserves, RE3 Sock Shop and 140 RE1 reserves stay unopened. The completed comparison passes these checks; the next experiment still needs its own protocol.


## Results

All 192 calls succeeded, returning 576 valid answers. The largest request contains 7,768 bytes; the largest recorded input uses 2,295 tokens.

| Application and input | Correct verdicts, rounds 1 / 2 / 3 | Correct displayed support | False displayed support | Withheld verdicts |
|---|---|---|---|---|
| Train Ticket, observations | 58 / 58 / 58 of 60 | 19 / 18 / 18 of 20 | 1 / 1 / 1 | 2 / 3 / 3 |
| Train Ticket, ledger | 60 / 60 / 60 of 60 | 20 / 19 / 20 of 20 | 0 / 0 / 0 | 1 / 2 / 1 |
| Online Boutique, observations | 33 / 33 / 33 of 36 | 10 / 10 / 10 of 12 | 0 / 0 / 0 | 4 / 4 / 5 |
| Online Boutique, ledger | 36 / 36 / 36 of 36 | 11 / 11 / 11 of 12 | 0 / 0 / 0 | 3 / 3 / 3 |

The ledger fixes the same five statements in all three rounds and loses none. Every supported, contradicted and unanswerable verdict is correct in every ledger round. All ledger verdicts that cross the display boundary are also correct. Perfect verdict accuracy does not mean every correct answer is displayed: low probabilities still withhold some answers, and Train Ticket display decisions vary by round.

Original observations answer every unanswerable statement correctly. Their errors occur on three service cards, including two matched opposite pairs. That gives five failing statements, not five independent incidents.

## Follow the actual fixes

**Train Ticket, ts-admin-basic-info-service, CLA-aa0b53fdc937.** Uncovered median duration changes from 3,661 to 2,785 microseconds, with 719 before spans and 453 after spans. The decrease is 23.93%, below the 25% material-change boundary. Observations wrongly support the material-change statement at 0.90 / 0.88 / 0.90, and wrongly contradict its opposite. The ledger adds `relative_change: -0.23927888555039606` and marks duration eligibility true. Both verdicts become correct in every round. The supported negative statement remains withheld in round two at 0.68, despite being correct.

**Online Boutique, recommendationservice, CLA-48bd90609b81.** Uncovered median duration changes from 2,388 to 1,644.5 microseconds, with 5,346 and 5,410 spans. The 31.13% decrease meets the material-change boundary. Observations contradict the statement in every round; probabilities of 0.71 and 0.74 display the wrong verdict in the first two rounds. These are false contradictions, which the false-supported count alone would miss. The ledger adds `relative_change: -0.31134840871021774`; Jev supports the claim at 0.97 / 0.96 / 0.98.

**Online Boutique, adservice, CLA-796faa18afa8.** Memory's scaled change is −0.88630394; the ending missing fraction is 0.14008322. The eligible magnitude stays below three, although the raw medians fall sharply. The ledger adds `absolute_scaled_change: 0.88630394` and eligibility true. Jev correctly contradicts the material-change statement and supports its opposite in every round. Both corrected answers remain below 0.70. The same card's latency-90 change exceeds 600 but has 55.48% ending missingness: its threshold statement stays unanswerable. The ledger does not turn incomplete evidence into a decisive answer.

## What the result means

This supports a specific architecture for further testing: calculate numerical facts and eligibility in code, then ask Jev a bounded question about a written claim. The observed gains fit that architecture, but the comparison changes both representation and derived fields. It cannot attribute the gain to one particular field or establish the model's internal reasoning.

The result does not establish added value over a parser that recognizes these fixed templates. Nor does it show reliable handling of paraphrases, mixed statements, ambiguous wording or real incident reports. All 96 claims come from already inspected telemetry, and the chosen templates include no decidable span-adequacy pair. Neither result can be called held-out generalization.

## Next experiment

The next diagnostic will test meaning-preserving paraphrases and difficult distinctions on these same facts before spending untouched telemetry. Keep the ledger and verdict policy fixed. Independently write and review alternative claims, include negation and absent-versus-zero observations, and remove the one-of-each-class balance from the card construction. Preserve references at the proposition level, so wording changes cannot silently change the answer.

That diagnostic needs a separately committed language protocol and call budget. Any later fresh-telemetry confirmation needs a new allocation and frozen evaluation plan. Protected recordings remain unopened. Inspect this study at [the claim explorer](http://127.0.0.1:8769/claim-assessment); browsing uses recorded responses only.
