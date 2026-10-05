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
