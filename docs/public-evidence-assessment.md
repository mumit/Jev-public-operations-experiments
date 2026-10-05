# Assess the evidence before inferring a cause

I selected a narrower task after the trace-aware diagnosis comparison failed development. This study asks Jev to classify observable changes and coverage for one service at a time. Code combines those answers into an investigation-support indicator. It does not ask which service caused the incident.

## Reference rules

| Question | Numerical reference |
| --- | --- |
| Material metric change | At least one eligible metric has absolute scaled `signed_change` >=3.0. A metric is eligible when its change is numeric and both missing fractions are between zero and 0.20 inclusive. |
| Material duration change | At least one eligible median/p90 inclusive or uncovered duration changes by at least 25% in either direction. Eligibility requires a numeric positive starting duration, a numeric ending duration and at least five recorded spans in each window. |
| Trace coverage | Adequate: at least five spans in each window. Absent: no spans in either window, or no mapped trace. Limited: some spans exist but a window has fewer than five. |
| Strongest metric channel | The eligible metric with greatest absolute scaled change. Any tied maximum is acceptable. No eligible metric is a separate option. |

Metric and duration questions return material, quiet or unknown. Quiet means eligible observations exist and fall below the stated boundary. Unknown means none are eligible. An increase and a decrease can both be material. Five spans do not prove complete instrumentation or statistical significance. Uncovered duration is not CPU time or proof of a local cause.

These thresholds are author-defined research rules. “Material” means crossing this policy, not a specialist assessment of operational significance. The reference calculator reads the supplied observations directly. Published injected-service labels do not enter selection, requests or scoring. A program answers this task exactly; the rule control is correct by construction. The study tests whether Jev applies the policy and identifies the supporting metric, not whether Jev improves on rules.

## Questions and composition

Each call asks the four independent Choice questions. Their instructions define eligibility and boundaries explicitly. Questions in one call share the observations but do not see one another's answers, as described in the [official TypeSafe documentation](https://docs.typesafe.ai/introduction), checked on 2026-10-04.

Code assigns change-supported when either change answer is material. With no material answer, an unknown change answer produces evidence-limited; two quiet answers produce no-material-change. A missing or failed answer produces unavailable. Change-supported means the stated policy supports investigating an observed change. It does not identify its origin, severity or relation to the affected service.

The inherited 0.70 boundary displays the composed indicator only when both metric and duration answer probabilities meet it. This is a fixed diagnostic display choice, not a calibrated policy for the new task. Scoring retains withheld correct answers, incorrect answers and false displayed change-support. Missing coverage can produce a confidently answered unknown option; confidence in that classification does not fill the gap.

## Diagnostic data and comparison

The comparison reuses the 16 already inspected trace-task development recordings: ten Train Ticket and six Online Boutique cases. It selects two service cards per recording using observations only. One has the largest eligible metric/duration change. The second comes from candidates without mapped traces when available; otherwise it has the smallest eligible change. Stable hashes break ties. This deliberately selected set exercises strong changes and missing evidence. It does not estimate their frequency in operations.

The 32 cards remain correlated within their recordings and service/fault groups. Repeated rounds do not create independent cases. These are controlled public application code faults with supplied incident intervals. They are not telecom reports or fresh held-out evidence.

Two matched inputs contain identical single-service observations and questions. Observations supplies the original named metric summaries, span counts, duration values and elapsed window lengths. Calculated adds explicit relative duration and normalized recorded-span-rate changes from those same observations. It adds no classification, answer key, learned parameter or injected label. Rates correct window length only; duration classification ignores rates and status codes.

The frozen fitted ML control remains available in the earlier diagnosis inspector. It predicts the injected originating service, a different target. Scoring it against these per-service evidence classes would be invalid; this study fits no ML model and selects no ML shortlist.

## Execution and research checks

The plan freezes source bytes and prerequisite evidence before preparation. Exact request fingerprints freeze before hosted calls. Jev 1.13.0, its endpoint and declared 32,768-token context stay fixed. The budget is 192 calls: 32 cards, two inputs, three serial cyclic rounds, without retries or warmup. Every call contains four questions, giving 768 planned answers. HTTP, network, model-version or context errors stop execution; three consecutive malformed replies also stop it.

Results show each application's per-question accuracy, all-four card accuracy, composed decisions, displayed false support, correct change-support coverage, paired fixes and losses, and repeated choices. Tied maximum metrics have multiple acceptable references. Failed and missing answers remain in the denominators.

The predeclared calculated-input check requires complete successful execution, at least 90% accuracy for every question in every round in each application, zero false displayed change-support, at least half of reference change-supported cards displayed correctly per round, and no lower all-four accuracy than observations. These are descriptive diagnostic criteria. Passing does not unlock any protected panel.

## Protected data and next step

This study downloads no new telemetry. The 22 RE3 evaluation cases, nine remaining RE3 reserves, RE3 Sock Shop and all 140 RE1 reserves remain unopened. None becomes a test set for this task automatically.

The calculated-input diagnostic failed overall. The observations-only result is promising, but substituting it after inspection would violate this protocol. Fresh verification of that input requires a separate plan. These results remain separate from analyst usefulness, root-cause accuracy and operational reliability.

## Results

All 192 calls completed successfully, recording 768 answers. The largest request was 6,863 bytes; input tokens peaked at 2,109. Each sequence lists rounds one, two and three. Every question uses the full 20-card Train Ticket or 12-card Online Boutique denominator, including unknown references.

