# Jev public operations experiments

I am testing whether Jev can help identify the originating faulty service from public telemetry, and which input changes improve its recommendations. The app exposes the measurements, exact requests, actual responses, local ML scores and frozen review thresholds.

The current evidence comes from controlled RCAEval Online Boutique and Sock Shop faults. Each case supplies the injection boundary. These studies do not establish telecom readiness, anomaly detection or an operational error rate.

## Completed comparisons

| Study | Held-out evidence | Result |
|---|---|---|
| Metric root-cause comparison | 18 Online Boutique cases, six groups | Change ranking 18/18; Jev and trained ML 17/18; resource ranking 14/18. Jev's threshold displays one wrong recommendation. |
| Jev input presentation | 36 Sock Shop cases, 12 groups | Named fields 35/36; compact and explained inputs 34/36; transferred ML 32/36. Named input displays 34 correct recommendations and withholds two at its frozen threshold. |

Named fields are a candidate for further verification. Their gain over compact input is one case; adding explanations loses one named-input success. All recommendations require analyst review.

## Run the app

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/). Install the pinned dependencies:

```bash
uv sync --locked --extra public-data
uv run --locked --extra public-data python -m triage_bench.app --port 8769
```

Open [the public studies](http://127.0.0.1:8769/). The server binds to loopback and serves a read-only inspection app. It needs no API key and makes no model calls.

A fresh clone includes source, reports and checkpoints. Restore the [public evidence bundle](docs/evidence.md) to inspect recorded predictions. Missing local evidence stays explicitly unavailable. The bundle supplies pinned metric files, prepared inputs, separate references, the original fitted ML control and all 294 saved Jev calls across the two studies. It contains no synthetic study runs or credentials.

## Read and inspect

- [Dataset assessment](docs/public-data-assessment.md): sources, terms and input preparation.
- [Metric experiment](docs/public-rca-experiment.md): training, grouped splits, methods and results.
- [Input comparison](docs/public-input-format.md): lossless transformations, matched cases and review thresholds.
- [Evidence bundle](docs/evidence.md): download, safe restoration and verification.
- [Migration](docs/migration.md): archived sources and the standalone extraction.
- [HANDOFF](HANDOFF.md): current state and next experiment.
- [Verification](docs/verification.md): standalone tests and fresh-clone evidence replay.

## Checks

```bash
uv run --locked --extra public-data python -m unittest discover -s tests -v
uv run --locked --extra public-data python -m scripts.verify_evidence
node --check triage_bench/web/public-rca.js
node --check triage_bench/web/public-format.js
node --check triage_bench/web/study.js
```

The evidence verifier reconstructs ML from training-only inputs, rebuilds every recorded Jev request and recomputes all six stage assessments and the frozen thresholds. It makes no hosted calls. Unit tests run without the bundle; full evidence verification requires restoration.

## Continue the research

Read HANDOFF.md and AGENTS.md before editing. Completed protocols are read-only in this repository, including requests to use an alternative output directory. New inference needs a separately frozen protocol and your own key in an ignored `.env` or environment variable. Do not change measured input builders or tune against inspected evaluation failures.

The next recommended experiment checks exact-request repeatability on inspected cases. Thirty-six Sock Shop reserve cases remain undownloaded for later confirmation. ML keeps its Online Boutique training recipe; on Sock Shop it is a transfer control, not an optimal or locally retrained model.

The repository starts with a fresh Git history. Its public studies retain source provenance from [the earlier repository](https://github.com/mumit/Jev-incident-triage-experiments), without requiring that checkout or its synthetic experiments.
