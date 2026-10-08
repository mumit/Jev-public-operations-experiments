# New reports confirm three-class reading on a small panel

Literal claim definitions display all 81 repeated judgments correctly across 27 controlled claims, three new monthly reports and three rounds. Legacy definitions choose all 81 correctly, display 78 and withhold three. Neither displays a wrong answer. The literal candidate passes all twelve frozen checks across reports and rounds against assistant-reviewed references.

The gain concerns one claim about unreported data loss. This panel confirms correct reading and improved displayed coverage on these claims. It contains no control error, so it cannot show that literal definitions prevent wrong judgments.

## Purpose

The earlier six-claim diagnostic reduced wrong displays by withholding but failed its coverage gate. Its references contained supported and contradicted claims, with no not-established example. I chose a new-report comparison across all three verdict classes, keeping the question wording and 0.70 display threshold fixed.

This study asks whether Jev can assess an explicit claim against a selected publisher report section. It does not test incident detection, root-cause discovery, telemetry validation or automated network actions. Every displayed judgment remains an analyst-facing recommendation.

## Reports and preparation

The allocation froze three whole monthly-report groups before downloading their contents: GitHub availability reports for [January](https://github.blog/news-insights/company-news/github-availability-report-january-2024/), [February](https://github.blog/news-insights/company-news/github-availability-report-february-2024/) and [March 2024](https://github.blog/news-insights/company-news/github-availability-report-march-2024/). None appeared in the earlier report study.

The first preparation required three sections per report. The audit found three in January, one in February and two in March, so preparation failed before claims, reference annotations, requests or model calls. That failed audit remains recorded.

A separately committed v2 plan retained all three sources and their exact snapshots. Impact uses the first section, cause the second if available and recovery the third if available. A report with fewer sections reuses its last section. Assignment follows document order and count, without choosing sections to suit an answer. February combines two incidents within one section; March lists its later incident first.

Each report supplies nine controlled claims: one supported, one contradicted and one not established for each topic. That gives 27 distinct claims, nine in each verdict class. The three rounds repeat them; 81 judgments per arm do not represent 81 independent incidents.

The assistant wrote claims and references after inspecting these source snapshots and before model outcomes. Each reference records a rationale and hashes of the relevant source blocks. Publisher authorship is independent of this project; the references have zero independent specialist reviews. Section selections are preparation fixtures, with zero actual analyst entries.

February’s source contains inconsistent dates and durations. No claim depends on those inconsistent facts. The complete selected section retains them; preparation did not repair publisher text.

## Inputs and verdict definitions

Both arms receive identical state: the claim, an explicit section header and the report-wide introduction plus every block in that section. State excludes reference labels, claim IDs, evidence annotations and scoring rules. The legacy and literal requests reuse the earlier frozen producer unchanged; only their question instructions and verdict criteria differ.

Literal definitions judge the exact proposition, including subject, time, quantifiers and certainty. Supported requires matching evidence. Contradicted requires an incompatible statement in the same scope. Not established means neither verdict follows from the excerpt. Missing information alone does not make a claim false.

For example, the March 15 excerpt establishes service failures but does not settle whether customer repository data was lost. The claim that data was lost therefore remains not established. This differs from a claim that a report confirms a cause when the report explicitly says investigation is ongoing, which the literal contract treats as contradicted.

The committed exact protocol permits 162 once-only calls: two arms, 27 claims and three rounds. All calls succeeded and all 162 answers validated. Jev remains version 1.13.0; the display threshold remains 0.70. Requests used 142,155 input tokens. No call was retried, and no telemetry recording opened.

## Results

| Definitions | Correct choices | Correct displayed | Wrong displayed | Sent to review |
|---|---:|---:|---:|---:|
| Legacy | 81/81 | 78/81 | 0 | 3 |
| Literal claim | 81/81 | 81/81 | 0 | 0 |

Literal definitions display all 27 repeated judgments correctly in each verdict class. Every report contributes nine correct displays in every round. The exact-string rule control matches none of these paraphrased claims and withholds all judgments; it is a narrow baseline, not a full operational rules system.

All three paired gains involve the same March 15 data-loss claim. Legacy correctly chooses not established but withholds at 0.64, 0.68 and 0.68. Literal chooses and displays not established in every round. No other correct display changes, and no correct control display is lost. Both arms make the same correct choices throughout.

Each report and round meets the frozen requirements: zero wrong displays, at least six correct displays out of nine, a correct display in every verdict class and no correct display loss against fresh legacy. Global checks also pass. These are the new selective objectives; the earlier five-of-six coverage failure remains unchanged.

## What the result supports

The current input can judge these explicit claims across all three classes. Clear evidence binding and literal definitions warrant further testing for report-assisted operations work.

The result does not establish an error-rate advantage: legacy has no wrong display to prevent. All sources come from one publisher, the claims are controlled and many use explicit wording. Public reports may occur in pretraining and describe incidents with hindsight. Assistant references remain unreviewed independently. These limits prevent a claim of live triage reliability or telecom readiness.

## Next steps

The separately frozen [whole-report transfer](cross-reports.md) now tests a different publisher with time, service scope, uncertainty and recovery qualifications. It passes selective checks by withholding one repeated wrong choice while preserving correct displays. The questions and threshold remain fixed; the new result does not change this study’s outcomes.

Before a workflow trial, the intended task needs a choice: report claim checking or live incident recommendations. Report checking can continue with public postmortems. Live recommendations need evidence available during an incident and references for the action an analyst should take; retrospective report-reading scores cannot provide them. No additional inference or protected data access is included in this completed protocol.

## Inspect and replay

Open [the new-report comparison](http://127.0.0.1:8769/selective-reports?claim=gh-march-2024-c3&round=1&input=literal) to change reports, claims and rounds, inspect every class and gate, reveal reference rationales and compare exact local requests. Browsing makes no model calls.

The public bundle contains original answer/usage payloads and summaries. Full publisher reports and full-text requests stay local. Public replay checks request fingerprints, answer normalization, fixed rule projections and all scores. Reconstructing full input bytes and rule matches requires the matching retained snapshots. See [evidence restoration](evidence.md) for the versioned release.
