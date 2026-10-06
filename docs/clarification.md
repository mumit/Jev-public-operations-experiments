# What needs clarification before entering a claim?

I selected a language task after the numerical comparison showed no advantage over exact code. This experiment asks whether Jev can identify which parts of an analyst statement need clarification. Numerical checks remain in code; this study makes no numerical-verdict calls.

## The task

The workflow prepares one explicit metric claim: material absolute scaled change of at least 3.0, positive signed change greater than zero, or either condition's negation. It needs one service, metric, comparison meaning, assertion and before/after incident window. Jev classifies each field as clear or needing clarification. An explicit health, cause, ownership, repair or trace-duration request is outside this task; all entry fields then become not applicable.

For example, “CPU has a material scaled change between the before and after incident windows” specifies the metric, comparison, assertion and window, but omits the service. The next question is “Which observed service does the claim concern?” “Check CPU” also leaves the comparison, assertion and window unresolved. Code retains the full list and asks about the service first.

A clear claim can still lack eligible measurements. That is an evidence limit for the exact evaluator, not a reason to ask what the analyst meant. Jev receives no measurements here and cannot establish whether a statement is true.

## What counts as clear?

| Field | Clear | Needs clarification |
| --- | --- | --- |
| Service | One observed name, or a pronoun with one named antecedent | Missing name, competing antecedents or an undeclared alias |
| Metric | One observed channel or supplied channel alias | Missing metric or alternatives such as CPU or memory |
| Comparison | Material magnitude or positive direction | Vague worsening or a choice between the two meanings |
| Assertion | A condition or its negation, including a yes/no check | Conflicting assertions or a request to choose a condition |
| Window | Explicit selection of the supplied before/after incident comparison | No period selected or a different comparison period |

An explicit final correction supersedes earlier wording. Incidental background services do not make an explicitly named claim subject ambiguous. The contract permits processor utilization/CPU for `cpu` and memory for `mem`; it permits no service aliases.

## Controlled statements and comparators

The pack contains 76 statements: nineteen ambiguity families, two wording variants and two public application inventories. A family is one authored pattern, such as a missing service or conflicting assertion. Its variants and application versions are correlated examples. They are not 76 independent analyst reports.

The statements are newly written, controlled development examples. Only service names and available metric channels come from two previously inspected Train Ticket and Online Boutique packets. No measurements, additional recording, cause label or protected allocation enters the study. Manually declared reference masks freeze with the text before inference. The same assistant writes both; human and independent review counts remain zero.

Jev receives the statement, observed inventory, permitted channel aliases and available window comparison. Six Choice questions assess scope and the five entry fields. Exact requests exclude family names, case identifiers, references and source metadata. A simple parser checks literal service names, metric terms, comparison words, assertion conflicts and window words. It has no learned parameters or model probabilities and uses no reference labels.

Code selects the next action from either method's fields. It asks one question in service, metric, comparison, assertion and window order; explains an outside-task request; or says the wording is ready for the analyst to enter. It does not fill fields or bind an automatic claim.

## Frozen assessment

Three rounds use each statement once, for 228 hosted calls and 1,368 field answers. Jev needs a selected-option score of at least 0.70 for every field. Malformed fields quarantine the whole statement; inconsistent scope/field combinations and low scores require review. Original answers remain visible without repair or retry.

Each application and round has separate overall, clear-statement, clarification-needed and outside-task gates. Every gate requires complete valid classifications, at least 95% correct actions/next questions, at least 90% exact field masks and at least 90% correct displayed actions. No ambiguous statement may display as ready; no displayed question may target an already clear field; no incorrect scope action may display. The assessment also records omitted required fields, unnecessary fields, withholding and paired gains/losses against the parser.

These gates test the declared language contract. Passing would not establish authentic analyst performance, the best question to ask a real operator, correct downstream entries or telecom readiness. Further interpretation claims need new text and a separately frozen protocol.

## First result

All 228 calls returned 1,368 valid field answers, with no quarantines or retries. Jev classified 1,254 fields correctly, matched 140 complete field masks and selected 159 correct workflow actions. Only 73 correct actions passed the six-field display boundary; 137 classifications were withheld. It displayed no premature ready action or wrong scope action, but asked eighteen questions about already clear fields. Every application/round gate failed.

The literal parser matched 192 complete masks and displayed 204 correct workflow actions across the same repeated opportunities. It also displayed six premature ready actions and eighteen unnecessary questions. It fails too. Its deterministic outputs count 76 unique entries, reused across rounds, rather than 228 independent parser trials.

