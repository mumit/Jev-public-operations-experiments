# Handoff: public operations experiments

## Current state

Both public studies are complete and preserved. The standalone extraction passes 48 tests; a fresh GitHub clone restores all 347 release files and recomputes both studies exactly. The repository has a standalone read-only app, pinned preparation and inference code, separate references, recorded checkpoints and a public evidence release. The earlier synthetic studies and Git history remain in their original repository.

Start with README.md, docs/public-input-format.md, docs/migration.md and docs/evidence.md. Restore the evidence bundle, run scripts.verify_evidence, then inspect `/public-format` and `/public-rca`. Browsing and verification need no API key.

The first study uses all 90 RCAEval RE2 Online Boutique cases: 30 training, 24 development, 18 calibration and 18 held-out evaluation cases. ML fits a scaler and balanced logistic candidate classifier only on training. Jev makes 60 calls. Held-out results are change ranking 18/18, Jev 17/18, ML 17/18 and resource ranking 14/18. Jev's frozen 0.50 threshold displays its error.

The second study makes 234 calls across compact, named and explained inputs. Every arm keeps the same measurements, missingness, observed candidates and Choice question. Development reuses 24 inspected Online Boutique cases. New Sock Shop groups provide 18 calibration and 36 evaluation cases; 36 reserve cases remain undownloaded. Calibration freezes 0.60/0.50/0.50 display thresholds. Held-out results are compact 34/36, named 35/36 and explained 34/36; ML transfer 32/36, change ranking 31/36 and resource ranking 26/36. Named fixes one compact error without a regression. Added explanations lose one named-input success. Displayed recommendations contain 2/0/0 observed errors, with 3/2/3 withheld.

These are controlled application faults with a supplied fault window and published injected-service references. Public pretraining exposure is unknown. Correlated groups and one response per arm per case do not establish stable improvement, telecom readiness or an operational error rate. ML on Sock Shop is the unchanged Online Boutique transfer control.

## Next experiment

The exact-request replay is prepared in separate modules and documented in docs/public-repeatability.md. It selects all six earlier cases with any Jev reference error and six deterministic all-correct controls. Five serial rounds across compact, named and explained inputs make 180 calls. Exact wire bodies, the Jev checkpoint and original thresholds stay fixed. Original responses remain separate from the repeats.

Commit checkpoints/public-repeat-protocol-2026-10-03.json before execution, then run scripts.run_public_repeat and save the assessment to a new checkpoint. Its research gate keeps the 36 reserve cases sealed if calls fail, named choices or display decisions vary, a named recommendation displays an error, or named loses an originally correct selection. Repeats measure variability on inspected cases, not new held-out accuracy. Hosted replay results are not recorded yet.

## Preservation and source boundaries

provenance/migration.json records the original source commit, original protocol fingerprints and active standalone source hashes. Original inference dependencies remain byte-for-byte under provenance/source. They are archival references; the app does not import the original synthetic packages.

Historical protocols are blocked from new hosted execution, even with another output directory. Checkpoints and release evidence must remain unchanged. New inference requires a separate protocol and the user's own key; .env.example documents the settings, without credentials.
