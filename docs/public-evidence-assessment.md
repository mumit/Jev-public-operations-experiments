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

Results will show each application's per-question accuracy, all-four card accuracy, composed decisions, displayed false support, correct change-support coverage, paired fixes and losses, and repeated choices. Tied maximum metrics have multiple acceptable references. Failed and missing answers remain in the denominators.

The predeclared calculated-input check requires complete successful execution, at least 90% accuracy for every question in every round in each application, zero false displayed change-support, at least half of reference change-supported cards displayed correctly per round, and no lower all-four accuracy than observations. These are descriptive diagnostic criteria. Passing does not unlock any protected panel.

## Protected data and next step

This study downloads no new telemetry. The 22 RE3 evaluation cases, nine remaining RE3 reserves, RE3 Sock Shop and all 140 RE1 reserves remain unopened. None becomes a test set for this task automatically.

A successful diagnostic would justify a separate fresh evidence-assessment protocol under the same reference definition. Failure would identify which bounded judgments need attention before another cause-selection experiment. Either result must stay separate from analyst usefulness, root-cause accuracy and operational reliability.
