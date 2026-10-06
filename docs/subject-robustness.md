# Check what context selection removes

The latest-service excerpt fails the controlled challenges. It sometimes removes the statement needed to identify the subject, then Jev confidently resolves a different service. Full notes avoid that particular loss but retain other errors, including treating quoted health statements as endorsed assertions.

## Setup

Fifteen patterns each have nine examples, using complete service inventories from nine inspected recordings. Full-note, prefix and excerpt inputs share the same one-question subject task and fixed 0.70 eligibility boundary. Only their literal text differs. Three rounds produce 1,215 calls and raw answers; one inconsistent reply leaves 1,214 valid answers. No numerical evidence or cause labels enter these requests.

Cards, references, producers and the exact protocol were committed before calls. The text and references were also frozen before inspecting the preceding excerpt study's outcomes. The patterns cover explicit names, pronouns, request antecedents, negation, service changes, quotations, questions, ambiguity, missing subjects, later clarification, outside-inventory subjects and compound assertions.

Two references distinguish the subject identified by the complete note from the subject justified by the supplied context. Removing the only disambiguating statement makes `unresolved` correct for the reduced input. A lucky guess that matches the complete note still counts as unsupported. Correct withholding can nevertheless lose useful original information.

Eligibility means a resolved service with probability at least 0.70. It is not a numerical verdict or analyst recommendation. “Safe original subject” requires agreement with both references; its denominator includes all originally resolvable subjects.

## Results

Each cell reports rounds 1 / 2 / 3. Train Ticket has 45 subject opportunities per round; Online Boutique has 90.

| Application | Context | Correct for supplied text | Unsupported eligible choices | Safe original subjects |
| --- | --- | --- | --- | --- |
| Train Ticket | Full note | 39 / 39 / 39 | 3 / 3 / 3 | 26 / 26 / 27 |
| Train Ticket | Prefix | 39 / 39 / 39 | 3 / 3 / 3 | 23 / 23 / 23 |
| Train Ticket | Excerpt | 36 / 36 / 36 | 9 / 8 / 7 | 18 / 18 / 18 |
| Online Boutique | Full note | 78 / 78 / 77 | 6 / 6 / 6 | 49 / 50 / 49 |
| Online Boutique | Prefix | 75 / 76 / 76 | 6 / 6 / 6 | 41 / 42 / 41 |
| Online Boutique | Excerpt | 74 / 74 / 73 | 12 / 12 / 12 | 33 / 31 / 31 |

Originally resolvable subjects total 30 per Train Ticket round and 60 per Online Boutique round. The excerpt fails both application gates. Its safe-subject losses against full notes are 11/11/12 for Train Ticket and 23/25/24 for Online Boutique, alongside gains of three and 7/6/6 respectively. Gains do not erase the losses.

## Inspect an information-removal failure

The complete note in `RSC-9780eea6c8b1` says:

```text
My current assessment concerns adservice.
Is shippingservice healthy?
The service in my current assessment has enough recorded spans.
```

The last sentence explicitly refers to the current assessment. In round one, full-note and prefix calls select `adservice` at 0.82 and 0.85. The excerpt starts at the question about `shippingservice`, removes the current-assessment anchor and selects `shippingservice` at 0.85. Its supplied context justifies `unresolved`. This is a confident unsupported resolution, not a successful context reduction. [Inspect the three actual inputs](http://127.0.0.1:8769/subject-robustness?dataset=Online+Boutique&family=question_interruption&card=RSC-9780eea6c8b1&arm=excerpt&round=1#inspect).

Every excerpt in the question-interruption family fails its visible-subject reference in every round. Quoted targets also fail in all three contexts and rounds: Jev resolves the quoted service instead of selecting `unresolved`. Conversely, explicit service switches benefit from the excerpt; full and prefix calls get none of those subjects correct. Ambiguous pairs, missing anchors, outside-inventory subjects and compound targets are correctly unresolved throughout. The failures depend on discourse structure, not simply input length.

One full-note round-three reply for `RSC-4bfd2ebcd311` selects `shippingservice` at 0.41 while `unresolved` has 0.42. Validation quarantines that sentence without changing the choice or retrying. The raw distribution remains inspectable.

## Cost and implication

Each context makes 405 calls. Full, prefix and excerpt inputs consume 588,429, 587,763 and 586,413 input tokens respectively. Excerpt savings are about 0.3%, with summed call latency of 68.92 seconds versus 69.30 for full notes. These totals do not measure end-to-end latency or establish a meaningful speed advantage.

Latest-name truncation cannot serve as a general subject-reading policy on this evidence. The [complete-workflow comparison](full-workflow.md) therefore retains full notes and separately measures extraction, accepted fields and numerical checking.

The same assistant wrote the text and references. These are constructed challenges on inspected inventories, with zero human or independent reviews and no new recordings. Repeated examples and rounds are correlated. Results establish neither authentic-report performance nor network cause accuracy, anomaly detection or operational reliability. All protected panels remain unopened.
