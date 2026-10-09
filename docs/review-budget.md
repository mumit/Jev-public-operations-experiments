# The accepted review budget passes

The unchanged report-knowledge definitions display 25 of 27 claims correctly in every round, send two to review and display none incorrectly. All twelve prospective checks pass on three newly allocated Cloudflare reports. Both variants choose all 81 repeated reference answers correctly. Literal displays 79 correctly and withholds two; report knowledge displays 75 correctly and withholds six. The candidate loses four correct displays and gains none, so this panel does not show a comparative error reduction.

## Purpose and accepted objective

The [earlier diagnostic](report-knowledge.md) corrected an interpretation error but failed its no-loss coverage requirement. I accepted up to one claim in ten sent to review for a new study, with the intention of reducing that burden later. The earlier failure remains unchanged.

The new committed plan requires, in every round, complete valid paired evidence, at least 90% correct displays, at most 10% review and zero wrong displays. With 27 claims, the integer requirements are at least 25 correct displays and at most two reviews. Every report must also correctly display all three verdict classes. Comparative gains and losses remain visible but do not determine eligibility under this objective.

The 10% budget applies to all claims in a round. It does not impose a separate 10% limit within every verdict class or report. Results below expose those differences rather than treating the overall rate as uniform coverage.

## Newly allocated reports and controlled claims

The plan allocates three exact official sources before downloading whole snapshots:

