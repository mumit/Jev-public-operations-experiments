# Explicit incident selection does not improve displayed accuracy

The selected-section diagnostic is complete. All 54 Jev calls returned valid answers on six inspected claims, repeated in three rounds. The selected-section input gives nine correct displays, six wrong displays and three withheld judgments, matching the fresh full-report control. Every declared candidate gate fails.

Adding only an incident-selection field reduces wrong displays from six to three by withholding more answers. It adds no correct displays. That arm is a diagnostic comparator, not the declared candidate.

## The input contract

The analyst selects one exact incident header before checking a claim. Missing, unknown or multiple selections require clarification. Code does not infer dates, choose a default or substitute another incident. Claims comparing multiple incidents fall outside this one-incident task.

The user selected this workflow on October 7. For this experiment, I prepared six selection fixtures on GitHub’s already inspected April 2023 availability report. The selections are assistant-supplied, not actual analyst entries. Human entry, human review and independent specialist review counts remain zero.

## Three inputs

| Input | State supplied to Jev | Report text |
|---|---|---|
| Full report | Original claim and excerpt | Original complete-block prefix |
| Selected incident + full report | Same claim and excerpt, plus selected_incident | Same full prefix |
| Selected incident + its section | Same claim, plus selected_incident | Report introduction and the selected incident’s complete blocks |

The full control is byte-identical to the earlier request, with fresh replies. Both selected inputs add the exact incident header. The section input removes unrelated incidents; it does not summarize or rewrite the retained text. Selection precedes model inference and does not use reference answers to choose blocks. Reference spans are checked afterward only to ensure their evidence remains present.

For the March 31 claims, the excerpt shrinks from 7,155 to 1,125 bytes. The claim, question instructions, three verdict options and 0.70 display boundary stay unchanged. The plan, selections, producer sources, exact requests and 54-call budget were committed before calls. Inputs rotate across three rounds. No retry, reference change or new telemetry access occurs.

## Results

Each input has eighteen repeated opportunities on the same six claims.

| Input | Correct choices | Correct displayed | Wrong displayed | Sent to review |
|---|---:|---:|---:|---:|
| Full report | 9/18 | 9/18 | 6 | 3 |
| Selected incident + full report | 9/18 | 9/18 | 3 | 6 |
| Selected incident + its section | 9/18 | 9/18 | 6 | 3 |

Neither transformation gains or loses a correct display against the fresh control in any round. The sole candidate, selected-section input, fails the no-wrong-display criterion, the five-of-six coverage minimum and the requirement to display both earlier error claims correctly in every round. Literal rules remain an offline comparator; their narrow matching is not a semantic reference.

### The affected-admin claim stays wrong against its reference

The March 31 claim concerns repository admins with the relevant notice still active. Its frozen assistant-reviewed reference is supported. Jev chooses contradicted with section-input probabilities 0.74, 0.78 and 0.84. All three display.

The full report with a selection field withholds the first-round answer, then displays contradicted at 0.75 and 0.76. Selecting the incident does not settle the coordinated-negation interpretation. The reference remains an assistant reading of the publisher’s wording, not independently adjudicated truth.

### Recovery moves to review without becoming correct

The March 29 claim says the first recovery permanently cleared the Actions backlog. Its reference is contradicted. The section input chooses not established at 0.59, 0.51 and 0.51, withholding every answer. The full control displays supported incorrectly in every round.

This catches a wrong display by withholding it, but adds no correct judgment. The replies do not establish why the model changes its answer.

### The unresolved-cause claim exposes a verdict-definition problem

The April 26 claim says the report confirms Copilot’s contributing factors. The publisher says the investigation is ongoing. The original policy assigns not established because the cause remains unconfirmed. The full-report inputs choose contradicted below 0.70 and withhold it. The section input chooses contradicted at 0.77, 0.72 and 0.73, displaying all three.

These count as wrong displays under the frozen reference policy. However, the claim describes what the report confirms, not simply whether the cause is known. Contradicted is a reasonable literal reading when the report explicitly defers that confirmation. The disagreement cannot by itself establish that Jev misunderstands the report.

The user has now selected literal judgment of the claim as written for the next experiment. That new definition will mark this confirmation claim contradicted. It will not rewrite the completed results or turn their old wrong-display counts into measured improvements.

## What follows

Incident selection remains a useful way to make the task scope explicit, but this experiment provides no displayed-accuracy gain from it. Shorter input also does not guarantee a better judgment. Model probabilities do not settle an ambiguous reference definition.

The next diagnostic will compare the original and literal verdict definitions on fresh replies, holding the selected section and claim wording fixed. A separate protocol and reference version must precede those calls. Changes on these inspected cases remain development findings; later confirmation needs new reports and all three verdict classes.

## Inspect and replay

Open [the input comparison](http://127.0.0.1:8769/incident-scope) to inspect each prepared selection, claim, round, probability and reference. Exact full-text requests remain local. Public answer evidence preserves every provider model/answers/usage payload, validation and summary, with request hashes and frozen rule projections in Git.

Replay makes no model call. Public replay checks outcomes and gates without publisher text; complete source and wire reconstruction requires matching local snapshots. Publisher authorship is independent of this project, but claims, selection fixtures and references are assistant-authored or reviewed. This is not fresh validation, analyst-effort evidence or operational readiness.
