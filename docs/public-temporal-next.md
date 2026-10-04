# What evidence should the next input preserve?

## What the replay establishes

The [repeatability diagnostic](public-repeatability.md) separates two problems. Named input changes some weak, withheld selections, and two correct selections cross its display boundary. It keeps all originally correct service choices on the selected panel. Explained input displays a shared error that its original response withheld. Exact requests do not guarantee fixed recommendations, and five repeats do not reveal the provider's internal reason.

The development experiment keeps single-service accuracy as a control and tests shortlists of up to three services, with the cause explicitly unconfirmed. A shortlist is an investigation aid, not a confirmed diagnosis. Including the published target in three candidates is a different result from selecting it first; the report must show both, shortlist size, wrong leads and withheld outputs. No current threshold or historical score changes.

## Offline timing audit

I inspected the original time series for the 12 replay cases without making model calls or downloading reserve data. The audit preserves before-window scale and missingness, then calculates latency medians for 0–60, 60–300 and 300–721 seconds after the supplied boundary. These windows were chosen after inspecting the failures. They are an exploratory hypothesis, not a validated transformation.

In `FMT-ebb72cb3ab15`, the published injection is orders. Its latency-50 before median is 0.339286; the three later medians are 0.704545, 1.594368 and 1.541667. Payment latency-90 rises from 0.004662 to 0.165, 0.22 and 0.22. Shipping latency-90 rises from 0.004640 to 0.173, 0.220349 and 0.22. Both symptoms produce much larger baseline-scaled changes than orders. The existing input retains the full-window shifts but loses this timing detail.

These values do not establish a causal sequence. Metric collection and aggregation delays are unknown, and similar time windows can contain both the fault and its effects. Adding time windows may help distinguish transient from sustained evidence, or may simply add more correlated symptoms. A comparison on fresh cases must resolve that question.

The audit also leaves the weak disk cases unresolved. Their metric summaries have no disk-I/O series for orders. That absence does not prove the root cause is unknowable, but it explains why relabelling fields cannot add a direct measurement that was never collected.

Reproduce the audit to a new file:

```bash
uv run --locked --extra public-data python -m scripts.audit_public_temporal --output runs/public-temporal/audit-copy.json
```

The output folder must already exist. The recorded checkpoint contains the inspected calculations and raw-file hashes. It records no new model performance.

## Fresh development evidence

The pinned RCAEval index provided 90 RE2 Train Ticket cases that the earlier studies had not inspected. All report 720 before and 721 after samples. Their service/fault repetition groups can stay together in 18 development, 18 calibration, 36 evaluation and 18 reserve cases. The existing 36-case Sock Shop reserve and new Train Ticket calibration/evaluation/reserve telemetry remain sealed.

Train Ticket is larger: index entries report 340–376 metric series per case, compared with the smaller applications already studied. Preparation measured request size and candidate coverage before any hosted call. The current named input and a temporal variant must fit the declared context bound without silently dropping candidates or measurements.

The separate protocol compares unchanged named summaries with the same summaries plus latency time windows. Both arms keep the same candidate services and cause-selection question. The shortlist comes from the saved choice distribution, not another hidden inference step. Single-service accuracy, candidate inclusion, shortlist size and display behavior must stay visible separately. New ML fitting, trace interpretation and automatic routing are outside this comparison.

The shortlist direction was selected after the instruction to continue. Its precise development contract is now frozen below.

## Development preparation result

All 18 development cases passed source hashes, timestamp checks, input reconstruction and separate reference joins. Every case retains 68 observed services; the published cause is present in every candidate set. Metric counts range from 345 to 374. The downloaded metrics and boundary files total 16,797,536 bytes. All 72 later Train Ticket cases and 36 Sock Shop reserve cases remain undownloaded.

Complete named requests contain 67,301–71,940 bytes; temporal requests contain 73,444–79,840 bytes. None passes the lab's conservative bound of request bytes plus 512 within the declared 32,768-token capacity. This is not an actual tokenizer measurement and does not establish that Jev rejects these requests.