| Report | Retained blocks | Text bytes | Code blocks |
|---|---:|---:|---:|
| [June 12, 2025 service outage](https://blog.cloudflare.com/cloudflare-service-outage-june-12-2025/) | 61 | 17,250 | 0 |
| [July 14, 2025 DNS incident](https://blog.cloudflare.com/cloudflare-1-1-1-1-incident-on-july-14-2025/) | 48 | 13,275 | 1 |
| [November 18, 2025 outage](https://blog.cloudflare.com/18-november-2025-outage/) | 77 | 18,046 | 1 |

All three pass the once-only source audit. Extraction retains every prose, heading, list, table and code block in source order, normalizes whitespace and excludes images. No replacement, summarization, answer-led selection or truncation occurs. Discovery searches exposed some text before allocation, including substantial DNS background and timeline; source selection is not blinded. These are new to the project’s model protocols, not guaranteed unknown to Jev’s training.

Each report supplies nine assistant-written claims: impact, cause and recovery each include supported, contradicted and not established. One claim in each topic concerns what the report says or establishes; the other two concern incident facts. The 27 distinct claims therefore balance verdict classes within both assertion types. Three rounds repeat those claims; they do not add independent reports.

References freeze exact source-block hashes and rationales before model outcomes. They follow the selected literal-claim contract, with zero human entries or independent reference reviews. The June rerouting claim asserts an established explanation where the report explicitly says investigation continues. The DNS claims preserve transport exceptions and distinguish the non-causal hijack. The November claims distinguish old/new proxy behavior and partial/full recovery.

June gives a precise KV error rate in its table and a rounded figure later. November gives differing onset and bypass timestamps across prose and timeline. Claims avoid treating those as single exact facts; the complete input keeps the differences. Source cautions remain visible in the inspector.

## Model input and fixed execution

Both arms reuse `report_knowledge_features.request` unchanged. State contains only the exact claim, whole-report title and complete extracted text. Paired states are byte-identical. Assertion-type annotations, IDs, URLs, references and evidence selections stay outside state. The arms differ only in their previously frozen instructions and verdict descriptions; [the earlier report](report-knowledge.md) shows the exact transformation.

Jev stays at 1.13.0 with 32,768 context tokens and the 0.70 display boundary. The committed protocol freezes 162 requests: 27 claims, two variants and three rounds. The largest body is 20,859 bytes under the 64,000-byte cap. All calls succeed and validate, using 688,797 input tokens. No retry, threshold fitting, reference correction or new telemetry access occurs.

The exact-string rules match none of these claims and withhold every answer. No new ML model is trained for this text task. Historical numerical controls remain separate.

## Results by round, report and class

| Definitions | Correct choices | Correct displayed | Wrong displayed | Review |
|---|---:|---:|---:|---:|
| Literal control | 81/81 | 79/81 | 0 | 2 |
| Report knowledge | 81/81 | 75/81 | 0 | 6 |

Each candidate round displays 25/27 correctly, or 92.6%, and sends 2/27 to review, or 7.4%. Every global and report/class-representation check passes. Correct-display losses against the control are two in round one and one in each later round. There are no choice gains, choice losses or display gains.

Across rounds, the candidate displays 24/27 correctly on the June report, 27/27 on DNS and 24/27 on November. Incident-fact coverage is 51/54; report-knowledge coverage is 24/27. Both supported and contradicted classes receive 27/27 correct displays. Not-established coverage is 21/27, or 77.8%, so that class receives substantially more review than the overall average.

The related interpretation challenge does not expose a control error here. Both arms correctly display the June claim about an established rerouting explanation as contradicted throughout. The candidate assigns 0.97 in each round; literal assigns 0.78, 0.79 and 0.82. Higher probabilities do not establish calibrated risk or an error-rate improvement.

## The two remaining review cases

| Claim sent to review by candidate | Literal probabilities, rounds 1/2/3 | Candidate probabilities, rounds 1/2/3 |
|---|---|---|
| A single named customer generated all the extra Zero Trust registration traffic during the outage. | 0.71 / 0.67 / 0.66 | 0.58 / 0.62 / 0.64 |
| The report supplies an exact completion date for each listed follow-up hardening project. | 0.86 / 0.88 / 0.89 | 0.53 / 0.58 / 0.58 |

Both references and both variants’ choices are not established. Literal withholds the first claim in rounds two and three; the candidate withholds both in every round. This creates four additional reviews on two distinct claims. Reviewing them means checking what the report establishes, not discovering the true customer identity or forecasting project completion dates.

The first case concerns an unsupported attribution with a universal quantifier. The second concerns missing reporting. They are useful targets for a later evidence-support diagnostic, but their inspected outcomes cannot validate a new mitigation on fresh claims.

## What this establishes and what remains

The candidate meets the accepted coverage/review objective on this controlled panel. It does not outperform the literal control here: both have no wrong displayed answers, and literal covers more claims. The earlier development supplies a corrected interpretation on one different claim; this new result cannot turn that into a general advantage.

Publisher hindsight, possible training exposure, controlled claims and same-assistant references limit the conclusion. No authentic analyst usefulness, independent agreement, measured review time, operational error guarantee or telecom-specific performance is established. Earlier protocols and protected telemetry remain unchanged.

The next useful mitigation is to make withheld claims easier to resolve using relevant source evidence, while preserving review and 0.70. That requires a new evidence-selection protocol: score whether the selected text supports the review, including absence-of-information claims, before testing whether it reduces review effort. More confident display alone is not the objective. Actual time saved or analyst usefulness requires an analyst workflow; assistant checks cannot supply that evidence.

No further call belongs to this completed confirmation. A separate mitigation protocol or authentic analyst-claim workflow must precede new inference. The complete inspector exposes the two withheld cases, all distributions, every gate, assertion-type and class denominators, and exact local inputs.

## Inspect and replay

Open [the review-budget comparison](http://127.0.0.1:8769/review-budget?claim=cf-nov18-2025-c9&round=1&input=knowledge). Reference rationales remain behind explicit reveal. Browsing invokes no model.

The public answer-only supplement retains original model/answer/usage payloads and the execution summary. Publisher snapshots and full-text requests remain local. Public replay verifies 900 calls in the text-study chain using saved replies, fixed rule projections and committed fingerprints; matching local snapshots additionally permit exact full-request reconstruction. See [restoration](evidence.md).
