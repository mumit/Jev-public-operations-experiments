# Confirm the selective policy on untouched reserves

The user selected confirmation of the existing selective policy. This experiment consumes the remaining 18 Train Ticket and 36 Sock Shop reserve cases under a separate protocol committed before download. Their service/fault repetition groups remain intact: six Train Ticket groups and twelve Sock Shop groups.

The named input, cause-selection question, all observed candidates, Jev version and fitted ML stay unchanged. Every call uses the same 0.70 probability display boundary, zero required margin, and at most one lead. Insufficient-evidence choices, failures and missing responses withhold. The protocol performs no threshold search, calibration, prompt changes, candidate filtering or refitting.

Three serial rounds make at most 162 calls. Each application is scored separately for first-choice correctness, shown correct/wrong leads, coverage, correct choices lost to withholding, and repeated display consistency. The unfiltered first choice, fixed supported alternative, original up-to-three shortlist and unchanged ML/change/resource controls remain visible.

The preceding evaluation has complete evidence, nonempty selective coverage and zero observed wrong displayed leads in every round. That gate permits confirmation; it does not guarantee another zero-error result. Any failure stays in the report. Reserve cases become inspected once downloaded and cannot subsequently serve as fresh validation for a changed policy.

These public application faults supply incident boundaries and injected-service references. They do not establish telecom readiness, investigation benefit or an operational error guarantee. Repeated calls are not independent incidents.

## Confirmation results

All 162 calls completed successfully. The named input and 0.70 display boundary stayed unchanged. Both reserve panels are now inspected; these cases cannot validate a later policy change.

| Application and method | Correct first choice per round | Wrong shown leads per round | Withheld cases per round |
|---|---:|---:|---:|
| Train Ticket, frozen one-or-withhold | 11, 10, 11 out of 18 | 1, 1, 1 | 6, 7, 6 |
| Train Ticket, unfiltered Jev | 15, 15, 15 out of 18 | 3, 3, 3 | 0, 0, 0 |
| Sock Shop, frozen one-or-withhold | 27, 27, 27 out of 36 | 0, 0, 0 | 9, 9, 9 |
| Sock Shop, unfiltered Jev | 36, 36, 36 out of 36 | 0, 0, 0 | 0, 0, 0 |

On Train Ticket, withholding removes two of the three wrong first choices but retains the same error in every round. It also removes 4, 5 and 4 correct first choices. Display remains stable on 15/18 cases. Frozen ML ranks 16/18 causes first; change and resource rankings each match 10.

On Sock Shop, every unfiltered Jev first choice is correct. The selective rule adds nine withheld correct choices without avoiding an error in this panel. All 36 display decisions stay stable. ML and change rankings each match 34/36 first; resource ranking matches 27.

These application results differ materially. Combining their scores would obscure the Train Ticket failure and the Sock Shop coverage cost. Repeated wrong responses are one persistently wrong case, not three independent faulty incidents.

## The confidently wrong lead

In `TMP-80d015d089a4`, the published injection is route-service network loss. Jev chooses admin-travel in every round, with normalized choice probabilities 0.8081, 0.8081 and 0.8182. All pass the frozen boundary.

Route-service latency-90 changes from 0.005119 to 0.128008, with a baseline-scaled shift of 77.8536. Admin-travel latency-90 changes from 0.235 to 0.8875, with a shift of 277.6596. The change ranking also selects admin-travel. ML selects route, ranking admin-travel second. The shared metric evidence contains a competing symptom pattern; the largest shift does not establish the originating service. This explains what evidence to inspect, not the provider's internal reason for its choice.

The inspection view shows when Jev and ML disagree. It does not silently change the frozen display rule. On this inspected panel, an agreement requirement would withhold the erroneous Train Ticket lead and one correct shown lead per round. Sock Shop has no disagreement among its 27 shown leads. That observation motivates a new hypothesis; it is not fresh validation of a new filter.

## Interpretation and next decision

The zero-wrong-lead result from the earlier evaluation did not reproduce on Train Ticket. A probability boundary reduces displayed errors here, but cannot reliably remove confident causal mistakes. Jev remains a candidate for analyst-facing suggestions with explicit uncertainty and review. This evidence does not support automatic routing or treating its probabilities as diagnostic confidence.

The next experiment needs fresh cases and a separately frozen protocol. I recommend testing Jev/ML disagreement as a reason for analyst review, with the lost correct coverage reported explicitly. The other direction is richer causal evidence, such as traces or dependency context, to help Jev distinguish origin from propagated symptoms. The inspected reserve failure can guide that design but cannot evaluate its success.

Inspect [Train Ticket confirmation](http://127.0.0.1:8769/selective?split=train-ticket-reserve&case=TMP-80d015d089a4&round=1#inspect) and [Sock Shop confirmation](http://127.0.0.1:8769/selective?split=sock-shop-reserve#overview).