[TypeSafe's Models documentation](https://docs.typesafe.ai/models) specifies 64k tokens for a request and 32k for state plus the longest question. The API schema provides token usage after evaluation, but no token-count-only endpoint. A separate, committed one-call capacity protocol selects the largest temporal request by byte size, without reference answers. The probe completed successfully: 30,471 input tokens and 391 ms. It does not score accuracy or loosen any existing guard. Acceptance of one request is not an exact token-count proof for every prepared request.

The provider also documents weaknesses with precise numerical tasks and large irrelevant states, recommending calculations and filtering in code. This supports testing focused, computed evidence rather than assuming that more raw numbers will improve the result. It does not prove why any recorded case failed. [Jev 1.13 documented limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

## Frozen development comparison

A separate protocol now permits 108 calls: 18 development cases, six groups, two input arms and three serial rounds. Named input keeps the original full-window measurements. Temporal input keeps those measurements and adds only the latency windows. The original cause-selection question and all 68 observed candidates remain identical. Case and first-arm order rotate across rounds. Calls have no retries or warmup; HTTP, network, model-version or reported capacity failures stop execution. Missing calls stay in all planned denominators.

The analyst shortlist contains at most three positive-probability service candidates. The selected tied winner comes first; remaining ties follow service identifier order. Insufficient-evidence choices and failed or missing replies withhold the shortlist. Each lead carries an unconfirmed-cause interpretation. No new probability boundary is fitted. Both top-1 correctness and target inclusion among the leads remain visible, alongside wrong leads, shortlist size and withholding. The original fitted ML transfers unchanged; deterministic change and resource rankings use the same input summaries.

Calibration will stay sealed until the intended inclusion-versus-withholding criterion is selected. A list with the target somewhere among three services is not equivalent to one correct recommendation; its extra wrong leads consume analyst effort. That tradeoff determines how a later boundary should be chosen. The protocol does not assume an operational error budget.

## Development results

All 108 comparison calls succeeded, and every reported input count stayed within the declared capacity. Each round uses the same 18 cases; do not pool them into 54 independent test cases.

| Method | Correct first choice, each round | Published cause in first three leads, each round | Extra wrong leads per round |
|---|---:|---:|---:|
| Jev named | 16/18 | 18/18 | 32–34 |
| Jev temporal | 15/18 | 18/18 | 36 |
| Frozen ML transfer | 18/18 | 18/18 | Not a calibrated shortlist policy |
| Change ranking | 17/18 | 18/18 | Not a calibrated shortlist policy |
| Resource ranking | 10/18 | 14/18 | Not a calibrated shortlist policy |

Named input kept its first choice on all 18 cases across three rounds. Its ordered shortlist stayed identical on 11 cases. Temporal input kept its first choice on 17 cases and its ordered shortlist on 10. Named generated 50–52 leads per round; temporal generated 54. Neither withheld a shortlist. Secondary leads can change while the primary selection stays fixed.

`TMP-536c2593bbc8` is the consistent regression. Named selected the published orders service in every round. Temporal selected inside-payment instead, with orders second. Adding timing evidence did not remove the true cause from the shortlist, but it displaced the correct first choice. There were no temporal first-choice fixes or shortlist-inclusion gains.

Both named errors involve train-service network-loss cases, where admin-travel ranks first and train remains in the shortlist. On one of those cases, temporal alternates between admin-travel and payment. The unchanged ML control ranks the published service first on every development case. This is an observed transfer result on six groups, not evidence that ML will stay perfect on new faults.

## Decision before calibration

Named input is the development candidate. Temporal windows add request size and one repeated regression without improving target inclusion. The candidate keeps the named summaries.

A shortlist includes the published cause more often than one selected service here, but extra leads can create unnecessary investigation. Most named first choices were already correct. Adding weak alternatives to those cases inflated the lead count without fixing a primary error. The benchmark reference can count those extras; it cannot measure their actual investigation cost or usefulness to an analyst.

The user selected fewer wrong leads, accepting more withholding. The separate [selective-policy experiment](public-selective.md) freezes its calibration objective and display rules before opening new telemetry. The 72 later Train Ticket cases were undownloaded when development ended; subsequent calibration and evaluation belong to that new experiment. The 36 Sock Shop reserve cases remain undownloaded.

Inspect the [development comparison](http://127.0.0.1:8769/temporal) for exact inputs, the added latency windows, all three responses and matched local rankings. These are development findings, not held-out improvement or demonstrated analyst benefit.
