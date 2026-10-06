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

The verifier for this stage checks the full nine-stage dependency chain, including both original pack validators, without inference. Restore assets in the documented order. Never replace a published archive or rerun a completed protocol.


## Wording diagnostic supplement

The [public-claim-language-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-claim-language-v1) adds 456 calls with 1,368 answers. It records three wordings of 152 propositions on the same 32 inspected service cards. No measurements are altered and no fresh telemetry is downloaded. The six files retain separate references, exact wording/ledger requests and responses. The archive is 176,200 bytes and requires all nine earlier assets. All ten preserve 2,317 actual responses in 1,053 files.

```sh
gh release download public-claim-language-v1 --repo mumit/Jev-public-operations-experiments --pattern public-claim-language-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-claim-language-v1.tar.gz --manifest evidence/public-claim-language-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_claim_language
```

Restore assets in order. The verifier for this stage invokes all ten study verifiers and both original pack validators without inference. Historical assets remain immutable.


## Multi-service report-reading supplement

The [public-report-reading-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-report-reading-v1) adds 96 calls with 576 answers. Six claims about two named services form each of 16 reports. Direct questions and numbered report lookup share identical two-service ledgers. The six files contain reports, separate typed references, exact requests and actual responses. The archive is 83,750 bytes and requires all ten earlier assets. All eleven preserve 2,413 actual responses in 1,059 files.

```bash
gh release download public-report-reading-v1 --repo mumit/Jev-public-operations-experiments --pattern public-report-reading-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-report-reading-v1.tar.gz --manifest evidence/public-report-reading-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_reports
```

Restore in order. The verifier for this stage checks all eleven studies and both original pack validators without inference. Direct judgments are correct throughout; report lookup repeats two withheld errors and fails both comparison checks. These authored notes reuse inspected telemetry. Protected recordings stay unopened and historical releases stay unchanged.


## Explicit binding and scope supplement

The [public-claim-binding-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-claim-binding-v1) adds 672 calls and 1,152 verdicts on the same 16 reports. It retains four controlled steps: numbered lookup, bound text, one-claim grouping and scoped service facts. Six files preserve unchanged reports/references, exact requests and individual provider responses. The archive is 216,247 bytes and requires all eleven earlier assets. All twelve preserve 3,085 actual responses in 1,065 files.

```bash
gh release download public-claim-binding-v1 --repo mumit/Jev-public-operations-experiments --pattern public-claim-binding-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-claim-binding-v1.tar.gz --manifest evidence/public-claim-binding-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_binding
```

Restore assets in order. The verifier for this stage checks all twelve studies and both original pack validators without inference. Explicit binding fixes both repeated lookup errors; one-claim grouping introduces a one-round regression; scoped facts judge and display every claim correctly. The full sequence fails, while binding and scope pass their separate checks. All protected recordings remain unopened and historical releases stay immutable.

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

Restore in order. The verifier for this stage preserves the response failures and recomputes an extraction-only audit. It checks all historical stages and both original pack validators without inference. There are 1,944 raw extraction answers and 1,800 normalized answers; the two rejected notes remain in every planned scoring denominator. The inspector exposes raw distributions without treating them as accepted replies. Measurements are already inspected, and all protected panels stay unopened. Historical releases remain immutable.

## Sentence-review evidence

The [public-sentence-review-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-sentence-review-v1) adds the separate extraction replay and dependent verdict comparison. Its six files preserve 108 actual responses, 2,312 valid answers, exact requests and once-only execution records. The archive is 175,471 bytes. Restore all fourteen earlier assets first; the unchanged notes and annotations come from the note-extraction asset.

```bash
gh release download public-sentence-review-v1 --repo mumit/Jev-public-operations-experiments --pattern public-sentence-review-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-sentence-review-v1.tar.gz --manifest evidence/public-sentence-review-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_sentence_review
```

All fifteen assets preserve 3,409 actual responses in 1,113 files. The new run contains no inconsistent answers; both validators accept the same 152 correct bindings on its replies. All accepted Jev claims receive correct, displayed verdicts, but incomplete-note coverage fails both application checks. The earlier sizing failure and rejected replies remain frozen. No protected telemetry opens, and verification makes no calls.

## Extraction-definition contrasts

