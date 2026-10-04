# Handoff: public operations experiments

## Current state

Both public comparisons and the exact-request replay are complete and preserved. The standalone extraction passes 58 tests; a fresh GitHub clone restores all 347 release files and recomputes both studies exactly. The repository has a standalone read-only app, pinned preparation and inference code, separate references, recorded checkpoints and a public evidence release. The earlier synthetic studies and Git history remain in their original repository.

Start with README.md, docs/public-input-format.md, docs/migration.md and docs/evidence.md. Restore the evidence bundle, run scripts.verify_evidence, then inspect `/public-format` and `/public-rca`. Browsing and verification need no API key.

The first study uses all 90 RCAEval RE2 Online Boutique cases: 30 training, 24 development, 18 calibration and 18 held-out evaluation cases. ML fits a scaler and balanced logistic candidate classifier only on training. Jev makes 60 calls. Held-out results are change ranking 18/18, Jev 17/18, ML 17/18 and resource ranking 14/18. Jev's frozen 0.50 threshold displays its error.

The second study makes 234 calls across compact, named and explained inputs. Every arm keeps the same measurements, missingness, observed candidates and Choice question. Development reuses 24 inspected Online Boutique cases. New Sock Shop groups provide 18 calibration and 36 evaluation cases; 36 reserve cases remain undownloaded. Calibration freezes 0.60/0.50/0.50 display thresholds. Held-out results are compact 34/36, named 35/36 and explained 34/36; ML transfer 32/36, change ranking 31/36 and resource ranking 26/36. Named fixes one compact error without a regression. Added explanations lose one named-input success. Displayed recommendations contain 2/0/0 observed errors, with 3/2/3 withheld.

These are controlled application faults with a supplied fault window and published injected-service references. Public pretraining exposure is unknown. Correlated groups and one response per arm per case do not establish stable improvement, telecom readiness or an operational error rate. ML on Sock Shop is the unchanged Online Boutique transfer control.

## Next experiment

The exact-request replay is complete: 180 successful calls on 12 inspected cases, five serial rounds across three inputs. Protocol and assessment are checkpoints/public-repeat-protocol-2026-10-03.json and checkpoints/public-repeat-results-2026-10-03.json. Recompute with scripts.run_public_repeat score. Original wire bodies, checkpoint and thresholds remain fixed.

Across five new rounds, compact/named/explained choices stayed stable on 12/9/11 cases; display decisions stayed stable on 11/10/12. Wrong displayed response counts were 7/0/5 out of 60 per input. Named retained all originally correct selections but changed choices on three already-wrong or insufficient-evidence cases. Two correct named selections crossed the frozen display threshold. Explained displayed the shared delay error in all five rounds although its original response had been withheld.

The predeclared gate failed on named choice and display variability. Keep the 36 reserve cases sealed. Inspect the ambiguous cases and evidence discarded by median summaries before designing a new transformation on fresh development cases. Do not tune thresholds or rerun this completed protocol. The read-only `/repeatability` inspector compares original and repeated responses, exposes exact wire JSON and hides published case answers until reveal. docs/public-repeatability.md reports the full diagnostic; these selected repeats do not estimate held-out accuracy or an operational error rate.

## Preservation and source boundaries

provenance/migration.json records the original source commit, original protocol fingerprints and active standalone source hashes. Original inference dependencies remain byte-for-byte under provenance/source. They are archival references; the app does not import the original synthetic packages.

Historical protocols are blocked from new hosted execution, even with another output directory. Checkpoints and release evidence must remain unchanged. New inference requires a separate protocol and the user's own key; .env.example documents the settings, without credentials.

## Prepared next stage

The offline timing audit is checkpoints/public-temporal-audit-2026-10-03.json; it uses 12 inspected cases, makes no calls and downloads no reserve data. docs/public-temporal-next.md explains the hypothesis and limitations. The instruction to continue uses the recommended analyst shortlist direction while retaining single-service scores; the inference contract has not been frozen yet.

The new preparation plan assigns all 90 RE2 Train Ticket cases in 18/18/36/18 grouped development/calibration/evaluation/reserve splits. Commit checkpoints/public-temporal-preparation-2026-10-04.json before scripts.prepare_public_temporal prepare. Only 18 development cases may be downloaded. Measure complete named and temporal request sizes and observed candidate coverage before any hosted protocol. All other Train Ticket telemetry stays undownloaded. No temporal hosted calls are authorized by the preparation script itself.

Fresh development preparation is now complete and validates exactly. It retains 68 services per case and 345–374 metric series. Complete named/temporal requests are 67–72/73–80 KB and fail the conservative byte bound, not a measured token limit. checkpoints/public-temporal-sizing-2026-10-04.json records counts and manifest hash. All 72 later Train Ticket cases and 36 Sock Shop reserve cases stay undownloaded.

The separate public-context-probe-2026-10-04 protocol allows one call on the largest temporal development request to check provider acceptance and input token usage, with no accuracy score or retries. Commit it before scripts.probe_public_context run. No hosted temporal comparison is frozen.
