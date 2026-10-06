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

## Preserved preparation failures

Three separately frozen preparations downloaded fifteen recordings each, then stopped before producing claim inputs, references, a request protocol or hosted calls. All source bytes and failure audits remain preserved.

1. The older adapter rejected native `load` and `latency` names.
2. The first native adapter rejected `workload` in later groups. The next version retains the original known-channel allowlist plus `load` and `latency`, with no aliases.
3. The complete allowlist reached a recording with 63 timestamps, all before the declared injection time. Its last timestamp is 1685371799; the injection time is 1685373255. There are no post-incident rows to compare.

The forty-five downloaded recordings are now opened, even though no Jev confirmation ran. None can be relabeled untouched. The first experiment's separate fifteen-recording allocation and all earlier protected panels remain unopened.

The preparation failure required a choice between retaining the incomplete recording as missing evidence and replacing its entire service/fault group. The user selected retention. The new contract below leaves the absent after-window unknown and makes both assertion polarities unanswerable; completed results and failed producers remain unchanged.

Retaining missing evidence tests a condition an operations workflow must handle without inventing measurements. This remains a controlled public-data experiment. Actual analyst accuracy, preparation time and usefulness require someone using the form; the current fixtures cannot measure them.

## Selected missing-window confirmation

The selected treatment retains the incomplete recording. A new frozen protocol reuses the fifteen already downloaded native-v2 recordings, without opening more data. Absent windows have unknown duration, medians, missing fraction and change. Their actual row count remains zero; that count does not establish a measured metric or a recorded span count. Both assertion polarities remain unanswerable when evidence is ineligible.

The focused and calculated requests, numerical policy, independent reference implementation and 0.70 display boundary stay unchanged. Three rounds across 360 claims require 2,160 calls. Separate gates cover all claims, complete windows, the missing window, complete-window metric comparisons and complete-window other kinds. Every gate requires complete valid replies, at least 95% accuracy, at least 90% correct displays and zero wrong displays. Exact computation must agree with all references.

Schema and window coverage were inspected during failed preparation. This is post-preparation confirmation on previously downloaded recordings, not wholly untouched validation. The historical failures remain preserved; the original fifteen-case allocation and all earlier protected panels stay unopened.

## Confirmation result

All 2,160 calls returned valid answers. Focused and calculated inputs each answered and displayed all 1,080 verdicts correctly, with no wrong display. Both passed every gate in all three rounds. The exact evaluator matched every reference without a hosted call.

| Panel, per arm and round | Correct answers and displays | Wrong displays |
| --- | ---: | ---: |
| All claims | 360/360 | 0 |
| Complete windows | 336/336 | 0 |
| Metric comparisons on complete windows | 112/112 | 0 |
| Other claim kinds on complete windows | 224/224 | 0 |
| Missing-window recording | 24/24 | 0 |

These panels overlap. The incomplete recording contributes 24 distinct claims and 72 answers per arm across three rounds; both polarities remain unanswerable. All fourteen complete recordings retain exactly the earlier adapter's aggregate values. No onset, row or channel was repaired.

Of the 360 distinct claims, 56 are supported, 56 contradicted and 248 unanswerable. The missing eight metric comparisons and all 240 duration, span, health and causality claims are unanswerable under the supplied evidence. There are no traces in this panel. Its many evidence-limit answers do not establish duration arithmetic or incident-cause understanding; the separate 112-claim complete-metric gate also passes.

Calculated input gained and lost zero displays against focused input. Each arm made 1,080 calls; focused consumed 569,472 input tokens and calculated 625,320, about 9.8% more. Summed call latency was 176.68 and 176.08 seconds respectively, excluding preparation and human time. The earlier boundary-fixture advantage remains recorded, but it did not recur on these measurements.

The experiment confirms consistent application of this bounded policy, including missing evidence, after schema and window inspection. It does not show additional utility over exact computation. I will keep numerical checks in code. Further Jev work needs a language task with a separately frozen reference policy, or a participant to measure actual claim-entry effort. The recommended next language task is identifying what needs clarification before an ambiguous analyst statement becomes an explicit entry. That task has not been selected or tested.
