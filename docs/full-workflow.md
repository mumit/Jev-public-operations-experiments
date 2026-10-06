# Compare the complete note workflow with supplied claim fields

Correct supplied fields let Jev check every claim correctly in this comparison. Automatic report reading loses claims and produces five unsafe displays across three rounds. The frozen literal parser accepts none of the six routable claims correctly and also produces unsafe displays. The automatic candidate fails both application gates.

## Setup and actual inputs

Each of 27 controlled notes contains twelve sentence candidates and six routable claims. The same nine inspected recordings supply observations. Three workflows receive fresh replies:

- **Automatic:** the unchanged family-only extraction request asks Jev for role, service, assertion kind, channel, measure and polarity for every sentence. Full note context and complete inventories remain available. Validated fields determine the actual dependent verdict questions.
- **Parser:** the earlier frozen literal parser supplies its accepted fields without fitting or probabilities. Jev assesses those actual fields; the parser receives no reference repairs.
- **Trusted-field control:** the committed assistant review supplies the six correct claims and fields. Jev receives the exact clean bound-text numerical request. Selection and field correctness are correct by construction; this control does not measure extraction, analyst effort or human review.

Required extraction probabilities and the numerical display boundary remain 0.70. An invalid dimension quarantines its entire sentence, preserving valid siblings. Wrong accepted fields fail complete-workflow scoring even if the numerical verdict happens to match the original claim. Accepted quotations and other nonclaims also count as unsafe when displayed.

The initial protocol froze 81 automatic extraction calls and 81 trusted-field verdict batches before inference. A second protocol then froze the **actual** validated extraction outputs, parser bindings and dependent request hashes before numerical calls. All 81 automatic notes and 27 parser notes received verdict calls; 54 empty parser selections created recorded skips. Total: 270 provider calls, 6,813 raw answers and 6,812 valid answers. No retries, answer repairs or threshold changes occurred.

This compares complete workflows, including preparation and grouping. It cannot attribute every difference to one input change. Earlier context diagnostics remain separate subject-only or reviewed-claim comparisons.

## Results

Each cell reports rounds 1 / 2 / 3. Train Ticket has 54 routable claims in nine notes per round; Online Boutique has 108 in eighteen notes. Correct complete-workflow claims require correct accepted fields and a correct numerical verdict.

| Application | Workflow | Correct complete-workflow claims | Safe displays | Unsafe displays | All six claims correct per note |
| --- | --- | --- | --- | --- | --- |
| Train Ticket | Automatic | 53 / 51 / 50 | 53 / 51 / 50 | 0 / 1 / 0 | 8 / 7 / 6 of 9 |
| Train Ticket | Trusted fields | 54 / 54 / 54 | 54 / 54 / 54 | 0 / 0 / 0 | 9 / 9 / 9 |
| Train Ticket | Parser | 0 / 0 / 0 | 0 / 0 / 0 | 6 / 5 / 6 | 0 / 0 / 0 |
| Online Boutique | Automatic | 94 / 96 / 92 | 94 / 96 / 92 | 2 / 0 / 2 | 7 / 9 / 7 of 18 |
| Online Boutique | Trusted fields | 108 / 108 / 108 | 108 / 108 / 108 | 0 / 0 / 0 | 18 / 18 / 18 |
| Online Boutique | Parser | 0 / 0 / 0 | 0 / 0 / 0 | 12 / 12 / 12 | 0 / 0 / 0 |

Every correctly accepted automatic binding receives a correct displayed numerical verdict: 436 across 486 repeated claim opportunities. Extraction and acceptance account for the missing correct claims. Four wrong bindings and one nonclaim nevertheless clear the gates and display. Whole-note correctness exposes losses that an aggregate claim percentage conceals.

The parser is a narrow historical template matcher, not a representative limit on rule-based processing. Its accepted negated claims have incorrect meanings; it also accepts archived attributions. Plain and boundary notes yield empty selections. Its failure argues against reusing this particular parser, not against deterministic evaluation of explicitly supplied fields.

## Follow a wrong interpretation

In `NWL-fe6c9911a37a`, sentence `s03` says:

```text
For redis, the eligible signed cpu change is not zero or negative.
```

The reference interprets this as positive change. Automatic extraction chooses negative polarity with minimum required probability 0.72 in round one and 0.74 in round three. Those wrong fields are accepted and proceed to numerical checking. Even a coinciding verdict cannot make the wrong interpretation safe. The trusted-field control supplies positive polarity and checks the intended claim correctly. [Inspect extraction, actual fields and verdicts](http://127.0.0.1:8769/full-workflow?dataset=Online+Boutique&wording=negated&card=NWL-fe6c9911a37a&arm=automatic&round=1&sentence=s03#inspect).

Another error accepts the sentence “The previous ticket attributed the incident to recommendationservice, but this note does not adopt that attribution.” as a current assertion. Two metric-direction claims are classified as span adequacy in separate application/round combinations. These failures show why a numerical verdict alone cannot validate the report-reading pipeline.

An Online Boutique boundary-note reply selects a kind below its distribution maximum for `NWL-0f527b766ed7`, `s06`, round one. That sentence remains quarantined; valid siblings continue. The raw choice is preserved without argmax repair or a replacement call.

## Cost and next decision

Automatic extraction and verdicts use 162 calls, 1,747,634 input tokens and 37.98 seconds summed call latency. Trusted-field checking uses 81 calls, 332,187 tokens and 14.76 seconds. The parser's 27 verdict calls use 75,351 tokens and 4.55 seconds, while producing no correct complete-workflow claims. Summed call latency excludes preparation, user effort and end-to-end execution time.

The strongest bounded evidence supports numerical claim checking after correct selection and interpretation. It does not establish ordinary-report reliability. All notes and references come from the same assistant; there are zero human or independent reviews and no new recordings. None of the results establishes authentic-report performance, incident detection, cause accuracy or telecom readiness.

The [task-fit assessment and remaining plan](operations-fit.md) explains the next product decision. All protected panels remain unopened.
