# Whole-report transfer preserves selective coverage

Literal definitions display 78 of 81 repeated judgments correctly, withhold three and display no wrong answer on three Cloudflare reports. Legacy displays the same 78 correctly and three incorrectly. Both choose 78 correctly. All twelve frozen selective checks pass against assistant-written references.

The difference repeats one claim about what a report establishes. Literal wording sends the wrong interpretation to review without correcting it. This is one distinct error repeated three times, not three independent failures prevented.

## Purpose and allocation

The [earlier new-report study](selective-reports.md) passed on 27 controlled claims from GitHub monthly reports, but contained no control error. I chose a transfer test with a different publisher and longer whole incident reports, keeping Jev's question producer and 0.70 display threshold fixed.

The committed plan allocates Cloudflare's [March 26 power failure](https://blog.cloudflare.com/major-data-center-power-failure-again-cloudflare-code-orange-tested/), [June 20 CDN incidents](https://blog.cloudflare.com/cloudflare-incident-on-june-20-2024/) and [June 27 DNS routing incident](https://blog.cloudflare.com/cloudflare-1111-incident-on-june-27-2024/). None appeared in an earlier model protocol. Discovery searches exposed some content before allocation, including substantial DNS text, so source selection was not blinded.

The once-only audit retained all three reports. Extraction keeps every prose, heading, list, table and code block in the article container, in source order. Whitespace is normalized; images are excluded. No summary, answer-led selection, replacement or prefix truncation occurs. The power report includes discussion of an earlier failure already present in a historical study; the new report is not independent of that incident history.

| Report | Extracted blocks | Text bytes | Code blocks |
|---|---:|---:|---:|
| March 26 power | 49 | 13,678 | 0 |
| June 20 CDN | 79 | 17,521 | 2 |
| June 27 DNS | 75 | 23,949 | 2 |

Each source supplies nine controlled claims: impact, cause and recovery each have one supported, one contradicted and one not-established example. There are 27 distinct claims, nine in each class. Three rounds repeat them; they do not add independent incidents.

The assistant wrote and reviewed claims after inspecting the reports and before Jev outcomes. References record rationales and exact source-block hashes, with zero human entries or independent reviews. They judge the supplied text, not independently verified incident facts. June 20's timeline and later prose give different rule-disablement times. No claim depends on that precise timestamp; the full input preserves both statements.

## Exact input and model setup

Each request supplies three state fields: `claim`, `selected_incident` and `report_excerpt`. Selection is the exact whole-report title. The excerpt is the complete extracted report, including earlier incidents, technical examples and future plans. IDs, source URLs, references, evidence annotations and scoring rules remain outside state.

For example, the power claim asks whether the report establishes when the breaker settings were configured. Both variants receive the same claim, full text and title. Legacy definitions evaluate report support in their earlier terms. Literal definitions explicitly preserve the claim's subject, time, quantifiers and certainty: an assertion that the report establishes a fact conflicts with its explicit statement that the fact is unknown. Missing information alone remains not established.

Both variants reuse `literal_claim_features.request` unchanged. Only question instructions and verdict criteria differ; every paired state is byte-identical. Jev remains 1.13.0, with 32,768 context tokens and the fixed 0.70 display boundary. These provider probabilities are not a calibrated operational risk estimate.

The committed protocol froze 162 exact requests before once-only inference: 27 claims, two variants and three rounds. All replies succeeded and validated. Requests used 867,129 input tokens in total, compared with 142,155 in the earlier selected-section study. The new prospective wire cap is 64,000 bytes; the largest request is 25,853 bytes. No call was retried, no reference changed after outcomes and no telemetry opened.

Publisher and report scope changed together. This comparison does not isolate either change or establish that whole-report inputs outperform selected sections.

## Results

| Definitions | Correct choices | Correct displayed | Wrong displayed | Sent to review |
|---|---:|---:|---:|---:|
| Legacy | 78/81 | 78/81 | 3 | 0 |
| Literal claim | 78/81 | 78/81 | 0 | 3 |

Both variants correctly display all nine claims per round in the CDN and DNS reports. In the power report, each correctly displays eight of nine; legacy displays the remaining answer incorrectly, while literal withholds it. No correct control display is lost and no correct display is gained.

All supported and not-established references receive correct displays throughout. Of 27 repeated contradicted references, 24 receive correct displays from each variant. The remaining three are the same power claim:

> The report establishes when the breaker settings involved in the March 26 failure were configured.

The source explicitly says that timing is unknown. The literal contract therefore marks this report-establishment claim contradicted. Both variants instead choose not established in all three rounds. Legacy assigns 0.89, 0.91 and 0.89 to that choice and displays it. Literal assigns 0.63, 0.64 and 0.66 and sends it to review. The task distinguishes what the report establishes from the underlying configuration date; those are different propositions.

Every report and round meets the frozen selective requirements: no wrong display, at least six correct displays out of nine, a correct display in each class and no loss of a correct legacy display. Global completeness and no-wrong/no-loss checks also pass. These criteria permit withholding. Passing does not mean every claim is understood correctly.

The unchanged exact-string rule control matches none of these paraphrases and withholds every judgment. It is a narrow comparator, not a comprehensive rules system. No new ML model was trained for this text task; historical numerical ML results remain separate.

## What this adds to task fit

Jev's literal input supports further exploration of explicit report claim checking. It handles these service exceptions, recovery sequences and routing qualifications while preserving correct displayed coverage and withholding one repeated wrong interpretation. That is useful evidence for an analyst-facing selective checker.

The result does not establish a generally lower error rate or reliable live triage. Twenty-seven controlled claims across three related publisher reports are a small panel. The same assistant wrote the references; public reports may be in pretraining and include causal hindsight. Discovery was exposed. Longer context and publisher change are combined. No authentic analyst claims, independent reference agreement, calibrated risk, measured analyst benefit or telecom-specific performance was tested.

## Next step and remaining input

The next useful study is an analyst claim-checking workflow: an analyst selects a public report, enters a claim they actually want checked, and judges whether the displayed result and source evidence help. Exact claims and intended scope must be recorded before model answers; a separately frozen protocol must precede any new calls. The current inspector already exposes the input, verdict distribution, reference and original reply needed to examine that workflow.

That step needs claims authored outside this experiment, or a decision to continue controlled diagnostics instead. More assistant-written paraphrases can test specific mechanisms but cannot measure authentic analyst usefulness or independent interpretation. I recommend collecting a small batch of naturally occurring claims before further tuning. The current producer and threshold remain frozen; the repeated error is not repaired against this inspected panel.

No protected recording or further call is authorized by the completed transfer protocol. Earlier failures remain unchanged.

## Inspect and replay

Open [the whole-report comparison](http://127.0.0.1:8769/cross-reports?claim=cf-power-2024-c5&round=1&input=literal) to inspect the remaining error, other claims, three rounds, classes and report gates. Reveal reference rationales separately. The local input panel shows readable complete report text and the exact request. Browsing makes no model calls.

The public answer-only bundle contains original model/answer/usage replies and the execution summary. Publisher snapshots and full-text requests remain local. Public replay verifies original payloads, fixed rule projections, source/reference/producer fingerprints, complete denominators and every gate. Full input and rule reconstruction additionally require matching retained snapshots. See [evidence restoration](evidence.md).
