# Handoff: public operations experiments

## Current state

Both public studies are complete and preserved. The standalone extraction passes 52 tests; a fresh GitHub clone restores all 347 release files and recomputes both studies exactly. The repository has a standalone read-only app, pinned preparation and inference code, separate references, recorded checkpoints and a public evidence release. The earlier synthetic studies and Git history remain in their original repository.

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
