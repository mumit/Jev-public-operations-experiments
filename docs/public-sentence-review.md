# Reviewing one sentence while preserving valid siblings

## Purpose

The previous note-extraction protocol stopped before verdict calls because two answers selected an option below their reported probability maximum. Its whole-note validator rejected the other answers in those replies too. I chose sentence-level review for this separate diagnostic.

## Fixed comparison

The nine inspected notes, their 108 sentence candidates, service inventories, task definitions and exact Jev extraction bodies stay unchanged. Three new rounds measure variation on those inspected notes. There are six routable claims and nine atomic assertions per note; ambiguous and compound assertions remain in review.

The new validator checks each independent answer with the earlier strict Choice normalizer. Any missing, malformed or inconsistent answer withholds its entire sentence, including an invalid unused dimension. Valid siblings can proceed if their required extraction probabilities reach 0.70. The raw inconsistent choice stays visible; code never replaces it with the probability maximum or invents missing probabilities.

Wrong models, unexpected answer fields, invalid global reply shape or usage, context overflow and access/network failures stop execution. A reply with valid siblings and quarantined sentences counts as completed work, with lost sentence coverage. It does not count as a correct judgment of the quarantined sentences.

Actual accepted bindings determine the bound-batch verdict requests. The exact text, assigned service and code-calculated fact ledger enter the request without annotation repairs. Verdict display still requires probability at least 0.70. An invalid verdict reviews its sentence while valid sibling verdicts remain usable. The literal parser and supplied-annotation control run alongside Jev.

## What the comparison can establish

The historical whole-note result stays frozen at 142 correct accepted bindings across 162 opportunities, with no verdict calls. Comparing it with the new run also captures response variability.

A separate offline comparison applies the historical whole-note validator to the **same new extraction replies**. That comparison isolates bindings preserved by the validation policy. It makes no extra calls and supplies no counterfactual verdicts.

Role, service and meaning agreement, accepted bindings, conditional verdict accuracy, end-to-end correctness, displayed errors and all-six note correctness retain their full denominators. A correct verdict on the wrong binding fails end-to-end scoring. The earlier research gate stays fixed and applies separately to each application and round.

## Protocol and limits

The source and plan commit before execution. Exact extraction requests commit before 27 once-only calls; actual bindings and dependent requests receive a separate committed protocol before at most 81 verdict calls. Maximum budget: 108 calls and 2,916 answers. No retries, text edits, threshold changes or protected telemetry access.

These are controlled notes with assistant-prepared annotations on inspected public application faults. They do not establish authentic-report performance, specialist-reviewed semantics, causal diagnosis, analyst benefit or telecom readiness. The earlier failed protocols remain available for comparison.

## Results

All 108 calls completed: 27 extraction calls, then 27 verdict calls each for Jev bindings, parser bindings and supplied annotations. Every raw answer passed validation, so no sentence needed validation quarantine in this run. The 2,312 answers comprise 1,944 extraction answers and 368 verdicts.

| Application | Round | Role agreement | Correct service | Correct meaning | Accepted correct bindings and verdicts | All-six notes correct | Wrong displayed verdicts |
|---|---|---|---|---|---|---|---|
| Train Ticket | 1 | 36/36 | 18/18 | 17/18 | 16/18 | 1/3 | 0 |
| Train Ticket | 2 | 36/36 | 18/18 | 18/18 | 16/18 | 1/3 | 0 |
| Train Ticket | 3 | 36/36 | 18/18 | 18/18 | 14/18 | 1/3 | 0 |
| Online Boutique | 1 | 69/72 | 36/36 | 36/36 | 36/36 | 6/6 | 0 |
| Online Boutique | 2 | 71/72 | 36/36 | 36/36 | 35/36 | 5/6 | 0 |
| Online Boutique | 3 | 70/72 | 36/36 | 36/36 | 35/36 | 5/6 | 0 |

