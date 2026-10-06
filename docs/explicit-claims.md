# Explicit claims: Jev versus an exact policy evaluator

I selected explicit analyst-entered claims after automatic report reading produced wrong bindings. This workflow asks the analyst to choose the service, observation window, claim type, assertion and applicable metric or duration measure. The selected fields define the claim. The app generates its wording and shows the facts used to check it.

## What this changes

An example entry is: service `emailservice`, type `metric_material`, channel `cpu`, assertion `true`. That asks whether the absolute scaled CPU change reaches 3.0. An assertion of `false` asks whether it stays below that threshold. Missing or ineligible observations make either assertion unanswerable.

Jev receives those fields, the selected raw facts and the fixed policy. It returns supported, contradicted or unanswerable. The exact evaluator computes the same policy directly. Neither arm reads a report or selects a service on the analyst's behalf. Health and incident causality remain unanswerable under this measurement policy.

The preview makes no hosted call and saves no server-side entry. Its export is a local draft. It is not an independent review or a new Jev response.

## Frozen experiment

Development contains 216 claims on eighteen service observations from nine previously inspected public recordings, plus 34 constructed boundary fixtures. Each claim type appears in both assertion polarities. The fixtures cover inclusive thresholds, decreases, zero direction, missing values, span coverage and an invalid duration starting value.

Confirmation is conditional on development passing. Its fifteen untouched Online Boutique recordings form three whole service/fault groups from RCAEval RE1. Fixed hashes select the groups, two observed services per recording and their metric names. Cause labels and reference answers never enter requests. This panel supplies metrics without traces, so it cannot validate duration decisions on fresh traces.

Three rounds use each exact claim once per round. Jev must complete every call, answer at least 95% correctly, display at least 90% correctly and display no wrong answer at the unchanged 0.70 score boundary, separately for each application and round. Policy fixtures have their own gate. The exact evaluator must match every reference. A displayed unanswerable answer explains an evidence limit; it is not a service recommendation.

Earlier reference code implements the measurement policy separately from the new evaluator. Hand-specified fixtures cross-check that code. Both implementations and the controlled entries come from the same assistant. They establish implementation agreement, not independently reviewed operational truth.

## Preparation and scope

A metric or duration claim requires four field choices; another claim requires three, in addition to selecting the source window. These counts describe the form, not elapsed analyst effort. The experiment has zero human entries or independent reviews. Correct field entry is a supplied assumption shared by both arms.

The earlier protected panels stay unopened. This study does not establish automatic report understanding, anomaly detection, root-cause ranking or production readiness. Results will determine whether Jev adds value to this narrow numerical task and which evidence is still missing.

## First result

All 750 calls returned valid answers. Jev answered 629 correctly (83.9%), displayed 450 correct answers and displayed nine wrong answers. The exact evaluator matched all 750 policy references. Every application and boundary-fixture gate failed. Confirmation therefore stays unopened.

The new typed format and general policy instructions performed worse than the earlier correctly supplied bound-text control. That comparison changes the claim set, grouping and input representation; it does not show that explicit entry itself causes the loss. The current entries include both polarities and additional boundary cases.

The next diagnostic will keep the fields, observations, references and 0.70 display rule fixed. A narrower request will state the selected assertion directly and include only its relevant policy rules, against fresh unchanged typed-format controls. This tests a request transformation on inspected data, without advancing the failed format to fresh confirmation.

## Request transformation result

Fresh unchanged typed controls repeated the weakness: 626 of 750 answers were correct, with nine wrong displays. The focused request gave 733 correct answers and 701 correct displays, but still displayed three wrong answers. Calculated facts gave 750 correct answers and correct displays, with no wrong displays. Every calculated-input panel passed.

| Input | Correct answers | Correct displays | Wrong displays |
| --- | ---: | ---: | ---: |
| Fresh general typed control | 626/750 | 452/750 | 9 |
| Focused statement and relevant policy | 733/750 | 701/750 | 3 |
| Focused statement plus calculated facts | 750/750 | 750/750 | 0 |
| Exact evaluator, same unchanged claims | 750/750 | 750/750 | 0 |

For the below-threshold duration fixture, the raw values are 100 and 124.999 microseconds. The focused statement says that the absolute relative change is at least 0.25. Calculated input adds `observations_eligible: true`, `relative_change: 0.24998999999999996` and its absolute value. It does not add the reference answer or the truth of the selected assertion. Jev then judges the comparison correctly.

The calculated input gains 298 correct displays against contemporary typed controls and 49 against focused inputs, with no losses on this development set. Each arm makes 750 calls. Input-token totals are 544,800, 397,842 and 438,672 respectively; summed provider latency is about 109 seconds per arm. These are repeated calls on 250 claims from nine inspected recordings and constructed fixtures, not independent incidents.

The useful transformation is concrete: generate a direct comparison from the selected fields, include only its relevant policy, preserve missingness, and compute eligibility and arithmetic in code. The focused step changes wording, state and policy scope together, so this study cannot attribute its gain to one change. The calculated step adds only derived facts and their explanation to the focused request. Its success demonstrates assisted policy checking. The exact evaluator already supplies the verdict without a model call, so this does not establish extra value from Jev for numerical policy execution.

A new confirmation protocol will use another three unallocated RE1-OB groups. The first experiment's fifteen-recording allocation stays unopened. Fresh metrics can test transfer of the frozen calculated input, while actual analyst entry errors, effort and usefulness require a person using the workflow.
