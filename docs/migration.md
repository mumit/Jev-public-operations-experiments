# Starting the public studies in a separate repository

I separated the public RCAEval work from the synthetic incident lab so others can inspect and extend it without the earlier Git history. The source snapshot is recorded in `provenance/migration.json`.

## What moved

The new repository includes both public experiments, their checkpoint files, metric preparation, Jev request construction, response normalization, local ML training and scoring, read-only workbenches and formatted reports. A versioned release adds the public metric packs, exact saved requests and responses, fitted ML artifact and once-only execution records.

Synthetic packets, their reports and runs, credentials, environments and unrelated drafts were excluded. The original repository and running app remain available. This app uses port 8769 by default.

## How verification works

Original inference dependencies are archived byte-for-byte under `provenance/source/`. Some helper files originally imported synthetic modules; their archived copies are references, not runtime dependencies.

The active extraction replaces those imports with focused helpers for wire encoding, redaction, key cleanup and profile validation. A public-only app and reader replace the synthetic app routes. Original protocols and checkpoints retain their bytes and source hashes. The verifier checks those hashes against the archived source, checks the extracted active baseline separately, reconstructs all saved request bodies and recomputes ML and every stage assessment. It does not pretend that the original protocol ran from this new Git history.

Future protocols fingerprint the active standalone sources. Completed historical protocols cannot make new hosted calls here. New experiments belong in separate modules so the imported baseline remains verifiable.

## What did not change

The dataset revision, measurements, split assignments, references, service candidates, questions, fitted ML control, saved Jev responses, scores and calibration-selected thresholds remain unchanged. The migration makes no model calls and consumes none of the reserve telemetry.

The historical evidence is a baseline, not a new validation result. Inspect the original study reports for the limits of their comparisons.
