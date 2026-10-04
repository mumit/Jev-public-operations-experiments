# Are the input results repeatable?

## Question and frozen design

I will check whether the saved Jev choices and display decisions recur when the provider receives exactly the same requests. The named input gained one correct held-out case over compact input; another shared error was withheld. A single response cannot show how stable either result is.

This diagnostic selects all six inspected calibration/evaluation cases where at least one Jev input disagrees with the published target. It adds the lexicographically first case for each of six faults where all three inputs were correct. That produces 12 cases; selection deliberately uses earlier outcomes. It does not represent the benchmark population or create a new held-out set.

Five serial rounds replay compact, named and explained input for every case: 180 calls, 60 per input and five responses per distinct request. Case starting position and first input rotate by round. Each request body is copied from the verified historical run; its bytes and hash remain identical. The model, question, candidates, measurements and explanations stay fixed. References, repetition identifiers and selection roles remain outside the wire request.

The original display thresholds remain 0.60 for compact and 0.50 for named and explained. No threshold is fitted here. The original response stays a separate comparison; it is not pooled with the five new responses.

## Execution and reporting

A committed protocol records the selection, source and evidence hashes, exact request plan, stop conditions and 180-call maximum. A once-only claim rejects another execution under that protocol, including another output directory. Calls have a 30-second timeout and no retries or warmup. HTTP, network or model-version errors stop execution; three consecutive malformed replies also stop it. Failed and unattempted calls remain in the planned denominators.

Results will show correctness, displayed errors and withheld choices for each round. Case-level inspection will distinguish stable choices from stable display decisions: the same selected service can move above or below its threshold. Five consistent wrong answers remain wrong. Each round will retain the named-versus-compact fixes and explained-versus-named regressions.

The author-set research gate keeps the reserve sealed if any call fails or is missing, a named-input displayed recommendation is wrong, a named choice or display decision changes across the five rounds, or named input loses an originally correct selection. Passing this targeted diagnostic would support considering a separately frozen reserve confirmation. It would not establish an operational error budget or justify automatic routing.

Five nearby rounds cannot establish stability across days, provider updates or production load. The hosted internals and caching are unknown. Correlated cases and outcome-based selection prevent a general accuracy estimate. All recommendations require analyst review, and all 36 reserve cases remain undownloaded.

## Prepared state

The replay is implemented in separate modules; original inference sources and checkpoints remain unchanged. Hosted results are not recorded yet. The new protocol must be committed before execution.

```bash
uv run --locked --extra public-data python -m scripts.run_public_repeat freeze
uv run --locked --extra public-data python -m scripts.run_public_repeat run
uv run --locked --extra public-data python -m scripts.run_public_repeat score --assessment checkpoints/public-repeat-results-2026-10-03.json
```

The CLI reads the local ignored `.env` by default; `--env-file` can select an existing local configuration. The key stays in process memory and never enters the protocol, requests, results or Git. Restoring the public evidence release is required before preparation.
