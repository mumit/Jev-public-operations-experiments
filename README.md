# Jev public operations experiments

I am testing where Jev can help operations analysts: selecting investigation leads, assessing evidence and checking written claims against public telemetry. The app exposes the measurements, exact requests, actual responses, local ML scores and frozen review thresholds.

The current evidence comes from controlled RCAEval Online Boutique, Sock Shop and Train Ticket faults. Each case supplies the injection boundary. These studies do not establish telecom readiness, anomaly detection or an operational error rate.

The new [claim review workflow](http://127.0.0.1:8769/claim-review) lets an analyst confirm Jev's extracted service and meaning before a verdict request. This stage has no new model results; it awaits actual reviews.

## Completed comparisons

| Study | Evidence | Result |
|---|---|---|
| New-note wording | Three styles on nine inspected recordings, two inputs, three rounds | Family-only gives 430/486 correct end-to-end judgments versus baseline 447/486. It displays no wrong binding; baseline displays two. Both application checks fail; no promotion. |
| Extraction definitions | Same nine notes, four inputs, three rounds | Assertion-family-only recovers seven claims: 160/162 versus baseline 153/162. Combined loses eleven overall and fails both checks. No accepted wrong binding or unsafe verdict; no candidate promotion. |
| Sentence review | Same nine inspected notes and exact extraction bodies, three new rounds | Jev accepts 152/162 correct bindings, then judges and displays all 152 correctly. Both full-note coverage checks fail. No inconsistent replies recur, so both validators give the same new bindings. |
| Note extraction | Nine inspected recordings, twelve sentence candidates per note, three rounds | Jev accepts 142 correct bindings across 162 planned opportunities. Two inconsistent replies fail whole-note validation; no dependent verdict calls occur. Parser accepts only 54 explicit-name bindings. End-to-end performance remains unmeasured. |
| Fresh claim confirmation | Nine untouched recordings, three fault groups, new controlled wording, three rounds | Both candidates judge all 54 claims correctly throughout. Bound displays all verdicts; scoped withholds one correct verdict once and uses six times as many calls. Both pass bounded-task checks; extraction and attribution remain untested. |
| Claim wording | 152 propositions with three wordings, 32 inspected cards, three rounds | Every verdict is correct for all wordings and rounds. Explicit comparisons reduce withholding; no displayed errors. Specific authored paraphrases pass, with real reports and fresh incidents still untested. |
| Explicit claim binding | Same 96 claims and 16 reports, four steps, three rounds | Bound text fixes both repeated errors with no verdict losses. One-claim grouping introduces a one-round Train Ticket regression; scoped facts judge and display all claims correctly. Full sequence fails; step results remain separate. |
| Multi-service report reading | 16 reports, 96 claims, two presentations, three rounds | Direct: all verdicts correct; report: 59/60 Train Ticket and 35/36 Online Boutique each round. Two repeated errors withheld; both comparison checks fail. |
| Written claim assessment | 96 constructed statements on 32 inspected cards, two inputs, three rounds | Ledger: 60/60 Train Ticket and 36/36 Online Boutique verdicts correct every round; observations: 58/60 and 33/36. Five repeated errors fixed; no losses. Diagnostic passes on fixed templates; fresh generalization remains untested. |
| Evidence assessment | 32 selected service cards from 16 inspected recordings, two inputs, three rounds | Observations gives Train Ticket 20/20 all-four matches each round. Calculated gives 19/20/19; Online Boutique improves from 11/9/10 to 11/11/11 of 12. The calculated candidate fails overall. This is numerical policy agreement, not cause accuracy. |
| Trace-aware task and arithmetic | 16 fresh RE3 development cases, four inputs, three rounds | No repeated fixes. Train Ticket displays no leads; Online Boutique remains 6/6 correct but loses one displayed lead in two rounds. Evaluation stays sealed. |
| Trace context | 13 RE3 development cases, two inputs, three rounds | No repeated fixes; evaluation remains sealed. Train Ticket metrics/trace matches 1–0–1 / 1–1–1 of 7; Online Boutique 3–3–4 of 6 in both arms. |
| Disagreement review trigger | 50 RE1 Train Ticket and 50 Sock Shop cases, three rounds | No wrong leads caught. Only correct Jev leads sent to review; Jev and ML agree on the one eligible Sock Shop error. |
| Reserve confirmation | 18 Train Ticket and 36 Sock Shop cases, three rounds | Train Ticket retains one confidently wrong lead per round; Sock Shop shows 27 correct leads and withholds nine correct choices. The zero-error result does not reproduce uniformly. |
| Selective recommendation policy | 36 Train Ticket cases, twelve groups, three rounds | Frozen 0.70 rule displays 19–22 correct leads, no wrong leads, and withholds 14–17 cases per round. Unfiltered Jev ranks 30/36 first; ML ranks 28/36. |
| Metric root-cause comparison | 18 Online Boutique cases, six groups | Change ranking 18/18; Jev and trained ML 17/18; resource ranking 14/18. Jev's threshold displays one wrong recommendation. |
| Jev input presentation | 36 Sock Shop cases, 12 groups | Named fields 35/36; compact and explained inputs 34/36; transferred ML 32/36. Named input displays 34 correct recommendations and withholds two at its frozen threshold. |

The fresh 18-case Train Ticket development comparison gives named/temporal Jev first choices of 16/18 and 15/18 in each of three rounds; frozen ML transfer gives 18/18. Both Jev shortlists include all targets but add 32–36 wrong leads per round. See the [development report](docs/public-temporal-next.md) before treating shortlist inclusion as a useful recommendation.

Named fields improve one compact-input case, but later confirmation retains a confidently wrong Train Ticket lead. The latest claim diagnostic instead keeps arithmetic in code and tests bounded written judgments. All recommendations require analyst review.

## Run the app

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/). Install the pinned dependencies:

```bash
uv sync --locked --extra public-data
uv run --locked --extra public-data python -m triage_bench.app --port 8769
```

Open [the public studies](http://127.0.0.1:8769/). The server binds to loopback and serves a read-only inspection app. It needs no API key and makes no model calls.

A fresh clone includes source, reports and checkpoints. Restore all seventeen [public evidence bundles](docs/evidence.md) to inspect recorded predictions. Missing local evidence stays explicitly unavailable. The original bundle supplies 294 saved calls across two comparisons; the supplement adds 289 responses for replay, context sizing and fresh development. The selective-policy release adds 162 calibration/evaluation responses. The confirmation release adds the final 162 RE2 reserve responses. The disagreement release adds 300 responses on fresh RE1 recordings and a ten-case schema audit. The trace release adds 78 development responses, raw traces, the audit and both sizing attempts. The trace-task release adds 192 development responses and the four-step comparison. The evidence-assessment release adds 192 four-question diagnostic responses. The claim-assessment release adds 192 three-question responses on 96 constructed statements. The wording release adds 456 calls and 1,368 answers on 152 propositions. The report-reading release adds 96 calls and 576 answers on 16 paired-service reports. The claim-binding release adds 672 calls and 1,152 verdicts across four controlled steps. The fresh-claim release adds 189 calls and 324 verdicts on nine previously untouched recordings. All thirteen retain measurements, separate references and exact requests, with actual provider responses, public source measurements and no credentials. The note-extraction supplement adds 27 actual responses, including two rejected replies, with new controlled notes and separate annotations. It makes no verdict calls and opens no recording. Those fourteen preserve 3,301 responses in 1,107 files. The separate sentence-review supplement adds 108 calls and six files, bringing all fifteen to 3,409 responses in 1,113 files. Extraction contrasts add 216 calls and six files; all sixteen preserve 3,625 responses in 1,119 files. The new-note wording supplement adds 324 responses and nine files, bringing seventeen assets to 3,949 responses in 1,128 files.

## Read and inspect

- [New-note wording](docs/public-note-language.md): check whether family-only extraction transfers across plain, negated and boundary phrasing.
- [Extraction definitions](docs/public-extraction-contrast.md): compare isolated wording changes, paired gains and losses, and actual acceptance probabilities.
- [Sentence review](docs/public-sentence-review.md): preserve valid siblings and inspect the complete extraction-to-verdict pipeline.
- [Note extraction](docs/public-note-extraction.md): separate role, subject, meaning and response-validation failures.
- [Fresh claim confirmation](docs/public-fresh-claims.md): new measurements, controlled notes and candidate call costs.
- [Claim binding](docs/public-claim-binding.md): explicit text, question grouping and service scope.
- [Report reading](docs/public-report-reading.md): six claims about two services, with direct and report judgments.
- [Claim wording](docs/public-claim-language.md): paraphrases, negation and actual missing-versus-zero observations.
- [Written claim assessment](docs/public-claim-assessment.md): compare observations with an explicit fact ledger.
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
uv run --locked --extra public-data python -m scripts.verify_public_binding
uv run --locked --extra public-data python -m scripts.verify_public_fresh_claims
uv run --locked --extra public-data python -m scripts.verify_public_note_language
node --check triage_bench/web/claim-review.js
node --check triage_bench/web/public-rca.js
node --check triage_bench/web/public-format.js
node --check triage_bench/web/public-repeat.js
node --check triage_bench/web/public-temporal.js
node --check triage_bench/web/public-selective.js
node --check triage_bench/web/public-agreement.js
node --check triage_bench/web/public-evidence.js
node --check triage_bench/web/public-claims.js
node --check triage_bench/web/public-note-extraction.js
node --check triage_bench/web/public-fresh-claims.js
node --check triage_bench/web/public-claim-binding.js
node --check triage_bench/web/public-report-reading.js
node --check triage_bench/web/public-claim-language.js
node --check triage_bench/web/public-trace-task.js
node --check triage_bench/web/public-traces.js
node --check triage_bench/web/study.js
```

The evidence verifier reconstructs ML from training-only inputs, rebuilds every recorded Jev request and recomputes the historical assessments and blocked extraction audit and the frozen thresholds. It makes no hosted calls. Unit tests run without the bundle; full evidence verification requires restoration.

## Continue the research

Read HANDOFF.md and AGENTS.md before editing. Completed protocols are read-only in this repository, including requests to use an alternative output directory. New inference needs a separately frozen protocol and your own key in an ignored `.env` or environment variable. Do not change measured input builders or tune against inspected evaluation failures.

Complete one note in the claim review workflow, download its JSON and run the local validator described in [the guide](docs/claim-review.md). Actual human reviews are pending. A new exact protocol and budget must precede any verdict calls. The 22 cause-evaluation cases, 30 RE3 Sock Shop cases and 140 RE1 reserves remain unopened.
