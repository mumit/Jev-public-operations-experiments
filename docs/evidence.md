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
