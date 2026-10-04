# Are the input results repeatable?

## Question and frozen design

This diagnostic checks whether the saved Jev choices and display decisions recur when the provider receives exactly the same requests. The named input gained one correct held-out case over compact input; another shared error was withheld. A single response cannot show how stable either result is.

This diagnostic selects all six inspected calibration/evaluation cases where at least one Jev input disagrees with the published target. It adds the lexicographically first case for each of six faults where all three inputs were correct. That produces 12 cases; selection deliberately uses earlier outcomes. It does not represent the benchmark population or create a new held-out set.

Five serial rounds replay compact, named and explained input for every case: 180 calls, 60 per input and five responses per distinct request. Case starting position and first input rotate by round. Each request body is copied from the verified historical run; its bytes and hash remain identical. The model, question, candidates, measurements and explanations stay fixed. References, repetition identifiers and selection roles remain outside the wire request.

The original display thresholds remain 0.60 for compact and 0.50 for named and explained. No threshold is fitted here. The original response stays a separate comparison; it is not pooled with the five new responses.

## Execution and reporting

A committed protocol records the selection, source and evidence hashes, exact request plan, stop conditions and 180-call maximum. A once-only claim rejects another execution under that protocol, including another output directory. Calls have a 30-second timeout and no retries or warmup. HTTP, network or model-version errors stop execution; three consecutive malformed replies also stop it. Failed and unattempted calls remain in the planned denominators.

Results show correctness, displayed errors and withheld choices for each round. Case-level inspection distinguishes stable choices from stable display decisions: the same selected service can move above or below its threshold. Five consistent wrong answers remain wrong. Each round retains the named-versus-compact fixes and explained-versus-named regressions.

The author-set research gate keeps the reserve sealed if any call fails or is missing, a named-input displayed recommendation is wrong, a named choice or display decision changes across the five rounds, or named input loses an originally correct selection. Passing this targeted diagnostic would support considering a separately frozen reserve confirmation. It would not establish an operational error budget or justify automatic routing.

Five nearby rounds cannot establish stability across days, provider updates or production load. The hosted internals and caching are unknown. Correlated cases and outcome-based selection prevent a general accuracy estimate. All recommendations require analyst review, and all 36 reserve cases remain undownloaded.

## Results

All 180 calls succeeded. Each request matched its historical wire hash. The table counts stability across the five new rounds; the original response remains a separate comparison.

| Input | Stable choices, 12 cases | Stable display decisions, 12 cases | Always matches original choice, 12 cases | Wrong displayed responses, 60 calls |
|---|---:|---:|---:|---:|
| Compact | 12 | 11 | 12 | 7 |
| Named | 9 | 10 | 9 | 0 |
| Explained | 11 | 12 | 10 | 5 |

Each round matched 7/12 published targets for compact and 9/12 for named and explained input. Named retained both earlier fixes over compact on this selected panel, with no regression. All six originally correct controls stayed correct across every input and round. These are descriptive counts on outcome-selected cases, not general accuracy estimates.

Three cases show why choice stability and display stability need separate checks:

- `FMT-49b5cf388bb3`: named selected the correct orders service in all five rounds, but its probability ranged from 0.41 to 0.54. Only the last round displayed the recommendation at the frozen 0.50 threshold. Compact consistently selected the wrong payment service and displayed it in two rounds.
- `FMT-a89dbccd5437`: named always selected the correct payment service, but one round fell to 0.49 and withheld it. Explained changed from its original wrong orders selection to payment in every new round. That change happened with identical requests.
- `FMT-ebb72cb3ab15`: named alternated between payment and shipping, both wrong, and withheld every response. Explained consistently selected payment, also wrong, and displayed it in every new round. Its original response had been withheld. Added explanations did not protect the display boundary.

The other two named choice changes occurred on weak, withheld disk-fault selections. Five nearby rounds cannot explain the provider's internal source of variation. They show that exact inputs do not guarantee identical choices or display decisions.

## What this changes

Named input remains the strongest candidate among these formats for analyst-facing research. It retained its correct choices and displayed no wrong recommendation on this panel. However, its original held-out display count is a single-run observation, not stable coverage. Explained input displayed the shared delay error in all five replays despite withholding the original response.

The predeclared research gate failed on named choice and display variability. The 36 reserve cases stay sealed; thresholds and historical results stay fixed. The subsequent [timing audit and fresh development comparison](public-temporal-next.md) inspect what the summaries discard and test an addition on Train Ticket cases. Changing the threshold to fit these inspected responses would not answer that question.

## Inspect and reproduce

The read-only [replay inspector](http://127.0.0.1:8769/repeatability) compares the original response with each round, displays choice distributions and exposes exact request and response JSON. Published references require explicit reveal. Browsing makes no model calls.

The committed protocol and assessment record the request plan, source hashes, stop conditions and results. Original inference code and checkpoints remain unchanged. The runner refuses another execution under this protocol. Use the saved evidence to recompute it:

```bash
uv run --locked --extra public-data python -m scripts.run_public_repeat score
```

The original public-study-v1 bundle contains the two historical studies only. The separate public-diagnostics-v1 asset supplies this replay and the later development evidence; restore it after the original bundle using the [evidence guide](evidence.md). No credentials belong in either bundle.
