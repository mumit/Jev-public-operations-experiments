# Does clearer input help Jev?

## Purpose

I tested whether Jev selects the faulty service more reliably when metric values have names and explicit explanations. The earlier public comparison found Jev and ML each correct on 17/18 held-out cases, while change ranking got all 18. Jev's display threshold admitted its wrong answer. Those results remain frozen.

The new comparison changes input presentation. Every arm keeps the same values, missingness, observed services, model and Choice question. No labeled examples, logs, traces or topology enter the request.

## Inputs

| Arm | Transformation | Comparison |
|---|---|---|
| Compact | Original five-value arrays and shared column legend. | Fresh control calls using the frozen request construction. |
| Named | Replace each array with five named fields; retain the shared metadata. | Named versus compact tests placement of field names. |
| Explained | Keep named fields and add static metric and field definitions. | Explained versus named tests the added explanations. |

For example, a socket entry changes from:

```json
"socket": [9, 22, 144.44444, 0, 0]
```

to:

```json
"socket": {
  "before_median": 9,
  "after_median": 22,
  "signed_change": 144.44444,
  "before_missing_fraction": 0,
  "after_missing_fraction": 0
}
```

The explained arm states that signed change is dimensionless and is neither a raw before/after ratio nor a causal probability. A flat baseline can make a modest raw increase produce a large normalized score. Its socket definition asks the reader to compare raw medians alongside this score. Static definitions apply to every service; they do not select a fault or target.

