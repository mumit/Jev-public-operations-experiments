# Optional clarification alongside required entry

I selected an optional clarification assistant after the readiness study improved coverage but exposed a repeated ambiguity error. Jev now suggests one question. Every required field still needs an explicit analyst selection, and exact code handles numerical checks. A missing suggestion does not clear a claim.

## The task

The analyst supplies one bounded metric statement. The supported checks are material absolute scaled magnitude of at least 3.0, positive signed change greater than zero, or either condition's negation. Required fields identify the service, metric channel, comparison meaning, assertion and before/after incident window. Health, cause, ownership, repair and trace-duration requests fall outside this workflow.

Jev chooses service, metric, comparison, assertion or window clarification; no question; or an outside-task explanation. Code supplies the corresponding question text. When several fields need clarification, the declared order is service, metric, comparison, assertion and window. The assistant cannot fill fields, bind a claim, approve entry or execute an action.

For example, “A metric has material scaled change between the before/after incident windows. Neither the service nor channel is specified” needs both service and metric. The next question asks which observed service the claim concerns. Asking about the metric would address a real omission but violate the declared order; asking about the window would be unnecessary. Both count separately.

“No optional question suggested” leaves the entry form untouched. On an ambiguous statement, that outcome counts as a silent miss if displayed. Withholding also counts as missed clarification, even when the underlying classification is correct. This study retains the failures that the old ready action exposed.

## New wording and comparators

The pack contains 92 newly written statements: 23 controlled patterns, two variants and the same two public service/channel catalogs. Nineteen patterns cover the earlier policy situations in different wording. Four add an unavailable metric channel, missing subject and channel, a bare comparison topic without an assertion, and a repair request. Each application has twelve complete statements, 28 needing a question and six outside the task.

The text and manually declared reference questions freeze before any call. The same assistant writes both. Pattern variants and application versions are correlated development examples, not independent reports. Only the inventories come from public Train Ticket and Online Boutique recordings already inspected in earlier studies. No measurements, new recording or protected allocation enters this experiment.

Three methods use the same statements:

| Method | Jev input | Optional action |
| --- | --- | --- |
| Direct question selector | One Choice question on the statement, inventory, allowed aliases and available window comparison | Code displays the selected question or disposition when its score reaches 0.70 |
| Fresh checklist control | Unchanged field-specific six-question input from the previous study | Code maps its classifications to the same optional actions; all six scores must reach 0.70 |
| Frozen literal parser | Existing keyword/name checks, unchanged and without model calls | Code maps its fields to the same optional actions |

The direct input changes both the question structure and the number of required score events. This is a task-format comparison. A coverage gain would not demonstrate calibrated probabilities or an isolated improvement in the display threshold. The threshold stays at 0.70; the task determines which answers are required.

Exact requests exclude case identifiers, pattern names, references and source metadata. The direct prompt defines each field and the fixed question order. The checklist's state and request builder remain unchanged; no historical readiness result is rewritten.

## Frozen assessment

Three rounds make 552 once-only calls: 276 per Jev input, yielding at most 1,932 field answers. Paired inputs alternate order across statements and rounds. Malformed answers quarantine the entire statement. Wrong checkpoint, envelope, usage, context, access or network failures stop the run. Original replies remain intact, with no retries, repairs or threshold search.

The direct selector is the sole candidate. Every application and round has overall, complete-wording, needs-question and outside-task gates. Each requires complete valid responses, at least 95% correct canonical actions and at least 90% correct displayed actions. No displayed question may target an already clear field; no ambiguous statement may receive a displayed no-question answer; no incorrect scope action may display.

The assessment also retains necessary questions, correct first questions, questions in the wrong order, silent misses, withholding on ambiguity, missed clarification and paired gains/losses against both comparators. The parser's 92 unique outputs repeat across rounds; they are not 276 independent parser trials.

## What this can establish

A passing result would support this declared question-selection task on controlled wording. It would not establish useful advice, less analyst effort, correct entries, independent interpretation or telecom readiness. New wording written by the same assistant cannot supply independent human evidence.

## First result

All 552 calls completed, yielding 1,932 valid answers without retries or quarantine. Across 276 opportunities per method, the direct selector gives 217 correct actions and 149 correct displays. The checklist gives 263 and 187. Both withhold useful questions frequently: direct displays a necessary question on 105 of 168 ambiguity opportunities, checklist on 108. Direct misses 63 needed clarifications; checklist misses 60. All these misses are withheld suggestions, rather than displayed no-question answers.

Direct also displays five unnecessary metric questions on health requests. Those same five events count as wrong scope, not ten distinct errors. Checklist displays no unnecessary question or wrong scope action. Direct loses 87 correct displays and gains 49 against checklist, a net loss of 38. Its 52.5% lower input-token count does not offset the poorer observed behavior. The direct candidate fails its gates; neither method is selected for deployment.

The parser displays 180 correct actions, with 72 unnecessary questions, 24 silent misses and six wrong scope actions across the repeated opportunities. Its deterministic outputs do not establish a successful alternative.

## A specific display-policy diagnosis

Inspection suggests a narrower application question: must a first clarification depend on scores for fields that come later in the declared order? On the already inspected checklist replies, using only scope and the fields up to the first requested clarification would give 252 correct displays, versus 187 when all six scores gate every action. This retrospective count motivates a new frozen comparison; it is not confirmation.

The new comparison will collect fresh replies to the unchanged six-question request and apply both policies to each reply. A service question will require scope and service; a metric question will also require channel. No suggestion will still require all six scores. An outside-task explanation will depend on scope alone. Every answer must remain structurally valid: a malformed unused answer still quarantines the whole statement. The policy retains every label and score for inspection, without filling fields or declaring readiness.

The threshold stays at 0.70. Only the display dependencies change. This remains development on inspected wording and a declared priority policy, not independent validation or a measured reduction in analyst effort.