| Application | Input | Metric change | Duration change | Trace coverage | Strongest metric | All four correct |
| --- | --- | --- | --- | --- | --- | --- |
| Train Ticket (20 cards) | Observations | 20 / 20 / 20 | 20 / 20 / 20 | 20 / 20 / 20 | 20 / 20 / 20 | 20 / 20 / 20 |
| Train Ticket | Calculated | 19 / 20 / 19 | 20 / 20 / 20 | 20 / 20 / 20 | 20 / 20 / 20 | 19 / 20 / 19 |
| Online Boutique (12 cards) | Observations | 11 / 10 / 11 | 12 / 12 / 12 | 12 / 12 / 12 | 12 / 11 / 11 | 11 / 9 / 10 |
| Online Boutique | Calculated | 12 / 12 / 12 | 12 / 12 / 12 | 12 / 12 / 12 | 11 / 11 / 11 | 11 / 11 / 11 |

| Application | Input | Correct displayed change-support | Reference change-supported cards | False displayed change-support | Withheld indicators |
| --- | --- | --- | --- | --- | --- |
| Train Ticket | Observations | 10 / 10 / 10 | 10 | 0 / 0 / 0 | 0 / 0 / 0 |
| Train Ticket | Calculated | 8 / 9 / 9 | 10 | 0 / 0 / 0 | 2 / 1 / 1 |
| Online Boutique | Observations | 2 / 2 / 3 | 5 | 0 / 0 / 0 | 4 / 4 / 3 |
| Online Boutique | Calculated | 4 / 3 / 4 | 5 | 0 / 0 / 0 | 1 / 2 / 1 |

The indicator also displays correctly classified evidence-limited and no-material-change cards. Correct displayed change-support counts only the cards whose reference supports investigating a change; withholding includes all indicator classes.

The calculated input passes Online Boutique's checks and fails Train Ticket's because it lowers all-four accuracy relative to observations in rounds one and three. Both arms classify duration changes and trace coverage correctly on every card in every round. All 32 cards have at least one eligible metric, so metric-unknown has no model test opportunity here. Trace references include six material, one quiet and 25 unknown cards; 24 have absent coverage, one has limited coverage and seven have adequate counts. High trace agreement therefore mostly tests the unknown branch. Online Boutique has one three-round all-four fix and no repeated loss; Train Ticket has neither. The overall check fails, so no fresh panel opens.

## Inspect the remaining disagreements

In [EVA-4b122fec2849](http://127.0.0.1:8769/evidence-assessment?dataset=Train+Ticket&card=EVA-4b122fec2849&arm=calculated&round=1&field=metric_change#inspect), ts-route-mongo has eligible socket scaled change −16.666667, above the absolute 3.0 boundary. Observations returns material in every round. With added trace arithmetic, Jev returns quiet in rounds one and three at 0.63 and 0.53. Neither incorrect indicator is displayed. The request preserves the socket observation and the question explicitly counts negative changes. The result shows a failure to apply that rule; it does not establish why adding trace fields changed the answer.

For [EVA-12e6912919dd](http://127.0.0.1:8769/evidence-assessment?dataset=Online+Boutique&card=EVA-12e6912919dd&arm=observations&round=1&field=metric_change#evidence), redis has eligible magnitudes 0.0368, zero, 1.0 and zero. The reference is quiet. Observations selects material in all three rounds, at 0.62, 0.53 and 0.58; the fixed boundary withholds all three incorrect support indicators. Calculated selects quiet in every round and fixes all four answers for this card. The added arithmetic covers traces, not these metric values, so this is an observed paired fix rather than evidence that a metric transformation caused it.

In [EVA-39ff3f617b7a](http://127.0.0.1:8769/evidence-assessment?dataset=Online+Boutique&card=EVA-39ff3f617b7a&arm=calculated&round=2&field=metric_channel#evidence), emailservice's eligible socket magnitude is 100, versus memory at 85.889116 and workload at 0.555. Its larger latency changes are ineligible because their missing fraction is 85.3%. The strongest eligible channel is socket. Calculated selects memory in every round; observations selects memory in rounds two and three. This error does not change the composed support indicator, but it gives the wrong supporting metric. Numerical comparisons should stay in code.

## What this says about Jev

Jev agrees with these explicit local evidence rules much more often than it matched injected causes in the preceding study. The targets, context and questions changed together, so the scores are not a paired improvement in root-cause diagnosis. The comparison does show that Jev can answer some bounded evidence questions correctly on these selected examples, including absent traces and insufficient samples.

Observations alone is perfect on these Train Ticket cards, while calculated changes help Online Boutique's material-change classification and displayed support. Arithmetic is not a uniform improvement. The strongest-channel error also survives the added calculations. Treat these as concrete task boundaries, not evidence that probabilities are calibrated or that a model adds value over deterministic rules.

My recommendation is to keep numerical eligibility, change thresholds and strongest-channel selection in code. Jev's next useful test should involve a judgment those rules cannot answer. Alternatively, a new protocol can verify the observations-only diagnostic on fresh public cases under the same numerical policy. That would test generalization, but still would not demonstrate analyst benefit or better fault diagnosis. This choice precedes any new telemetry access.

## Inspect and reproduce

The [evidence-assessment inspector](http://127.0.0.1:8769/evidence-assessment) exposes each question's distribution, all three repeated indicators, hidden/revealed numerical references, eligibility calculations, source observations, added arithmetic and exact requests. Browsing makes no calls.

Restore the eight [public evidence bundles](evidence.md), then run `python -m scripts.verify_public_evidence` with pinned dependencies. The supplement contains only the 32-card preparation and new hosted records. It requires the seven earlier assets; raw telemetry stays in those immutable releases. Verification reconstructs every card, question, numerical reference and outcome without inference. All 22 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves remain unopened.
