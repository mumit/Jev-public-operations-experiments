# Public study evidence bundle

The `public-study-v1` GitHub release contains the recorded evidence for both public experiments. It is separate from Git so the repository stays small. The bundle contains public RCAEval files and saved model evidence, without credentials or synthetic runs.

## Restore

From the repository root, download the release asset:

```bash
gh release download public-study-v1 --repo mumit/Jev-public-operations-experiments --pattern public-study-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-study-v1.tar.gz
uv run --locked --extra public-data python -m scripts.verify_evidence
```

The archive is also available from the [release page](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-study-v1). Place a manually downloaded copy under `runs/downloads/`, then run the restoration command.

Restoration verifies the tracked archive checksum and every included file, rejects unsafe paths and links, and refuses to overwrite existing evidence. It extracts only the listed public run directories. The included fitted model reconstructs exactly from the 30 Online Boutique training cases. Verification makes no hosted calls.

## Contents and limits

The bundle includes the pinned public case index, the 90-case Online Boutique metric pack, the matched-input pack, all 294 actual Jev responses, exact request bodies, fitted ML and stage summaries. Original source and checkpoint fingerprints remain in Git. The 36 reserve cases have assignments only; their telemetry is absent.

The dataset assessment documents source terms and collection limits. Restoring this bundle gives access to recorded benchmark evidence, not specialist-reviewed telecom reports or a live network connection. Replaying local scores does not regenerate hosted responses. New hosted calls would be a separate experiment.

## Later diagnostics

The separate [public-diagnostics-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-diagnostics-v1) adds the 180-call replay, 18 fresh Train Ticket development cases, the accepted one-call context probe and the 108-call named-versus-temporal comparison. Its 51 files contain 289 actual provider responses plus measurements, exact requests, transfer-control scores and execution records. It does not replace public-study-v1.

Restore the original bundle first, then the supplement:

```bash
gh release download public-diagnostics-v1 --repo mumit/Jev-public-operations-experiments --pattern public-diagnostics-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-diagnostics-v1.tar.gz --manifest evidence/public-diagnostics-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_diagnostics
```

The same safe restoration rules apply. The supplemental archive is 13,814,645 bytes. All 72 later Train Ticket cases and 36 Sock Shop reserve cases have assignments only; their telemetry is absent. Verification reconstructs the later assessments without calling Jev. The current decision before calibration is documented in [HANDOFF](../HANDOFF.md).


## Selective recommendation evidence

The [public-selective-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-selective-v1) adds the 54 calibration and 108 evaluation responses, public Train Ticket measurements, exact named requests and unchanged transfer controls. Its 124 files total 38,958,221 archive bytes. Restore the two earlier bundles first.

```bash
gh release download public-selective-v1 --repo mumit/Jev-public-operations-experiments --pattern public-selective-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-selective-v1.tar.gz --manifest evidence/public-selective-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_selective
```

All three releases preserve 745 actual hosted responses. They do not regenerate hosted inference or contain a live network connection. The remaining 18 Train Ticket reserve cases and 36 Sock Shop reserve cases have no telemetry in these bundles. Safe restoration rejects unknown entries, checksum drift, links and overwrites.


## Reserve confirmation evidence

The [public-confirmation-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-confirmation-v1) adds 162 responses on the final 18 Train Ticket and 36 Sock Shop reserve cases. Its 116 files include public measurements, exact named requests and unchanged local controls. The archive is 17,791,339 bytes. Restore the three earlier bundles first.

```bash
gh release download public-confirmation-v1 --repo mumit/Jev-public-operations-experiments --pattern public-confirmation-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-confirmation-v1.tar.gz --manifest evidence/public-confirmation-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_confirmation
```

The four releases preserve 907 actual hosted responses and 638 files. Both former reserve panels are now inspected. Earlier bundle descriptions and verifier sealing counts describe the state at their original stage, not the current supply of fresh validation data. See [confirmation results](public-confirmation.md) and [HANDOFF](../HANDOFF.md) before designing another experiment.

## Fresh disagreement evidence

The [public-agreement-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-agreement-v1) adds 300 responses on 50 RE1 Train Ticket and 50 Sock Shop recordings, plus the ten-case schema audit. Its 229 files contain public measurements, separate references, exact requests, unchanged controls and saved paired routing outcomes. The archive is 30,394,164 bytes. Restore the four earlier bundles first.