The [public-extraction-contrast-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-extraction-contrast-v1) adds four paired inputs on the same nine inspected notes. Its six files preserve 216 actual calls and 8,385 valid answers, with exact extraction and dependent verdict requests, raw replies and execution records. The archive is 604,485 bytes. Restore the fifteen earlier assets first; the notes, measurements and references remain in their unchanged earlier bundles.

```bash
gh release download public-extraction-contrast-v1 --repo mumit/Jev-public-operations-experiments --pattern public-extraction-contrast-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-extraction-contrast-v1.tar.gz --manifest evidence/public-extraction-contrast-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_extraction_contrast
```

All sixteen assets preserve 3,625 actual responses in 1,119 files. Assertion-family-only recovers seven correct bindings against fresh baseline without losses; the declared combined candidate loses eleven overall and fails both application checks. All accepted bindings and verdicts are correct. No input is promoted, no protected recording opens, and verification makes no calls.

## New-note wording

The [public-note-language-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/public-note-language-v1) adds three controlled wording styles per inspected recording. Its nine files preserve 27 notes with separate references, exact extraction and dependent verdict requests, 324 actual calls, 12,543 raw answers, 12,538 validated answers and five quarantined sentence fields. The archive is 1,103,081 bytes. Restore all sixteen earlier assets first; the source measurements remain in their unchanged bundles.

```bash
gh release download public-note-language-v1 --repo mumit/Jev-public-operations-experiments --pattern public-note-language-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/public-note-language-v1.tar.gz --manifest evidence/public-note-language-v1.json
uv run --locked --extra public-data python -m scripts.verify_public_note_language
```

All seventeen assets preserve 3,949 actual responses in 1,128 files. Family-only gives 430/486 correct end-to-end judgments versus baseline 447/486, with ten gains and twenty-seven losses. It displays no wrong binding; baseline displays two. Both application checks fail, and no candidate is promoted. Verification makes no model calls; protected recordings remain unopened.

## Assistant-reviewed verdict comparison

The [assistant-review-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/assistant-review-v1) adds 162 actual replies on 27 same-assistant-reviewed controlled notes. Its three files preserve exact requests, raw replies and once-only execution records, with 972 valid verdicts. The committed review decisions, plan, exact protocol and assessment are in the repository. Restore all seventeen earlier assets first. The archive is 102,453 bytes.

```bash
gh release download assistant-review-v1 --repo mumit/Jev-public-operations-experiments --pattern assistant-review-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/assistant-review-v1.tar.gz --manifest evidence/assistant-review-v1.json
uv run --locked --extra public-data python -m scripts.verify_assistant_review
```

All eighteen assets preserve 4,111 actual responses in 1,131 files. Both bound-text and explicit-meaning inputs judge and display every reviewed claim correctly throughout. Explicit meaning adds no observed benefit and consumes 8.1% more input tokens. The same assistant authored notes, annotations and review decisions; there were zero human or independent reviews. No protected recording opens and verification makes no inference calls.

## Controlled binding-corruption evidence

The [binding-corruption-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/binding-corruption-v1) adds 405 actual replies on the same 27 controlled notes, comparing two clean controls, two wrong-service inputs and reversed explicit polarity. Its three files preserve exact requests, raw replies and once-only records. The archive is 201,056 bytes. Restore all eighteen preceding assets first.

```bash
gh release download binding-corruption-v1 --repo mumit/Jev-public-operations-experiments --pattern binding-corruption-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/binding-corruption-v1.tar.gz --manifest evidence/binding-corruption-v1.json
uv run --locked --extra public-data python -m scripts.verify_binding_corruption
```

The original-sentence and altered-proposition references, plan, exact protocol and assessment are committed separately from inputs. Two inconsistent fields remain quarantined: 2,428 of 2,430 raw verdicts validate. No protected recording or human review enters this diagnostic. The nineteen assets preserve 4,516 actual replies in 1,134 files; verification makes no calls.

## Explicit subject-check evidence

The [subject-check-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/subject-check-v1) adds 324 actual replies on 27 inspected controlled notes. Two exact sentence baselines compare with two inputs that ask for both a subject check and an original-sentence verdict. Its three files preserve exact requests, all 2,916 valid raw answers and once-only execution records. The archive is 230,327 bytes. Restore all nineteen preceding assets first.

