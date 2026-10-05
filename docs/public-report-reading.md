# Can Jev judge several claims in a short report?

The wording diagnostic preserved correct verdicts across explicit paraphrases and negation. This experiment tests whether Jev can locate and judge six claims about two named services in one short report.

## Setup

Six independently scored sentences form each of 16 reports. Both services come from the same previously inspected recording. Three propositions per service are selected by a fixed hash from the earlier catalogue, without using their reference verdict. Every sentence explicitly names its service; field positions are shuffled. The direct paraphrase supplies the sentence text.

The atomic control puts each sentence in its question. The report arm places all six numbered sentences in the input and asks each question to judge its assigned sentence. Both receive the same two-service fact ledger, numerical policy, Choice criteria and display boundary. This isolates the presentation and lookup task while keeping multi-service context fixed.

The frozen evaluator judges each typed proposition against its own service observations. A report is correct only when all six verdicts match their references. Complete display requires all six probabilities to meet the inherited 0.70 boundary. This boundary is uncalibrated for the task.

Three rounds permit 96 serial calls and 576 answers. The committed plan precedes preparation; exact requests freeze before inference. No retries, warmup or fresh telemetry access are permitted.

## Diagnostic criteria

In each application and round, the report arm must reach 90% accuracy in every reference class, display no wrong verdict, correctly display at least half the supported claims, match the atomic control’s correct count and give all six correct verdicts on at least 90% of reports. Both arms must complete successfully. Atomic errors remain visible.

## Limits

These are authored, numbered assertions on controlled application telemetry, not authentic analyst notes. Explicit service names avoid unresolved pronouns. The experiment does not test extracting implicit claims, conflicting narratives, operational causality, specialist policy or telecom readiness. Claims, services and rounds are correlated. Prior ML predicts incident origin and does not answer this task; the typed reference evaluator does not parse unrestricted text.

All 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves remain unopened. Passing these checks opens none of them.

## Results

All 96 calls succeed and return 576 valid answers. The largest request contains 15,693 bytes; recorded input usage peaks at 4,108 tokens. Direct atomic judgments are correct throughout. Report reading makes the same two errors in every round, one per application. Both application checks fail.

| Application and presentation | Correct claims, rounds 1 / 2 / 3 | All-six reports correct | Displayed correct | Wrong displayed | Correct displayed support | Complete report display |
|---|---|---|---|---|---|---|
| Train Ticket, direct | 60 / 60 / 60 of 60 | 10 / 10 / 10 of 10 | 60 / 60 / 60 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 10 / 10 / 10 of 10 |
| Train Ticket, report | 59 / 59 / 59 of 60 | 9 / 9 / 9 of 10 | 58 / 58 / 59 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 8 / 8 / 9 of 10 |
| Online Boutique, direct | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 36 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 6 / 6 / 6 of 6 |
| Online Boutique, report | 35 / 35 / 35 of 36 | 5 / 5 / 5 of 6 | 33 / 33 / 33 | 0 / 0 / 0 | 10 / 10 / 10 of 11 | 4 / 4 / 4 of 6 |

Train Ticket has 18 supported, 20 contradicted and 22 unanswerable claims. Online Boutique has 11, 12 and 13. Each class clears the 90% claim-accuracy requirement, but both applications lose a correct judgment against the fresh direct control. Online Boutique also falls below 90% whole-report correctness: five of six reports, or 83.3%. Train Ticket reaches nine of ten, exactly 90%.

Both erroneous report verdicts stay below 0.70 in all rounds. No wrong verdict is displayed. All report verdicts are stable across rounds, including the errors; one Train Ticket claim changes its display decision. Atomic verdicts and display decisions stay stable throughout. Complete display does not guarantee completeness of understanding: a withheld claim still needs review.

## Inspect the two repeated errors

**Report reading falsely supports positive change at an eligible zero.** RPT-5e9c57b96fdc contains assertions about ts-preserve-other-mongo and ts-route-mongo. Its sixth sentence reads:

> For service ts-preserve-other-mongo: The eligible signed change for socket is greater than zero.

The correct service’s ledger records socket medians of two in both windows, zero missingness and a signed change of zero. The verdict is contradicted. Direct questions select contradicted at 0.90 / 0.92 / 0.85. Report questions select supported at 0.64 / 0.63 / 0.46 and withhold it. The last response assigns 0.46 to both supported and contradicted; the recorded selected verdict remains supported.

**Report reading supports an ineligible positive-change claim.** RPT-ddcba9332c6e contains assertions about adservice and redis. Its fourth sentence reads:

> For service adservice: The eligible signed change for mem is greater than zero.

Adservice’s signed memory change is 0.038857363, but the after-window missing fraction is 39.53%, above the fixed 20% maximum. The claim is unanswerable under the declared policy. Direct questions select unanswerable at 0.96 / 0.97 / 0.98. Report questions select supported at 0.50 / 0.47 / 0.48 and withhold it.

The input changes concretely. A direct question ends with the full sentence after “Statement:”. The corresponding report question instead ends with “Assess only sentence 6” or “Assess only sentence 4” and a service-scope instruction. The sentence moves into the state’s numbered report. Both arms retain identical two-service ledgers, numerical instructions and verdict criteria. The comparison identifies a loss when Jev must locate the claim in the report; it cannot show whether the internal failure concerns lookup, service binding or applying the numerical policy. No reasoning trace was requested or inferred.

## What this means for operations

The result supports direct, explicitly scoped claim questions on this inspected panel. Passing from isolated phrasing to a report lookup introduces repeatable errors despite unchanged facts. Withholding catches these two errors at the inherited boundary, but that boundary has not been calibrated for real notes or new incidents.

Keep arithmetic and eligibility in code. A practical candidate is to bind each report claim to its sentence text and service before asking Jev to judge it. The application can preserve the original report for analyst inspection while supplying a direct claim question. This result does not prove that a parser can reliably extract claims from unrestricted notes or that Jev adds value beyond templates.

## Next experiment

Test explicit claim binding while retaining the report as context. Compare the current numbered lookup with a question containing both a stable claim ID and its exact sentence, and with the same sentence plus an explicitly scoped service ledger. Freeze all three inputs, references and budget before calls. Report each step separately so a wording change and removal of other-service evidence do not get conflated.

The existing direct control already answers every selected claim correctly with both ledgers. That makes binding a useful next diagnostic; it does not justify retuning against protected cases. Subsequent generalization still needs a separate fresh-data allocation and evaluation protocol. Inspect [the report explorer](http://127.0.0.1:8769/report-reading) for the six sentences, their service facts, actual responses and exact requests.

The explicit-binding comparison is now complete. Bound questions fix both repeated errors; one-question grouping introduces an isolated regression, and scoped facts correct it. The overall sequence fails while binding and scope pass separate checks. See [the binding study](public-claim-binding.md) for exact input changes and limits.