Jev accepts 152 correct bindings across 162 claim opportunities. All 152 receive correct, displayed verdicts; no wrong binding, nonclaim or review-only sentence is accepted. The parser accepts 54 claims, judges all correctly and displays 53. Supplied annotations produce all 162 correct, displayed verdicts; their extraction is correct by construction.

Both application research checks fail. Train Ticket falls below 90% accepted-binding and end-to-end coverage in every round, with only one of three complete notes each round. Online Boutique meets the claim-level requirements but loses one complete note in rounds two and three: 5/6 is below 90%. Zero observed displayed errors does not erase those coverage losses.

### Validation policy versus response variation

Both validators accept the same 152 correct bindings on the new extraction replies. The same-reply comparison recovers zero bindings and loses zero. These replies contain none of the inconsistencies that blocked the previous run, so this experiment cannot demonstrate a live recovery benefit from sentence review.

The ten-binding increase from the historical 142 comes from different responses to unchanged questions. It is not an improvement caused by the new validation policy. Negative tests establish that an inconsistent unused field withholds its sentence, preserves valid siblings and never substitutes the probability maximum. Historical rejected replies remain untouched.

### Where claims are lost

The ten missed opportunities all stop at extraction. Every routable service assignment is correct. The limiting fields are speech act, assertion family and, in one overlapping case, polarity.

| Sentence | Observed problem | What a new input should clarify |
|---|---|---|
| `Its recorded span count reaches five in both windows.` | NEX-0865282369d5 selects health at 0.65 in round one; later correct span-adequacy mappings still stay below acceptance. NEX-f7427d20a27f also withholds the correct family at 0.54 once. | A recorded-count statement belongs to span adequacy. It does not assert service health. |
| `ts-travel-mongo has an eligible signed cpu change that is zero or negative.` | Correct mapping throughout, but assertion probability is 0.58/0.61/0.64. Negative polarity also reaches only 0.69 in round two. | A statement of zero or negative change is an endorsed factual assertion. The alternatives describe one property, not two independently checkable claims. |
| `adservice has an eligible signed latency-90 change that is greater than zero.` | Correct mapping throughout, but assertion probabilities of 0.67/0.68 withhold rounds two and three. | Speech-act classification concerns what the note asserts, rather than whether telemetry proves it. |
| `That service is healthy.` | Correct service and meaning, but health probability is 0.66 once. | Health concerns an explicit healthy/unhealthy assertion. Its truth belongs in the later verdict stage. |

Six Online Boutique compound-role mistakes classify two assertions as one. Their unresolved service or meaning keeps them in review; none receives a verdict. These are still extraction errors, even though routing prevents display.

### Cost

| Stage and binding source | Calls | Input tokens | Summed recorded seconds |
|---|---|---|---|
| Extraction, Jev | 27 | 472,881 | 7.49 |
| Verdict, Jev bindings | 27 | 106,626 | 4.62 |
| Verdict, parser bindings | 27 | 74,934 | 4.06 |
| Verdict, supplied annotations | 27 | 110,565 | 4.51 |

The Jev pipeline uses 54 calls and 579,507 input tokens. Its summed call latency is 12.11 seconds; this excludes preparation and verification and is not an end-user latency estimate. No new recording opens.

## Next steps

The next useful diagnostic is a paired change to the speech-act and assertion-family definitions. General examples can distinguish factual assertions from requested checks, negative values from negated speech acts, recorded span adequacy from service health, and compound claims from one property with alternatives. Separate role-only, family-only and combined inputs would show which change helps.

Keep the notes, references, service inventories, verdict policy and 0.70 boundaries fixed. Freeze the new definitions and budget before calls, then report wrong bindings, lost correct claims and complete-note coverage alongside gains. That comparison would be development on inspected notes. Fresh or independently authored notes would still be needed to test generalization.

Sentence-level review is now implemented and tested. The remaining question is whether clearer extraction definitions improve useful coverage without admitting wrong bindings. Lowering the threshold on these inspected failures would answer a different question.
