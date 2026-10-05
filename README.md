# Jev public operations experiments

I am testing whether Jev can help identify the originating faulty service from public telemetry, and which input changes improve its recommendations. The app exposes the measurements, exact requests, actual responses, local ML scores and frozen review thresholds.

The current evidence comes from controlled RCAEval Online Boutique, Sock Shop and Train Ticket faults. Each case supplies the injection boundary. These studies do not establish telecom readiness, anomaly detection or an operational error rate.

## Completed comparisons

| Study | Held-out evidence | Result |
|---|---|---|
| Evidence assessment | 32 selected service cards from 16 inspected recordings, two inputs, three rounds | Observations gives Train Ticket 20/20 all-four matches each round. Calculated gives 19/20/19; Online Boutique improves from 11/9/10 to 11/11/11 of 12. The calculated candidate fails overall. This is numerical policy agreement, not cause accuracy. |
| Trace-aware task and arithmetic | 16 fresh RE3 development cases, four inputs, three rounds | No repeated fixes. Train Ticket displays no leads; Online Boutique remains 6/6 correct but loses one displayed lead in two rounds. Evaluation stays sealed. |
| Trace context | 13 RE3 development cases, two inputs, three rounds | No repeated fixes; evaluation remains sealed. Train Ticket metrics/trace matches 1–0–1 / 1–1–1 of 7; Online Boutique 3–3–4 of 6 in both arms. |
| Disagreement review trigger | 50 RE1 Train Ticket and 50 Sock Shop cases, three rounds | No wrong leads caught. Only correct Jev leads sent to review; Jev and ML agree on the one eligible Sock Shop error. |
| Reserve confirmation | 18 Train Ticket and 36 Sock Shop cases, three rounds | Train Ticket retains one confidently wrong lead per round; Sock Shop shows 27 correct leads and withholds nine correct choices. The zero-error result does not reproduce uniformly. |
| Selective recommendation policy | 36 Train Ticket cases, twelve groups, three rounds | Frozen 0.70 rule displays 19–22 correct leads, no wrong leads, and withholds 14–17 cases per round. Unfiltered Jev ranks 30/36 first; ML ranks 28/36. |
| Metric root-cause comparison | 18 Online Boutique cases, six groups | Change ranking 18/18; Jev and trained ML 17/18; resource ranking 14/18. Jev's threshold displays one wrong recommendation. |
| Jev input presentation | 36 Sock Shop cases, 12 groups | Named fields 35/36; compact and explained inputs 34/36; transferred ML 32/36. Named input displays 34 correct recommendations and withholds two at its frozen threshold. |

The fresh 18-case Train Ticket development comparison gives named/temporal Jev first choices of 16/18 and 15/18 in each of three rounds; frozen ML transfer gives 18/18. Both Jev shortlists include all targets but add 32–36 wrong leads per round. See the [development report](docs/public-temporal-next.md) before treating shortlist inclusion as a useful recommendation.

Named fields are a candidate for further verification. Their gain over compact input is one case; adding explanations loses one named-input success. All recommendations require analyst review.

## Run the app

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/). Install the pinned dependencies:

```bash
uv sync --locked --extra public-data
uv run --locked --extra public-data python -m triage_bench.app --port 8769
```

