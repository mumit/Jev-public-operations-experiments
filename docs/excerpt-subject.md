# Resolve a subject from its latest explicit service context

The shorter excerpt displays 103/104/104 correct Online Boutique claims, versus 102/103/103 with fresh full-prefix controls. Each round gains four displays and loses three. Subject accuracy does not improve consistently, and the candidate fails overall. Train Ticket and Online Boutique boundary wording pass; Online Boutique negated wording fails.

## Setup

I tested the final context transformation on the same 27 inspected controlled notes. Both inputs ask one literal subject question and retain the complete observed inventory. Only state.note changes. The excerpt starts at the latest sentence naming exactly one observed service and ends at the queried claim. Multiple names in that latest named sentence, or no service name, retain the full prefix. Complete-name boundaries prevent frontend from matching frontend-external. Every selected character and original line ending remains intact.

For the recurring redis claim, the excerpt contains:

> redis has eligible cpu signed change above 0.
> Both windows for this service meet the recorded-count minimum of 5 spans.

The subject input receives no reviewed subject, proposed service or measurement. Numerical verdict calls keep the original full note, ledgers and clean or deliberately swapped supplied binding. Code compares the selected subject with that binding; it never repairs the proposal.

Plan/producers were committed as 404c89f, then de46205 froze both exact phases before inference. The experiment completes 972 paired subject calls and 162 unconditional six-question verdict batches over three rounds: 1,134 actual calls and 1,944 valid answers. No quarantine or retry occurs. Subject replies support both proposal conditions, with actual calls counted once. Zero new recordings, human reviews or independent reviews enter the study.

## Results

Values correspond to rounds one, two and three. Displays below are correct guidance under the clean proposal.

| Application / wording | Full-prefix displays | Excerpt displays | Excerpt subject accuracy |
| --- | --- | --- | --- |
| Train Ticket, all | 54/54/54 | 54/54/54 | 54/54/54 out of 54 |
| Online Boutique, all | 102/103/103 | 103/104/104 | 106/106/106 out of 108 |
| Online Boutique, plain | 36/36/36 | 36/36/36 | 36/36/36 out of 36 |
| Online Boutique, negated | 32/33/33 | 31/32/32 | 34/34/34 out of 36 |
| Online Boutique, boundary | 34/34/34 | 36/36/36 | 36/36/36 out of 36 |

Full-prefix subject accuracy is 107/107/106 out of 108 for Online Boutique. The excerpt has paired service gains of 1/0/2 and losses of 2/1/2. Net displayed coverage improves by one each round, but not through uniformly better subject extraction. Both workflows display zero swapped guidance. Both clean numerical baselines judge and display every claim correctly.

The fixed gate requires correct subject comparisons and clean verdicts throughout, no loss of correct clean baseline displays, at least 90% coverage and zero unsafe swapped guidance. Excerpt still withholds 5/4/4 correct Online Boutique baseline verdicts. Negated wording fails each round; no promotion follows.

## A repeated fix and repeated losses

For NWL-59bca7262cdd, boundary s07, the excerpt selects redis at 0.83/0.85/0.82 and displays its correct unanswerable verdict throughout. Fresh prefixes select redis at 0.44/0.43, then recommendationservice at 0.46, withholding all three. Removing the earlier service context fixes this example and raises its probability above 0.70.

The same transformation loses three correct displays in every round. Two recurring losses involve negated cause claims s04, while a frontend-external span or health claim accounts for the third. Some losses retain the correct subject below 0.70; others select unresolved. The inspector exposes each actual reply. A net gain cannot erase these regressions, and the redis fix does not justify applying the rule to general reports.

## Cost

| Clean workflow | Actual constituent calls | Input tokens | Summed call latency |
| --- | --- | --- | --- |
| Full-prefix subjects plus verdict | 567 | 1,064,601 | 97.61 seconds |
| Excerpt subjects plus verdict | 567 | 1,047,258 | 97.80 seconds |

The excerpt saves 1.6% of total workflow input tokens; summed latency does not improve in this run. Each workflow uses six subject calls and one verdict batch per note. Clean and swapped compositions share subject calls and their respective verdict baselines, so workflow totals overlap. Summed call latency is not end-to-end elapsed time.

## Limits and continuation

The same assistant wrote and inspected these notes and references. These results measure a transformation on familiar, uniquely resolvable claims, not independent report reading or telecom reliability. All 22 cause-evaluation cases, 30 RE3 Sock Shop cases and 140 RE1 reserves remain unopened.

The separately frozen [subject-context challenge](subject-robustness.md) tests quoted or intervening context, ambiguity and later clarification. Its text and separate complete-note/context-visible references were committed as d2fcb3c before inspection of this experiment's results. No further wording tuning on these 27 notes follows from the small net gain. The next complete-workflow design must account for information removed by truncation and the earlier role/meaning extraction failures.

[Inspect the redis improvement](http://127.0.0.1:8769/excerpt-subject?dataset=Online+Boutique&wording=boundary&card=NWL-59bca7262cdd&arm=clean_excerpt&round=1&sentence=s07).