The [RCAEval paper](https://arxiv.org/html/2412.17015v1) describes resource and application metrics collected with Prometheus, cAdvisor and Istio. It does not establish the exact units of every abbreviated metric in the pinned files. The explanations therefore retain source scales and explicitly avoid assuming cores, percentages, bytes, seconds, milliseconds or request rates. Latency definitions retain the source labels rather than assert an unverified collector formula. This is a presentation and explanation study, not a unit-conversion study.

A round-trip check converts each named input back to the original state and requires exact equality, including nulls, zeros, signs, medians, missing fractions and service names. The question and options also match the frozen control exactly.

## Data

The pinned source revision stays `afeacb11bcc94dadfd1c8f483ee4377b2b8b614e`. Public references name the injected faulty service; source paths and index answers stay outside requests. All cases use the known injection boundary, so this comparison does not evaluate anomaly detection.

| Split | System | Cases | Groups | Use |
|---|---|---:|---:|---|
| Development | Online Boutique | 24 | 8 | Previously inspected cases; fresh calls for each arm. |
| Calibration | Sock Shop | 18 | 6 | New groups; select display thresholds only. |
| Evaluation | Sock Shop | 36 | 12 | New groups; compare frozen inputs once. |
| Reserve | Sock Shop | 36 | 12 | Metadata assignments only; telemetry remains undownloaded. |

Each service/fault group contains three repetitions and stays in one split. Calibration, evaluation and reserve each cover all six fault types. The assignment uses a fixed cyclic rule over service and fault names before telemetry inspection, recorded in the plan checkpoint. It does not select cases by baseline or Jev performance.

Sock Shop introduces another application system, not telecom incidents. The [RCAEval dataset description](https://github.com/phamquiluan/RCAEval) identifies it as a separate benchmark system. The new held-out comparison also changes the system, so old-versus-new accuracy is not an input-transformation effect. Only matched arms on the same new cases support that comparison. Public pretraining exposure remains unknown.

## Controls and execution

The change and resource rankings stay frozen. ML retains the original scaler and classifier fitted on 30 Online Boutique training cases. It receives the original metric vectors without refitting. On Sock Shop, it is a transfer control, not a Sock Shop-trained or optimal ML model.

Jev stays at `jev-1.13.0`. Three serial calls per case rotate arm order evenly. Each split has one execution claim, even if another output directory is requested. The maximum is 72 development, 54 calibration and 108 evaluation calls, with no retries or warmup. Access, checkpoint, rate-limit and network errors stop the run; three consecutive malformed responses also stop it. Failed and missing calls stay in each arm's denominator.

All three arms continue unchanged through evaluation. A committed candidate checkpoint gates calibration. Each arm separately selects its display threshold from the historical grid: maximize recommendations with zero observed calibration errors; choose the lower threshold on ties. If none qualify, display none. The committed boundary gates one held-out run. These are research criteria. Every recommendation needs analyst review.

Results report matched fixes and regressions, complete groups, failures, confidence errors, threshold coverage, input size, client latency and provider usage. One response per arm per case cannot fully separate presentation effects from provider variability. Fresh compact development calls keep the main comparison contemporaneous; older compact responses remain a separate repeat diagnostic.

## Evidence and reproduction

The study completed all 234 planned calls without failed or missing responses. The standalone test and evidence checks are recorded in the verification guide. Development, calibration and evaluation checkpoints recompute from the saved evidence. Raw evidence stays in ignored `runs/public-data/input-format-2026-10-03-v1/` and `runs/public-format/`. Tracked plan, data and protocol checkpoints preserve assignments, hashes and intended calls. The original public comparison remains unchanged.

On a fresh checkout, restore the public index using the dataset assessment's preparation commands, then prepare and verify the new pack:

```bash
uv run --locked --extra public-data python -m scripts.run_public_format build
uv run --locked --extra public-data python -m scripts.run_public_format validate
```

These commands need the original public metric pack for development and the recorded ML control for inference. They do not recover missing historical hosted responses. Existing packs and runs cannot be overwritten.

## Development result

Development completed 72 calls from protocol commit `1e3dd53`, with no failed or missing responses. Compact, named and explained inputs each match all 24 published services and all eight groups. Their selected services are identical. All three inputs fix the same one ML error and one change-ranking error; those gains already occur with compact input.

This set offers no decision-level evidence for adopting the clearer formats. The contemporaneous compact choices also match the original development choices. Probability differences and provider variability remain separate from correctness. All three arms continued unchanged to Sock Shop calibration and evaluation.

## Calibration result and frozen thresholds

Sock Shop calibration completed 54 calls on 18 cases in six new groups, with no failed calls. Compact input matches 15 published targets; named and explained each match 16. Named fields correct `FMT-dff737ef5d78` without a regression. Added explanations change another choice but fix no additional reference error. The fixed resource ranking and transferred ML each match 16; general change ranking matches 15.

The predefined threshold search selects 0.60 for compact input and 0.50 for named and explained input. Compact admits 13 recommendations; each clearer input admits 16. None of those admitted recommendations is wrong on calibration. These findings do not establish probability calibration or operational reliability. The committed boundary freezes all three thresholds before evaluation.

## Held-out result

Evaluation completed 108 calls from boundary commit `aa38b44`, on 36 cases in 12 previously untouched Sock Shop groups. Every arm used the frozen inputs and thresholds.

| Method | Correct services / 36 | Entire groups correct / 12 |
|---|---:|---:|
| Change ranking | 31 | 8 |
| Resource ranking | 26 | 8 |
| ML · frozen transfer | 32 | 10 |
| Jev · compact | 34 | 11 |
| Jev · named | 35 | 11 |
| Jev · explained | 34 | 10 |

Named fields correct one compact-input error without introducing a new error. Added explanations lose one case that named fields get right and fix none. The named input's extra correct case does not increase the number of entirely correct groups: another repetition in the same orders/delay group remains wrong.

| Frozen display boundary | Threshold | Displayed / 36 | Incorrect displayed | Withheld |
|---|---:|---:|---:|---:|
| Compact | 0.60 | 33 | 2 | 3 |
| Named | 0.50 | 34 | 0 | 2 |
| Explained | 0.50 | 33 | 0 | 3 |

The named boundary displays 34 correct recommendations and withholds one correct and one incorrect choice. The explained boundary withholds both incorrect choices and one correct choice. Compact input admits both errors, including one exactly at its inclusive 0.60 threshold. These thresholds were selected separately on calibration; their coverage comparison includes that selection as well as the input change. I did not adjust them after evaluation.

### What changed in individual cases

[Orders delay, FMT-49b5cf388bb3](/public-format?split=evaluation&case=FMT-49b5cf388bb3&arm=named#input) is the matched fix. Compact input selects payment at probability 0.60; named fields select the published target, orders, at 0.53. Explained input also selects orders, at 0.67. Change ranking and transferred ML select payment.

The orders `latency-50` record in that case changes from:

```json
[0.038010204, 1.1617647, 670.16632, 0, 0]
```

to:

```json
{
  "before_median": 0.038010204,
  "after_median": 1.1617647,
  "signed_change": 670.16632,
  "before_missing_fraction": 0,
  "after_missing_fraction": 0
}
```

Every other service receives the same transformation. Payment's normalized `latency-90` change is larger than orders', which helps explain the change-ranking result. ML's largest positive payment contribution comes from that latency feature. Jev returns choices and scores, so its response does not establish why field names changed its selection. The workbench lets the reader compare every value, the exact requests and the local score contributions.

[Orders delay, FMT-ebb72cb3ab15](/public-format?split=evaluation&case=FMT-ebb72cb3ab15&arm=named#decision) remains wrong under all three Jev inputs: each selects payment rather than orders. Compact assigns about 0.81 and displays it. Named assigns 0.43 and explained about 0.47, so their frozen boundaries withhold the error. This is a review-boundary improvement without a service-selection fix.

[Payment delay, FMT-a89dbccd5437](/public-format?split=evaluation&case=FMT-a89dbccd5437&arm=explained#input) is the added-explanation regression. Compact and named select payment at 0.80 and 0.58; explained selects orders at 0.48. The explained boundary withholds it. The extra definitions did not consistently help and cannot be credited merely because they sound informative.

### Request size and timing

On evaluation, the provider reports 141,798 input tokens for compact, 194,900 for named and 208,084 for explained input. Named fields use about 37% more input tokens than compact; explanations add another 7% over named. Each arm reports 5,613 output tokens. These are recorded usage totals, not a reconciled bill.

Median client latency is 157 ms for compact, 174 ms for named and 170 ms for explained, with respective 95th percentiles of 225, 223 and 207 ms. Those measurements describe this run; they do not establish a capacity or latency guarantee.

## Interpretation and next experiment

Named fields are the strongest candidate in this comparison: 35/36 correct services and zero observed errors among 34 displayed recommendations. The accuracy gain over compact input is only one case. Twelve correlated groups and one response per arm per case cannot establish a stable improvement or an operational error rate. The extra explanations provide no measured accuracy benefit over named fields.

Named input remains a candidate for further verification. The subsequent [exact-request replay](public-repeatability.md) recorded 180 calls on 12 inspected cases and failed its research gate on named choice and display variability. The 36 Sock Shop reserve cases remain undownloaded. A separate [Train Ticket development comparison](public-temporal-next.md) tests latency windows and analyst shortlists; its findings do not change this study’s frozen inputs, thresholds or held-out results.

The stronger Jev result supports further work on metric-based service recommendations. It does not establish telecom readiness, incident detection or a generally superior model: this study supplies the fault window, covers controlled application faults and compares a transferred ML recipe. Normal periods, ambiguous causes, missing candidates and operational analyst judgments remain separate tests.

Inspect the [input comparison](/public-format) to move from scores to metric evidence, transformations, saved responses and local ML contributions. Browsing makes no hosted calls. The public evidence release includes this study; restore it to inspect the recorded responses.
