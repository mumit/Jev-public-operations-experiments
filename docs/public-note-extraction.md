# Extracting claims from controlled operations notes

## Purpose

The fresh-measurement confirmation judged every supplied claim correctly, but preparation supplied its text and service. This diagnostic tests the missing step: finding a single assertion in a note, assigning its service and meaning, then checking it against recorded facts.

I keep the earlier verdict policy and reuse the nine inspected recordings. No new telemetry opens. Jev, a conservative text parser and a control with supplied annotations receive the same notes. The annotated control measures verdict capacity; its extraction is correct by construction.

## Notes and references

Each note contains six resolvable claims, one claim with an ambiguous service, a compound sentence containing two assertions, and four non-assertions: a heading, requested check, question and unendorsed quotation. There are nine atomic assertions per note, but only six can enter the bounded verdict task. Compound and ambiguous claims require review.

The six routable claims preserve the earlier typed meanings and cover metric magnitude, duration magnitude, incident cause, metric direction, recorded span counts and service health. New prose replaces some explicit names with “the same service,” “this service,” “its” and “that service.” Complete service blocks swap positions by a fixed identity hash. Neither placement nor wording depends on reference verdicts.

I prepared these ordinary-style controlled notes and annotations with the assistant. They are not authentic reports, independent analyst notes or specialist-reviewed references. The recordings are already inspected, so the results cannot establish fresh-data generalization.

## Pipeline

Code marks sentence candidates using punctuation boundaries. Jev receives the whole note and full observed service/channel inventories, without telemetry or annotations. Six independent Choice questions classify each candidate's speech act, service, assertion family, channel, duration measure and polarity. Code combines the replies. Questions cannot see one another's answers. This follows the provider's [typed primitives](https://docs.typesafe.ai/primitives) and [Choice interface](https://docs.typesafe.ai/primitives/choice).

A candidate proceeds only when it is one assertion with a unique service and mapped meaning. Every relevant chosen probability must reach 0.70. A channel is required for a metric claim; a duration measure is required for a duration claim. Unneeded dimensions do not affect acceptance. These probabilities are not calibrated error estimates.

Actual accepted bindings determine a second request: full note, exact candidate text, assigned service and code-calculated ledgers for accepted subjects. The unchanged numerical policy judges supported, contradicted or unanswerable. Display also requires verdict probability of at least 0.70. Incorrect bindings receive no correction from the answer key.

The parser recognizes literal phrases and explicit service names. It has no fitted parameters, probabilities or pronoun resolution. The annotated control supplies correct bindings for the six routable claims. Neither comparator is an additional language model; earlier fitted ML predicts an injected cause and does not answer this extraction task.

## Frozen setup

The first builder produced a 113,081-byte request, exceeding the frozen 79,840-byte cap before any call. Its plan, data and sizing failure remain preserved. A separate v2 builder puts each unchanged task definition once in the state and references it from focused questions. It shortens option descriptions while retaining every service name, sentence and option key. Its largest request is 70,686 bytes.

The plan and producers commit before preparation. The rendered notes, annotations and exact extraction requests commit before 27 calls. Actual extraction responses determine the dependent requests, which receive a separate committed protocol before at most 81 verdict calls. Three rounds measure variation on the same nine notes. Calls run once, without retries, text repair, threshold search or post-result substitution.

The maximum budget is 108 calls and 2,916 answers; acceptance can reduce the verdict budget. No accepted candidates means an explicit application skip, with no invented provider reply. The earlier 22 cause-evaluation recordings, 30 RE3 Sock Shop cases and 140 RE1 reserves remain protected.

## Scoring

Role agreement covers all twelve sentence candidates per note. Service and exact meaning agreement cover all six routable claims, including rejected claims. Meaning requires the correct family, polarity and relevant channel or measure. Assertion precision and recall include the ambiguous single assertion; compound handling is reported separately.

End-to-end correctness requires correct extraction, an accepted binding and the correct verdict. A coincidentally correct verdict for a wrong service fails. Accepted non-assertions or review-only claims count as errors, even if their verdict sounds plausible. Conditional verdict accuracy uses only correctly bound claims that received a reply. Whole-note correctness requires all six routable claims to succeed.

The frozen Jev check requires at least 90% role, service, meaning, accepted-binding and end-to-end agreement in each application and round; at least 90% whole-note correctness; complete calls; no accepted nonclaims or review-only candidates; no unsafe displayed verdicts; and correct display of at least half the reference-supported claims. A missing supported class makes the last criterion unassessable. Passing would not open protected data or establish operational reliability.

## Results

