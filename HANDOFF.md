# Handoff: public operations experiments

## Current state

Two public comparisons, an exact-request replay, a fresh temporal development comparison, selective calibration/evaluation and reserve confirmation are complete and preserved. The standalone app exposes their saved inputs, actual responses, fitted ML controls and references. It remains read-only on loopback port 8769. Browsing and verification make no provider calls and need no API key.

Start with README.md, docs/evidence.md and docs/public-confirmation.md. Restore all four versioned evidence bundles, then run scripts.verify_evidence, scripts.verify_public_diagnostics, scripts.verify_public_selective and scripts.verify_public_confirmation. The suite passes 75 tests. The earlier synthetic studies and their Git history remain in the original repository.

## Recorded findings

The first comparison uses all 90 RCAEval RE2 Online Boutique cases: 30 training, 24 development, 18 calibration and 18 evaluation cases. ML fits only on training. The 18-case held-out results are change ranking 18/18, Jev and trained ML 17/18, and resource ranking 14/18. Jev's frozen 0.50 threshold displays its error.

The input-format comparison records 234 calls. Fresh Sock Shop calibration/evaluation groups provide 18/36 cases; another 36 reserve cases remain undownloaded. Held-out results are compact/named/explained Jev 34/35/34 out of 36, frozen ML transfer 32/36, change ranking 31/36 and resource ranking 26/36. The frozen 0.60/0.50/0.50 thresholds display 2/0/0 observed errors. Named fixes one compact error; explanations lose one named-input success.

The 180-call replay uses 12 inspected cases and five rounds per input. Compact/named/explained choices stay stable on 12/9/11 cases; display decisions stay stable on 11/10/12. Wrong displayed response counts are 7/0/5 out of 60 per input. Named retains all originally correct selections, but two correct choices cross its display threshold. Its predeclared research gate fails. Inspect `/repeatability` and docs/public-repeatability.md.

The offline timing audit preserves latency windows on those inspected cases without new calls. Fresh Train Ticket preparation downloads 18 development cases in six groups, retaining 68 observed services per case. All 72 later Train Ticket cases stay undownloaded. A separate one-call probe accepts the largest temporal request: 79,840 wire bytes and 30,471 input tokens. The byte-bound failure remains recorded as conservative sizing, not a provider rejection.

The 108-call development comparison makes three rounds across named and temporal inputs. Every round gives top-1 correctness of 16/18 and 15/18. Both shortlists include all targets, but named adds 32–34 wrong leads and temporal adds 36 per round. ML transfers unchanged and ranks all 18 targets first; change/resource rank 17/10 first. Temporal causes one repeated regression and no fixes. Inspect `/temporal`, including the unchanged measurements, added windows, repeated responses and local rankings.

These are controlled application faults with supplied incident boundaries and published injected-service references. Repeats are not independent held-out cases. Public pretraining exposure is unknown. The results do not establish an operational error rate, analyst investigation benefit, anomaly detection or telecom readiness.

## Selected direction

The user chose fewer wrong leads, accepting more withholding, on 2026-10-04. Named input remains the candidate. The separate public-selective plan fixes a single-service-or-withhold policy family before any calibration download. A supported two-service alternative is a diagnostic comparator; with one published cause per case it necessarily adds benchmark wrong leads.

The probability threshold and the gap to the strongest competing option, including insufficient_evidence, control display. Calibration considers all three rounds and maximizes useful coverage among policies with zero observed wrong leads in every round. This is an author-set research criterion, not an operational error budget. Correct withheld recommendations remain visible in scoring.

All 54 calibration calls succeeded. The selected rule is probability >=0.70, margin >=0, one lead at most. It shows 11/10/11 correct leads and zero wrong leads; withholds 7/8/7 including 1/3/3 correct first choices. ML transfers at 15/18 on calibration, Jev unfiltered at 12/13/14. The new plan permits 108 evaluation calls. All 108 evaluation calls succeeded on 36 untouched cases in twelve groups. The frozen policy shows 21/19/22 correct leads, zero wrong leads, and withholds 15/17/14 cases including 9/11/8 correct first choices. Display is stable on 33/36 cases. Unfiltered Jev ranks 30/36 first each round; ML/change/resource rank 28/27/25. The policy improves displayed precision by withholding, not model accuracy. See /selective and docs/public-selective.md. Both reserve sets were undownloaded when selective evaluation ended. The user chose fixed-boundary confirmation on untouched reserve cases. The new public-confirmation plan permits 162 calls on 18 Train Ticket and 36 Sock Shop reserve cases, with all results separated by application. Its input and 0.70 policy stay unchanged; there is no fitting or threshold search. Commit the plan before reserve download, then the exact request fingerprints before calls. Recovering coverage with new inputs or ML fallback needs fresh development and calibration.

## Frozen evidence and continuation

Original protocols and active inference sources remain fingerprinted by provenance/migration.json; original source bytes stay under provenance/source. Do not modify or rerun them. Later protocol names begin public-repeat, public-context-probe and public-temporal. Their request plans, source fingerprints and results are committed under checkpoints. Their runners reject another execution. New experiments need separate modules, protocols and output folders.

The original public-study-v1 release contains 294 calls and 347 files. The separate public-diagnostics-v1 asset adds 289 calls and 51 files, including replay evidence, fresh development measurements and the capacity probe. Restore it after the original bundle. The public-selective-v1 asset adds 162 responses and 124 files for calibration and evaluation. The public-confirmation-v1 asset adds 162 responses and 116 files. All four preserve 907 recorded calls. They contain no credentials or synthetic runs and must not be replaced with changed evidence.

The app reveals published case answers explicitly. It exposes comparison results only after complete evidence matches the committed assessment. Keys remain server-side in ignored local configuration. Do not introduce other model providers, download model weights or execute network changes without a new request.


## Completed reserve confirmation

The user selected confirmation, then authorized the separate committed public-confirmation plan. All 162 calls on the final 18 Train Ticket and 36 Sock Shop cases succeeded. Input, model and the 0.70 boundary stayed fixed. No threshold search or refitting occurred.

Train Ticket shows 11/10/11 correct and one wrong lead per round, withholds 6/7/6 including 4/5/4 correct first choices, and has stable display on 15/18 cases. Unfiltered Jev matches 15/18 first, ML 16/18. The persistent error TMP-80d015d089a4 selects admin-travel at about 0.81 instead of the published route-service loss cause; ML chooses route. The earlier zero-error result does not reproduce.

Sock Shop shows 27 correct, zero wrong and nine withheld per round. Unfiltered Jev is correct on all 36 cases; the rule withholds nine correct first choices. All 36 display decisions stay stable. ML/change each match 34 first. Keep both applications separate.

Both reserve panels are now inspected. All 90 Online Boutique, 90 Sock Shop and 90 Train Ticket cases used here have been opened. No later policy may treat these as untouched validation. The app exposes both confirmation panels under /selective, including per-case Jev/ML agreement for inspection; that indicator does not modify the frozen recommendation.

The next experiment requires fresh cases and a new protocol. Recommended direction: test disagreement as a review trigger, with lost correct coverage measured. Alternative: add causal evidence such as traces/dependency context. This next objective needs a user decision; neither direction has been implemented as an inference or display change.