```bash
gh release download subject-check-v1 --repo mumit/Jev-public-operations-experiments --pattern subject-check-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/subject-check-v1.tar.gz --manifest evidence/subject-check-v1.json
uv run --locked --extra public-data python -m scripts.verify_subject_check
```

The plan, exact protocol, separate references and assessment are committed. The overall candidate fails: Online Boutique loses clean displays and still displays one corrupted-subject error. Train Ticket passes without a clean-display loss. No protected recording or human review enters the diagnostic. The twenty assets preserve 4,840 actual replies in 1,137 files; verification makes no calls.


## Separate subject-call evidence

The [separate-subject-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/separate-subject-v1) adds 486 actual replies: fresh joint checks, text-only subject calls and unchanged numerical verdict baselines. All 3,888 answers validate. Three files preserve exact bodies, raw responses and once-only execution records in a 333,805-byte archive. Restore all twenty preceding assets first.

```bash
gh release download separate-subject-v1 --repo mumit/Jev-public-operations-experiments --pattern separate-subject-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/separate-subject-v1.tar.gz --manifest evidence/separate-subject-v1.json
uv run --locked --extra public-data python -m scripts.verify_separate_subject
```

The plan, both exact phase protocols, original references and assessment are committed. Train Ticket passes; Online Boutique retains 16–17 clean display losses per round and fails overall, despite gaining eight displays over fresh joint checks. Both workflows withhold every swapped display here, but subject errors remain. No protected recording, human review or independent review enters the diagnostic. All twenty-one assets preserve 5,326 provider responses in 1,140 files; verification makes no calls.

## Direct subject supplement

The [direct-subject-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/direct-subject-v1) adds 405 actual replies: direct service extraction without a proposal, fresh proposal checks and unchanged numerical verdict baselines. All 2,430 answers validate. Three files preserve exact requests, raw replies and execution records in a 260,893-byte archive. Restore all twenty-one preceding assets first.

```bash
gh release download direct-subject-v1 --repo mumit/Jev-public-operations-experiments --pattern direct-subject-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/direct-subject-v1.tar.gz --manifest evidence/direct-subject-v1.json
uv run --locked --extra public-data python -m scripts.verify_direct_subject
```

All twenty-two assets preserve 5,731 actual responses in 1,143 files. The verifier for this stage reproduces unique service accuracy, both proposal compositions, shared-call costs, paired display gains and losses, every historical assessment and both original packs without inference. Same-author and zero-human/independent-review labels remain explicit; every protected recording stays unopened.


## Prefix subject-context evidence

The [prefix-subject-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/prefix-subject-v1) adds 1,134 actual replies: paired one-question subject calls with full-note and literal prefix context, plus unchanged clean and swapped numerical verdict batches. Three files preserve exact requests, raw responses and once-only execution records in a 357,786-byte archive. Restore all twenty-two preceding assets first.

```bash
gh release download prefix-subject-v1 --repo mumit/Jev-public-operations-experiments --pattern prefix-subject-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/prefix-subject-v1.tar.gz --manifest evidence/prefix-subject-v1.json
uv run --locked --extra public-data python -m scripts.verify_prefix_subject
```

Of 1,944 raw answers, 1,943 validate. One inconsistent subject reply remains quarantined without repair or retry. Prefix context displays 102/103/102 correct Online Boutique claims versus 99/99/99 with full-note context and blocks the full-note input's one unsafe swapped display. Subject errors, withholding and paired regressions remain; the candidate fails overall. Train Ticket passes. Zero human or independent reviews and all protected recording boundaries remain unchanged. All twenty-three assets preserve 6,865 actual replies in 1,146 files; verification makes no inference calls.

## Literal excerpts, context challenges and complete workflows

Three supplements extend the earlier evidence without altering historical inputs or results. Restore them after all twenty-three preceding assets, in this order. Each archive contains exact requests, untouched raw replies and execution summaries; references and frozen protocols remain in Git.

### Literal service excerpt

The [excerpt-subject-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/excerpt-subject-v1) adds 1,134 actual calls and 1,944 valid answers. Three files preserve fresh prefix/excerpt subject comparisons and unchanged numerical controls. The overall excerpt candidate fails. The archive has 347,645 bytes and SHA-256 `5e327461c603e376527b00b45199fb6d1f82e79bb008864890c0571b90ec3d51`.