```bash
gh release download public-agreement-v1 --repo mumit/Jev-public-operations-experiments --pattern public-agreement-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-agreement-v1.tar.gz --manifest evidence/public-agreement-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_agreement
```

All five bundles preserve 1,207 actual hosted responses and 867 files. The fifth verifier reconstructs the schema audit, publisher hashes, grouped evaluation packets, exact requests, normalized responses, fixed ML controls and both applications' paired outcomes without inference. Seventy RE1 cases per application remain unopened; their assignments are metadata only and their telemetry is absent from the archive. Earlier bundle reserve counts describe those historical stages, not the current RE2 state.

## Trace development evidence

The [public-traces-development-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-traces-development-v1) adds 78 paired development responses on 13 RE3 code-fault recordings. Its 112 files preserve the seven-case schema audit, public metrics and traces, both sizing representations, exact requests and local controls. The archive is 136,963,040 bytes. Restore the five earlier bundles first. Evaluation and reserve telemetry are excluded because development failed promotion.

```bash
gh release download public-traces-development-v1 --repo mumit/Jev-public-operations-experiments --pattern public-traces-development-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-traces-development-v1.tar.gz --manifest evidence/public-traces-development-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_traces
```

All six bundles preserve 1,285 actual responses across 979 evidence files. Restoring, browsing and verification need no key and make no model calls. Keep the first sizing failure and its compact replacement; neither preflight made a provider call. Never replace an asset with changed evidence.

## Trace-aware task evidence

The [public-trace-task-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-trace-task-v1) adds 192 responses on 16 fresh RE3 development recordings. Its 56 files include publisher-verified metrics and traces, separate references, four exact request forms, arithmetic changes and unchanged controls. The archive is 77,066,595 bytes. Restore the six earlier bundles first.

```bash
gh release download public-trace-task-v1 --repo mumit/Jev-public-operations-experiments --pattern public-trace-task-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-trace-task-v1.tar.gz --manifest evidence/public-trace-task-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_trace_task
```

All seven assets preserve 1,477 actual responses in 1,035 files. Both new development gates fail; the 22 evaluation cases and nine remaining RE3 reserves have no telemetry in this supplement. Sixteen cases from the earlier stage's 25 reserves became development for this separately frozen study. All historical assets remain unchanged.

## Evidence-assessment diagnostic

The [public-evidence-assessment-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-evidence-assessment-v1) adds 192 responses containing 768 answers on 32 service cards from 16 already inspected recordings. Its six files preserve the selected observations, separate numerical references, two exact request forms and execution records. It downloads no fresh telemetry. The archive is 73,359 bytes and requires all seven earlier assets.

```bash
gh release download public-evidence-assessment-v1 --repo mumit/Jev-public-operations-experiments --pattern public-evidence-assessment-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-evidence-assessment-v1.tar.gz --manifest evidence/public-evidence-assessment-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_evidence
```

All eight releases preserve 1,669 actual responses in 1,041 files. The new questions use numerical policy references, not injected-service labels. Calculated changes pass Online Boutique's checks but lose Train Ticket accuracy, so the overall diagnostic fails. Restoring and verification make no calls; all protected telemetry remains unopened. Earlier assets remain unchanged.


## Written-claim diagnostic supplement

The [public-claim-assessment-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-claim-assessment-v1) adds 192 responses with 576 answers on 96 constructed claims. It reuses the 32 inspected service cards and downloads no fresh telemetry. Its six files retain statements, separate typed references, exact observations/ledger requests and responses. The archive is 84,831 bytes and requires all eight earlier assets. All nine releases preserve 1,861 actual responses in 1,047 files.

```sh
gh release download public-claim-assessment-v1 --repo mumit/Jev-public-operations-experiments --pattern public-claim-assessment-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-claim-assessment-v1.tar.gz --manifest evidence/public-claim-assessment-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_claims
```

The latest verifier checks the full nine-stage dependency chain, including both original pack validators, without inference. Restore assets in the documented order. Never replace a published archive or rerun a completed protocol.


## Wording diagnostic supplement

The [public-claim-language-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-claim-language-v1) adds 456 calls with 1,368 answers. It records three wordings of 152 propositions on the same 32 inspected service cards. No measurements are altered and no fresh telemetry is downloaded. The six files retain separate references, exact wording/ledger requests and responses. The archive is 176,200 bytes and requires all nine earlier assets. All ten preserve 2,317 actual responses in 1,053 files.