Open [the public studies](http://127.0.0.1:8769/). The server binds to loopback and serves a read-only inspection app. It needs no API key and makes no model calls.

A fresh clone includes source, reports and checkpoints. Restore all eight [public evidence bundles](docs/evidence.md) to inspect recorded predictions. Missing local evidence stays explicitly unavailable. The original bundle supplies 294 saved calls across two comparisons; the supplement adds 289 responses for replay, context sizing and fresh development. The selective-policy release adds 162 calibration/evaluation responses. The confirmation release adds the final 162 RE2 reserve responses. The disagreement release adds 300 responses on fresh RE1 recordings and a ten-case schema audit. The trace release adds 78 development responses, raw traces, the audit and both sizing attempts. The trace-task release adds 192 development responses and the four-step comparison. The evidence-assessment release adds 192 four-question diagnostic responses. All eight retain measurements, separate references and exact requests, with no synthetic runs or credentials.

## Read and inspect

- [Evidence assessment](docs/public-evidence-assessment.md): local changes, missing evidence and the metric that supports investigation.
- [Trace-aware task](docs/public-trace-task.md): separate task wording and arithmetic, with case-level failures.
- [Trace study](docs/public-traces.md): dependencies, timing, missing instrumentation and paired development failures.
- [Disagreement study](docs/public-agreement.md): errors caught, correct guidance lost and shared mistakes on fresh recordings.
- [Dataset assessment](docs/public-data-assessment.md): sources, terms and input preparation.
- [Metric experiment](docs/public-rca-experiment.md): training, grouped splits, methods and results.
- [Input comparison](docs/public-input-format.md): lossless transformations, matched cases and review thresholds.
- [Next evidence experiment](docs/public-temporal-next.md): timing audit, fresh development results and selected shortlist direction.
- [Reserve confirmation](docs/public-confirmation.md): unchanged policy on both previously untouched reserve panels.
- [Selective recommendations](docs/public-selective.md): fewer leads, calibration boundaries and withholding costs.
- [Repeatability diagnostic](docs/public-repeatability.md): exact-request replay design and research gate.
- [Evidence bundle](docs/evidence.md): download, safe restoration and verification.
- [Migration](docs/migration.md): archived sources and the standalone extraction.
- [HANDOFF](HANDOFF.md): current state and next experiment.
- [Verification](docs/verification.md): standalone tests and fresh-clone evidence replay.

## Checks

```bash
uv run --locked --extra public-data python -m unittest discover -s tests -v
uv run --locked --extra public-data python -m scripts.verify_evidence
uv run --locked --extra public-data python -m scripts.verify_public_diagnostics
uv run --locked --extra public-data python -m scripts.verify_public_selective
uv run --locked --extra public-data python -m scripts.verify_public_confirmation
uv run --locked --extra public-data python -m scripts.verify_public_agreement
uv run --locked --extra public-data python -m scripts.verify_public_traces
uv run --locked --extra public-data python -m scripts.verify_public_trace_task
uv run --locked --extra public-data python -m scripts.verify_public_evidence
node --check triage_bench/web/public-rca.js
node --check triage_bench/web/public-format.js
node --check triage_bench/web/public-repeat.js
node --check triage_bench/web/public-temporal.js
node --check triage_bench/web/public-selective.js
node --check triage_bench/web/public-agreement.js
node --check triage_bench/web/public-evidence.js
node --check triage_bench/web/public-trace-task.js
node --check triage_bench/web/public-traces.js
node --check triage_bench/web/study.js
```

The evidence verifier reconstructs ML from training-only inputs, rebuilds every recorded Jev request and recomputes all six stage assessments and the frozen thresholds. It makes no hosted calls. Unit tests run without the bundle; full evidence verification requires restoration.

## Continue the research

Read HANDOFF.md and AGENTS.md before editing. Completed protocols are read-only in this repository, including requests to use an alternative output directory. New inference needs a separately frozen protocol and your own key in an ignored `.env` or environment variable. Do not change measured input builders or tune against inspected evaluation failures.

Inspect the latest [evidence-assessment diagnostic](http://127.0.0.1:8769/evidence-assessment). It reuses inspected recordings and opens no protected panels. The calculated input improves Online Boutique but loses Train Ticket accuracy, so its overall check fails. The next choice is a judgment beyond numerical rules or a separately frozen fresh verification of observations-only evidence assessment. All 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves remain unopened. Earlier fitted ML and all cause-selection studies remain preserved.

The repository starts with a fresh Git history. Its public studies retain source provenance from [the earlier repository](https://github.com/mumit/Jev-incident-triage-experiments), without requiring that checkout or its synthetic experiments.