```bash
gh release download excerpt-subject-v1 --repo mumit/Jev-public-operations-experiments --pattern excerpt-subject-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/excerpt-subject-v1.tar.gz --manifest evidence/excerpt-subject-v1.json
```

### Subject-context challenges

The [subject-robustness-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/subject-robustness-v1) adds 1,215 actual calls and 1,214 valid answers. Three files preserve subject-only responses on fifteen controlled patterns. One inconsistent choice remains quarantined; no numerical verdict or analyst recommendation exists. The archive has 257,268 bytes and SHA-256 `9e1cad4d2e82652236b999f0eb37d18cae78e5326f6d24270e799610019dda6c`.

```bash
gh release download subject-robustness-v1 --repo mumit/Jev-public-operations-experiments --pattern subject-robustness-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/subject-robustness-v1.tar.gz --manifest evidence/subject-robustness-v1.json
```

### Complete report workflow

The [full-workflow-v1 release](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/full-workflow-v1) adds 270 actual calls and 6,812 valid answers. Six files preserve full-note extraction, correct supplied-field controls and numerical requests generated from actual automatic/parser bindings. Fifty-four empty parser jobs are skips, not provider calls. The automatic candidate fails. The archive has 621,718 bytes and SHA-256 `f517f6dff50a7e0143b772bb1b95e52fdbef1ee52cddd0f4940e077884961e71`.

```bash
gh release download full-workflow-v1 --repo mumit/Jev-public-operations-experiments --pattern full-workflow-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/full-workflow-v1.tar.gz --manifest evidence/full-workflow-v1.json
```

All twenty-six assets preserve 9,484 actual provider responses in 1,158 files. The three supplements add 2,619 calls on familiar recordings, with zero human or independent reviews. All protected panels remain unopened. Run `scripts.verify_full_workflow` to replay the complete chain without credentials or inference.

## Explicit claims and preparation failures

Three new immutable supplements preserve the explicit-entry work. Restore all twenty-six predecessors first, then these supplements in order. Exact plans, protocols, assessments and failure audits remain in Git.

| Release | Files | Actual provider calls | Archive bytes | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| [explicit-claims-v1](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/explicit-claims-v1) | 6 | 750 | 132,499 | `e2e05232175f17816bc1cf25dd13411b20c444ab86b89d86ca1e19d869c07120` |
| [explicit-format-v1](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/explicit-format-v1) | 3 | 2,250 | 374,704 | `7c04f436ba5e91c29742c648ad3fe16ac23627a49d5988181f025c9a0dacee0a` |
| [explicit-preparation-failures-v1](https://github.com/mumit/Jev-public-operations-experiments/releases/tag/explicit-preparation-failures-v1) | 90 | 0 | 9,860,249 | `f6811d76dfde050207fdc1185e9efd77d276389c1f24fd0dd62d8cc1b4d2c42a` |

The first supplement includes 250 controlled entries, separate references and 750 typed-input calls. The second preserves 2,250 fresh typed, focused and calculated-fact calls on those same entries. The third contains ninety publisher-verified public source files from three failed preparations, with zero hosted responses and no prepared claims. Forty-five recordings were downloaded and are now opened; the first experiment's separate fifteen-recording allocation and all earlier protected panels stay unopened.

```bash
gh release download explicit-claims-v1 --repo mumit/Jev-public-operations-experiments --pattern explicit-claims-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/explicit-claims-v1.tar.gz --manifest evidence/explicit-claims-v1.json
gh release download explicit-format-v1 --repo mumit/Jev-public-operations-experiments --pattern explicit-format-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/explicit-format-v1.tar.gz --manifest evidence/explicit-format-v1.json
gh release download explicit-preparation-failures-v1 --repo mumit/Jev-public-operations-experiments --pattern explicit-preparation-failures-v1.tar.gz --dir runs/downloads
uv run --locked --extra public-data python -m scripts.restore_evidence runs/downloads/explicit-preparation-failures-v1.tar.gz --manifest evidence/explicit-preparation-failures-v1.json
uv run --locked --extra public-data python -m scripts.verify_explicit_preparations
```

All twenty-nine assets preserve 12,484 actual provider responses in 1,257 files. The latest verifier replays twenty-eight executed studies, all failed preparations and both original pack validators without credentials or inference. It verifies the missing post-incident window instead of inventing or repairing measurements. The next data-policy choice is recorded in [HANDOFF](../HANDOFF.md).
