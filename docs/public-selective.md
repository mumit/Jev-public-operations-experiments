# Fewer investigation leads, with explicit withholding

## Preference and experiment

I chose a more selective advisory policy: fewer wrong leads, accepting more withholding. The named-input development result motivates that choice. Jev ranked the published cause first in 16 of 18 cases per round, while its three-service shortlists added 32–34 extra leads. Timing windows did not improve the result.

The next comparison keeps the named measurements, cause-selection question and all observed services unchanged. Only the display policy changes. No ML refitting or new prompt is involved.

## How display works

A recommendation must meet a selected-probability boundary and a margin boundary. The margin is the selected probability minus the largest competing option probability, including insufficient_evidence. An insufficient-evidence choice, failed call or missing response always withholds.

Calibration tests probability boundaries of 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99 and 1.00, with margins of 0, 0.10 and 0.20. These values are frozen before new data. They are model-output scores, not verified probabilities that the diagnosis is correct.

The main policy shows at most one service. A fixed two-service comparator adds the strongest alternative only when its probability reaches 0.20 and half the first service's probability. That rule measures the cost and inclusion benefit of alternatives; it does not establish causal support. The original up-to-three shortlist remains another comparison.

The benchmark publishes one injected cause per case, so a two-service list always contains at least one extra lead under this scoring rule. An extra lead could still be diagnostically useful in practice. These data cannot measure that value or analyst time.

## Calibration and evaluation

The existing grouped assignments provide 18 calibration cases in six groups, 36 evaluation cases in twelve groups and 18 reserve cases. Three serial rounds produce 54 calibration and 108 evaluation calls. Repeated responses measure display variability; they do not create additional independent cases. The older 36-case Sock Shop reserve stays unopened.

A qualifying single-lead policy must show at least one recommendation in every calibration round and show zero wrong leads in all three. Selection maximizes the lowest correct-display count across rounds, then total correct displays, then stable per-case display. Lower probability and margin boundaries break remaining ties. If no policy qualifies, evaluation stays unopened.

The calibrated boundary must reproduce and be committed before evaluation telemetry is downloaded. Evaluation applies that boundary unchanged. The comparison records shown correct and wrong leads, withheld cases, correct choices lost to withholding, cause inclusion, repeated display consistency and the unchanged ML/change/resource controls. All recommendations require analyst review.

Zero observed calibration errors do not establish a production error rate. These are controlled application faults with supplied incident boundaries, published injected-service references and unknown pretraining exposure, not telecom reports.

## Calibration result

All 54 calibration calls completed successfully. The frozen rule selects a probability boundary of 0.70 and a margin of zero. It shows 11, 10 and 11 correct leads across the three rounds, with no wrong leads. It withholds 7, 8 and 7 cases, including 1, 3 and 3 correct raw first choices. Display stays the same on 17 of 18 cases.

Without filtering, Jev's first choice matches 12, 13 and 14 of 18 targets. The original three-service shortlist includes all targets but adds 34–35 wrong leads per round. Frozen ML ranks 15 targets first; change and resource rankings each match 10. The perfect development ML result did not carry over to these calibration groups.

Calibration chose the boundary, so its zero-error result is not an independent validation. Evaluation is the next test and uses the committed boundary unchanged. Implementation tests cover competing insufficient-evidence probabilities, alternative support, failures, every-round calibration eligibility, once-only calls, credential redaction and the evaluation download gate.

## Untouched evaluation result

All 108 evaluation calls completed successfully. The 36 cases belong to twelve previously unopened service/fault groups. The 0.70 probability boundary and zero margin stayed unchanged.

| Display policy | Correct first choice per round | Published cause included per round | Extra wrong leads per round | Withheld cases per round |
|---|---:|---:|---:|---:|
| Calibrated one lead or withhold | 21, 19, 22 | 21, 19, 22 | 0, 0, 0 | 15, 17, 14 |
| Unfiltered first choice | 30, 30, 30 | 30, 30, 30 | 5, 5, 5 | 1, 1, 1 |
| Fixed supported alternative | 30, 30, 30 | 33, 34, 33 | 6, 6, 7 | 1, 1, 1 |
| Original up-to-three shortlist | Not a first-choice display policy | 35, 35, 35 | 63, 62, 64 | 1, 1, 1 |

The selective rule removes every observed wrong first choice, but also withholds 9, 11 and 8 correct first choices. It provides a correct lead for roughly 53–61% of cases. This is improved precision of displayed output, not improved model accuracy. One case chooses insufficient evidence in all rounds; its exclusion is distinct from withholding a selected service below 0.70.

Unchanged ML ranks 28/36 causes first, change ranking 27/36 and resource ranking 25/36. Their first-three inclusion counts are 31, 32 and 30. They have no new display calibration, so comparing their unfiltered choices directly with Jev's selective display rate would conceal the coverage difference. Jev's 30/36 unfiltered result is slightly higher here; ML's earlier perfect development result was specific to those six groups.

Display stays identical on 33/36 cases. The remaining three are correct first choices that cross the boundary. For `TMP-ac37c4d350a2`, Jev selects train-service every time, with probabilities 0.6869, 0.64 and 0.71. The policy withholds the first two responses and shows the third. The other crossings involve route-service memory and socket cases. Exact requests still do not guarantee a stable analyst-facing recommendation.

The strongest remaining errors are delay cases: two train-service and two travel-service cases rank admin-travel first in every round. All stay below 0.70. An order-service loss case selects preserve, also below the boundary. This observation identifies failures to inspect; it does not justify changing the threshold on evaluation data.

## What this says about Jev

On this held-out panel, Jev can supply selective, analyst-facing service recommendations from named metric summaries. The calibrated rule avoids observed wrong leads at a substantial coverage cost. It is not ready for automatic routing: the study supplies incident boundaries, has few correlated fault groups, and leaves investigation time and real incident accuracy unmeasured.

The remaining 18 Train Ticket reserve cases and 36 Sock Shop reserve cases stay undownloaded. The recommended next experiment keeps the input and 0.70 boundary fixed, tests new groups, and reports display stability alongside precision and lost coverage. The separate [reserve confirmation](public-confirmation.md) tests that policy under a protocol committed before telemetry download; this selective evaluation remains unchanged. Any attempt to recover withheld cases through a new transformation or ML fallback needs a separate development/calibration protocol. These inspected evaluation cases cannot select the next boundary.

Inspect [the selective workbench](http://127.0.0.1:8769/selective) for per-case probabilities, the competing-option gap, display reasons, published references and the unchanged input.
