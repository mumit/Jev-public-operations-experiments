# When bindings conflict with the sentence

## Question and setup

Does the verdict remain faithful to the original sentence when an upstream service or meaning binding is wrong? The previous assistant-reviewed comparison gave correct displayed verdicts for all 162 claims in every round. That result depended on correct bindings. This diagnostic tests that dependency on the same 27 controlled notes and nine inspected recordings.

Five inputs run in three rounds, with six verdict questions per note: 405 calls and 2,430 answer opportunities. Clean sentence/service and clean explicit-meaning controls reuse the preceding request bodies exactly. Two inputs swap the two confirmed service names; a fifth reverses the supplied polarity in explicit meaning. Text, note context, both service ledgers and numerical policy stay fixed. Selection does not depend on whether a corruption changes the answer.

The primary reference remains the original sentence. A separate diagnostic reference evaluates the altered proposition. Only cases where those verdicts differ can distinguish preservation of the literal verdict from an answer compatible with following the altered binding. Identical verdicts cannot establish correct subject attribution. Direct service names and pronouns receive separate scores, alongside application, wording and round.

The existing question instructs Jev to use the supplied binding. Confident errors against the original sentence would expose a workflow vulnerability; they would not show that Jev disobeyed the request. The test retains the 0.70 display threshold, all missing-answer denominators and every paired loss. No candidate or promotion criterion applies.

## Boundaries

These are deliberately corrupted inputs on same-author notes, not authentic analyst reports. Zero human or independent reviews occurred. Corruption frequency is an experimental condition, not an estimated operational error rate. Repeated wordings and rounds do not add independent incidents. Protected data remains unopened.


## Recorded results

All 405 calls completed, returning 2,430 raw answers. Two inconsistent fields in wrong-service explicit-meaning replies were quarantined, leaving 2,428 valid verdicts. Raw replies remain unchanged; unavailable answers stay in the denominator.

| Application / input | Correct original verdicts, rounds 1–3 | Wrong displayed, rounds 1–3 |
| --- | --- | --- |
| Train Ticket, either clean control | 54, 54, 54 / 54 | 0, 0, 0 |
| Train Ticket, wrong service with sentence | 36, 35, 35 / 54 | 18, 18, 18 |
| Train Ticket, wrong service with explicit meaning | 30, 29, 29 / 54 | 18, 18, 18 |
| Train Ticket, reversed polarity | 54, 54, 54 / 54 | 0, 0, 0 |
| Online Boutique, either clean control | 108, 108, 108 / 108 | 0, 0, 0 |
| Online Boutique, wrong service with sentence | 78, 78, 78 / 108 | 30, 30, 30 |
| Online Boutique, wrong service with explicit meaning | 63, 65, 65 / 108 | 32, 32, 31 |
| Online Boutique, reversed polarity | 108, 108, 108 / 108 | 0, 0, 0 |

The most informative cases have different original and altered references. Wrong-service inputs create 24 such claims in Train Ticket and 48 in Online Boutique per round. Reversed polarity creates 27 and 51. Other claims have identical verdicts despite the corruption; a correct answer there cannot prove correct binding.

### Service errors survive the display threshold

Every divergent pronoun claim matches the wrong-service reference under both corrupted inputs: 18/18 in Train Ticket and 30/30 in Online Boutique, in every round. All these wrong original-sentence verdicts display at the fixed 0.70 threshold. Model confidence therefore fails to catch this deliberately introduced attribution error.

For example, the plain Train Ticket note NWL-6a1a2c127a1d says, “For that service, each recorded window contains at least five spans.” The antecedent is ts-preserve-other-mongo, whose trace mapping is missing, making the original claim unanswerable. The corruption binds it to ts-config-service, whose recorded counts exceed five. The sentence-input answer becomes supported. Both ledgers and the complete original note remain available.

Direct service names behave differently. Sentence/service input preserves the original verdict on all divergent named claims: 6/6 in Train Ticket and 18/18 in Online Boutique per round. Explicit meaning preserves only 0/1/0 of the six Train Ticket claims and 6/7/7 of the eighteen Online Boutique claims. Most of these additional errors are withheld, but one or two Online Boutique errors display per round. Adding asserted structure provides no protection against the wrong subject in this diagnostic.

### Polarity conflict does not produce verdict errors here

Every divergent reversed-polarity claim retains the original sentence verdict in all rounds. No answer matches the reversed proposition on those cases. This is evidence that the original text remains influential for these controlled polarity conflicts; it does not reveal Jev’s internal reasoning or establish tolerance of other meaning errors.

Online Boutique withholds 6/5/4 correct verdicts across the complete 108-claim panel, versus zero under the clean control. Train Ticket displays all 54. Correctness alone would miss this loss of useful coverage.

### What this changes

Correct reviewed bindings still support perfect verdict performance on these notes. Incorrect service bindings can produce confident, repeatable errors, especially when the sentence uses a pronoun. The verdict threshold checks the answer distribution, not whether an upstream subject assignment was sound.

The study changes the entire set of six bindings per note, rather than introducing one isolated organic extraction mistake. Same-author notes, repeated recordings and artificial corruption limit what the counts establish. The previous instructions treat the binding as authoritative, so the result concerns the reliability of the full workflow when that authority is wrong.

## Next experiment

The next comparison should make the conflict explicit: ask Jev to check the supplied subject against the full note before judging the claim, with a separate unresolved/conflict outcome. It should include matched clean controls, wrong-service inputs, direct names and pronouns. A separate protocol must freeze the wording, references and budget before calls. Success would require fewer wrong displayed verdicts without silently replacing the supplied subject or losing clean-case coverage. This would remain a diagnostic on inspected notes; fresh or independently written reports would still be needed to assess transfer.

[Inspect the recorded requests and answers](http://127.0.0.1:8769/binding-corruption).

The subsequent [subject-check comparison](subject-check.md) catches most wrong-subject displays, but fails overall because Online Boutique loses clean coverage and still displays one corrupted-subject error. The earlier corruption results remain frozen.