All 27 extraction calls returned. Twenty-five replies pass the frozen validator; two fail because a selected option has lower reported probability than another option. The frozen runner rejects the whole note response when any answer is invalid. The dependent verdict protocol requires complete valid extraction, so it was not created and no verdict calls were made.

| Application | Round | Valid replies | Role agreement | Correct service | Correct meaning | Accepted correct bindings |
|---|---|---|---|---|---|---|
| Train Ticket | 1 | 3/3 | 36/36 | 18/18 | 17/18 | 15/18 |
| Train Ticket | 2 | 3/3 | 36/36 | 18/18 | 18/18 | 18/18 |
| Train Ticket | 3 | 2/3 | 24/36 | 12/18 | 12/18 | 10/18 |
| Online Boutique | 1 | 5/6 | 60/72 | 30/36 | 30/36 | 29/36 |
| Online Boutique | 2 | 6/6 | 71/72 | 36/36 | 36/36 | 35/36 |
| Online Boutique | 3 | 6/6 | 71/72 | 36/36 | 36/36 | 35/36 |

Every planned note and claim stays in its denominator. Rejected replies count as unavailable, not repaired predictions. Across the three rounds, Jev accepts 142 correct bindings out of 162 planned routable-claim opportunities, with no wrong accepted binding or accepted review-only sentence. That is extraction routing, not verdict or display safety.

Among the 25 valid replies, all 150 routable service assignments are correct and 149/150 meanings match. The literal parser accepts only the two explicitly named metric claims per note: 6/18 Train Ticket and 12/36 Online Boutique each round. It resolves no pronouns. Its substring matching also confuses overlapping duration-measure names in two Online Boutique notes; that limitation lowers meaning agreement without changing its accepted explicit-name claims. Jev therefore covers more of these constructed notes than this deliberately conservative parser; added value over a stronger parser or authentic reports remains untested. The supplied-annotation control accepts all six routable claims by construction. No comparator has new verdict results.

### Two response inconsistencies

The [Choice documentation](https://docs.typesafe.ai/primitives/choice) defines the selected choice as the highest-probability option. These two raw answers violate that check:

| Note and round | Question | Selected option | Selected probability | Highest option and probability |
|---|---|---|---|---|
| NEX-8a35465e8421, round 1 | s11_kind, compound assertion | health | 0.34 | unmapped, 0.35 |
| NEX-ca19c97a64d8, round 3 | s05_service, requested check | none | 0.49 | ts-preserve-other-mongo, 0.50 |

Both sentences were intended for review or exclusion, but the frozen whole-response validator also removes their six routable sibling claims. I retain that outcome rather than selecting a new maximum, relaxing validation or salvaging individual fields after inspection. The gaps are 0.01; the recorded evidence does not establish why the API returned them.

### Mapping errors and correct claims withheld

One valid Train Ticket reply classifies “Its recorded span count reaches five in both windows” as health instead of span adequacy. Its minimum relevant probability is 0.60, so the candidate stays in review. Another round maps it correctly but withholds it at 0.68. The subject service is correct in both.

The Online Boutique claim “adservice has an eligible signed latency-90 change that is greater than zero” maps correctly in all rounds, but its minimum relevant probabilities are 0.64, 0.67 and 0.63. It stays withheld throughout. Two compound-role errors also remain in review because their service subject is ambiguous. None of these outcomes justifies lowering the boundary on the inspected notes.

The 27 calls consume 472,881 input tokens; the largest reports 25,570, within the 32,768 context limit. Summed recorded call latency is 8.52 seconds. There are 1,944 raw answers, of which 1,800 belong to fully valid replies. The two rejected raw replies remain available. No new recording opens.

## Interpretation

Jev handles local pronouns and bounded meanings well in the valid replies, while the literal parser loses those claims. The complete experiment is blocked by response validation and has no end-to-end verdict result. The evidence supports further work on bounded note interpretation, with explicit review routing. It does not establish a reliable report-processing workflow.

## Next steps

The next protocol needs a failure-handling choice. I recommend validating each sentence independently: an inconsistent answer sends that sentence to review, while validated sibling sentences may proceed. The alternative retains whole-note review whenever any answer is inconsistent. Both approaches must preserve the raw reply, retain all scoring denominators and avoid replacing the provider's choice with a computed maximum.

That change belongs in a separate frozen protocol. The completed extraction calls will stay unchanged; a new replay on these inspected notes would measure revised integration behavior and variability, not fresh generalization. Keep the 0.70 acceptance boundary fixed and measure the span-adequacy mapping and compound-role errors separately. Verdict comparison can resume only after the new failure policy and exact dependent requests are frozen.
