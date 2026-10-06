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