Jev's largest error concentration is comparison meaning: 57 wrong field answers. A conflicting assertion still names one material-magnitude comparison, but Jev repeatedly asks which comparison to use instead of asking about the assertion. A statement selecting last month's window still clearly identifies material magnitude; Jev sometimes asks about the comparison rather than the window. Outside-task scope is always classified correctly, yet separate fields often contradict that scope instead of becoming not applicable. High field accuracy therefore conceals incomplete masks, inconsistent fields and lost workflow coverage.

The paired diagnostic kept the texts, manual references, parser, question options, state and 0.70 boundaries fixed. Fresh unchanged controls ran alongside shorter field-specific instructions. The treatment emphasized that each field's clarity is independent of missing or conflicting information in other fields, except for the existing outside-task rule. It changed instructions only and remains development on inspected text.

## What changed in the Jev input?

The first input repeats the full workflow policy in each of six questions. The treatment keeps the statement, catalog, channel aliases, available comparison, question keys and answer options byte-identical. Only the instruction strings change. Each question receives a shorter definition for its own field and the existing rule that outside-task requests make every entry field not applicable.

For the comparison field, the new instruction explicitly says: “Conflicting positive/negative assertions of the SAME comparison leave this field clear: that conflict belongs to polarity.” It also separates an unspecified or different time window from an explicit comparison meaning. The assertion question describes contradictions and final corrections; the service question distinguishes one pronoun antecedent from competing names. These are request transformations, not examples containing case answers or additional measurements.

Take “For ts-config-service, CPU both has and does not have a material scaled change between the before and after incident windows.” The comparison is material magnitude; the assertion conflicts. Fresh controls ask which comparison to use in all three rounds. Focused classifies the comparison as clear and the assertion as needing clarification in all three, although its full six-field score gate still determines display. The inspector exposes each instruction, answer and score rather than inferring an internal model explanation.

## Paired result

The 456 once-only calls compare fresh unchanged controls with focused instructions, three rounds per arm. Both receive 228 statement opportunities. One response per arm contains a selected option below its reported probability maximum. The frozen validator preserves those responses and quarantines their whole statements; 2,734 of 2,736 raw field answers validate. No retry or repair occurs.

| Method | Exact masks | Correct workflow actions | Correct displays | Withheld | Premature ready | Unnecessary question |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fresh unchanged Jev | 136/228 | 153/228 | 77/228 | 133 | 0 | 18 |
| Field-specific Jev | 184/228 | 200/228 | 112/228 | 113 | 3 | 0 |
| Literal parser | 192/228 | 204/228 | 204/228 | 0 | 6 | 18 |

Focused produces 53 correct display gains and eighteen losses against the fresh control, a net gain of 35. Train Ticket gains 25; Online Boutique gains ten. Every application/round/statement-type gate still fails. Correctly classifying most individual fields does not establish a reliable next action.

The new error is concrete: “recommendationservice called redis. Its CPU has a material scaled change between the before and after incident windows.” The declared contract requires clarification because two service names precede “its.” Focused marks the statement ready in every round, with minimum selected scores of 0.80, 0.77 and 0.72. Its explicit pronoun instruction does not prevent this repeated error. The unchanged control withholds the statement in every round. In round one, the control also calls the service clear, with a score of 0.94. Its minimum field score of 0.53 triggers withholding; focused raises the minimum to 0.80 and exposes the wrong ready action. The control's withheld answer therefore does not demonstrate correct service interpretation.

Focused uses 467,274 input tokens against the control's 679,770, a 31.3% reduction. Summed call latencies are 39.05 and 40.45 seconds; these totals exclude preparation, replay and analyst time. The parser has no hosted calls. Neither method passes the declared workflow contract.

## What this means for the next step

Jev can respond to concrete instruction changes: this treatment separates comparison meaning from assertion conflicts and removes the observed unnecessary questions. It still loses coverage at the fixed six-field boundary and prematurely clears ambiguous wording. The current evidence supports further language research, not a dependable readiness decision or added analyst value.

The next workflow choice is whether to keep pursuing a complete readiness checklist or test an optional clarification assistant beside explicit field entry. I recommend the latter: keep required selections and numerical evaluation in code, let Jev suggest a question, and give the analyst control over whether to use it. This changes the product task and success criteria, so it needs a separately selected contract before further calls. Suggestions still need evaluation for missed ambiguity, unnecessary questions and effort; removing the ready action must not hide those failures.

A new test should freeze unfamiliar wording and references before inference, with a fresh unchanged comparator and a fixed budget. Controlled text can test transfer across wording, but authentic analyst usefulness and independent interpretation still require different evidence. The same assistant cannot supply independent human judgment by producing more fixtures. No protected recording needs to open for this language task.

Inspect [the clarification comparison](http://127.0.0.1:8769/clarification). The page switches between the first diagnostic and paired instructions, shows classifications and withholding, and reveals references only on request. It makes no new model call or server write.