```sh
gh release download public-claim-language-v1 --repo mumit/Jev-public-operations-experiments --pattern public-claim-language-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-claim-language-v1.tar.gz --manifest evidence/public-claim-language-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_claim_language
```

Restore assets in order. The latest verifier invokes all ten study verifiers and both original pack validators without inference. Historical assets remain immutable.


## Multi-service report-reading supplement

The [public-report-reading-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-report-reading-v1) adds 96 calls with 576 answers. Six claims about two named services form each of 16 reports. Direct questions and numbered report lookup share identical two-service ledgers. The six files contain reports, separate typed references, exact requests and actual responses. The archive is 83,750 bytes and requires all ten earlier assets. All eleven preserve 2,413 actual responses in 1,059 files.

```bash
gh release download public-report-reading-v1 --repo mumit/Jev-public-operations-experiments --pattern public-report-reading-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-report-reading-v1.tar.gz --manifest evidence/public-report-reading-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_reports
```

Restore in order. The latest verifier checks all eleven studies and both original pack validators without inference. Direct judgments are correct throughout; report lookup repeats two withheld errors and fails both comparison checks. These authored notes reuse inspected telemetry. Protected recordings stay unopened and historical releases stay unchanged.


## Explicit binding and scope supplement

The [public-claim-binding-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-claim-binding-v1) adds 672 calls and 1,152 verdicts on the same 16 reports. It retains four controlled steps: numbered lookup, bound text, one-claim grouping and scoped service facts. Six files preserve unchanged reports/references, exact requests and individual provider responses. The archive is 216,247 bytes and requires all eleven earlier assets. All twelve preserve 3,085 actual responses in 1,065 files.

```bash
gh release download public-claim-binding-v1 --repo mumit/Jev-public-operations-experiments --pattern public-claim-binding-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-claim-binding-v1.tar.gz --manifest evidence/public-claim-binding-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_binding
```

Restore assets in order. The latest verifier checks all twelve studies and both original pack validators without inference. Explicit binding fixes both repeated lookup errors; one-claim grouping introduces a one-round regression; scoped facts judge and display every claim correctly. The full sequence fails, while binding and scope pass their separate checks. All protected recordings remain unopened and historical releases stay immutable.

## Fresh-measurement claim confirmation supplement

The [public-fresh-claims-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-fresh-claims-v1) adds 189 actual responses containing 324 verdicts. It opens only nine separately allocated RE3 reserves, retaining their source metrics, traces, injection boundaries, new controlled notes, separate typed references and exact bound/scoped requests. The 33 files require all twelve earlier assets. The archive is 37,408,282 bytes. All thirteen preserve 3,274 responses in 1,098 files.

```bash
gh release download public-fresh-claims-v1 --repo mumit/Jev-public-operations-experiments --pattern public-fresh-claims-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-fresh-claims-v1.tar.gz --manifest evidence/public-fresh-claims-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_fresh_claims
```

Both candidates judge every claim correctly. Bound displays every answer with one call per report; scoped uses six and withholds one correct answer once. The new wording was fixed before measurement access, but still comes from the experiment author. Automatic extraction and attribution remain untested. Restoring and verifying make no calls; protected cause-evaluation, RE3 Sock Shop and RE1 reserve recordings stay unopened. Historical releases remain immutable.

## Ordinary-note extraction supplement

The [public-note-extraction-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-note-extraction-v1) preserves both note preparations and all 27 extraction responses. The first preparation fails sizing before inference. The separate compact v2 receives 25 valid and two inconsistent replies; the frozen whole-note validator rejects both. No dependent verdict calls occur. Nine files add 277,891 archive bytes and require all thirteen earlier assets. All fourteen preserve 3,301 actual responses in 1,107 files.

```bash
gh release download public-note-extraction-v1 --repo mumit/Jev-public-operations-experiments --pattern public-note-extraction-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-note-extraction-v1.tar.gz --manifest evidence/public-note-extraction-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_notes
```

Restore in order. The latest verifier preserves the response failures and recomputes an extraction-only audit. It checks all historical stages and both original pack validators without inference. There are 1,944 raw extraction answers and 1,800 normalized answers; the two rejected notes remain in every planned scoring denominator. The inspector exposes raw distributions without treating them as accepted replies. Measurements are already inspected, and all protected panels stay unopened. Historical releases remain immutable.
