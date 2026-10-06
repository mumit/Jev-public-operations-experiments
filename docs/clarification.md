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

The next diagnostic keeps the texts, manual references, parser, question options, state and 0.70 boundaries fixed. Fresh unchanged controls will run alongside shorter field-specific instructions. The treatment emphasizes that each field's clarity is independent of missing or conflicting information in other fields, except for the existing outside-task rule. It changes instructions only and remains development on inspected text.
