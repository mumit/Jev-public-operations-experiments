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

## Current status

All 54 calibration calls completed successfully. The frozen rule selects a probability boundary of 0.70 and a margin of zero. It shows 11, 10 and 11 correct leads across the three rounds, with no wrong leads. It withholds 7, 8 and 7 cases, including 1, 3 and 3 correct raw first choices. Display stays the same on 17 of 18 cases.

Without filtering, Jev's first choice matches 12, 13 and 14 of 18 targets. The original three-service shortlist includes all targets but adds 34–35 wrong leads per round. Frozen ML ranks 15 targets first; change and resource rankings each match 10. The perfect development ML result did not carry over to these calibration groups.

Calibration chose the boundary, so its zero-error result is not an independent validation. Evaluation is the next test and uses the committed boundary unchanged. Implementation tests cover competing insufficient-evidence probabilities, alternative support, failures, every-round calibration eligibility, once-only calls, credential redaction and the evaluation download gate.
