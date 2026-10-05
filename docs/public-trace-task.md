# Clarify Jev's trace-aware task

The first trace addition produced no repeatable gain. This comparison tests whether a trace-aware question and explicit arithmetic help Jev identify the originating service. All 192 development calls completed, but the candidate failed promotion. The 22 evaluation cases remain unopened. Jev continues to consider every observed metric candidate; ML supplies an unchanged comparison, not a candidate shortlist or fallback.

## Four inputs, three changes

| Input | Evidence | Question | Comparison |
| --- | --- | --- | --- |
| Metrics | Original named metric summaries | Original question | Metric-only control |
| Traces | Identical metrics plus compact trace context | Original question | Effect of adding traces |
| Trace-aware task | Identical metrics and traces | Revised question and insufficient-evidence wording | Effect of the task wording |
| Trace changes | Identical metrics and traces plus calculated changes | Same revised question | Effect of explicit arithmetic |

The fourth input is the predeclared candidate. The other inputs explain the differences; a better diagnostic arm cannot replace the candidate after results arrive.

The original question emphasizes local resource changes and its insufficient-evidence option refers to “metric summaries.” The revised version asks about all supplied metric and trace observations. It allows faults without a resource spike, distinguishes inclusive duration from uncovered work, keeps uninstrumented metric candidates eligible and treats missing status codes as unknown. A changed duration or parent-child link still does not prove a cause.

## Calculated changes

The added `trace_changes` field uses the same rounded trace observations already in the request. Each observed trace service gets signed relative changes in median/p90 inclusive and uncovered duration, a recorded-span-rate change and a flag for at least five spans in each window.

Relative change is `(after - before) / before`. A missing value or nonpositive before value yields null, without an artificial floor. Recorded-span rate divides recorded spans by elapsed window seconds, so unequal window lengths do not become a count increase by themselves. The calculation does not correct sampling or traffic changes and is not a measured request rate. A five-span flag does not establish statistical significance.

These fields restate existing evidence. They add no independent corroboration, published answer or fitted parameter. All original observations remain available, including missing coverage and unresolved links.

## Fresh cases and fixed controls

Development opened 16 previously unopened RE3 recordings in four intact service/fault groups: ten Train Ticket cases and six Online Boutique cases. The earlier 13 trace-development recordings are excluded. The existing 22-case evaluation panel stays unchanged and unavailable until the new candidate passes development. Nine RE3 reserve cases, RE3 Sock Shop and all 140 RE1 reserves stay unopened.

Jev 1.13.0 ran each development input in three rounds: 192 calls, serial, with cyclic arm/case order, no retries and no warmup. Sources and allocation froze before telemetry download; exact requests froze before calls. The existing 32,768-token context and conservative 79,840-byte sizing cap apply. The 0.70 probability boundary, zero margin, at most one displayed lead and fitted metric ML remain fixed. There is no threshold search or training on these cases.

## Evaluation rule

The fourth input must fix at least one distinct original-trace failure in every round in each application, with no repeated loss of a metric or original-trace success. Every round must preserve first-choice accuracy and displayed correct coverage against both original controls, add no displayed wrong leads and supply some correct displayed guidance. Complete successful development is required.

If those descriptive criteria pass, a committed candidate can unlock 132 calls on the existing 22 evaluation cases: original trace input versus the frozen candidate, three rounds. Otherwise evaluation stays unopened. The criteria are research choices, not an operational error budget.

These are controlled public application code faults with supplied incident boundaries and published injected-service references. Repeated rounds are not independent incidents. The study does not establish operational reliability, analyst benefit or telecom readiness.

## Results

Each sequence below lists rounds one, two and three. Every round uses the same cases; the three responses do not triple the independent sample size. No request failed or retried.

| Application | Input | Correct first choices | Correct displayed leads | Wrong displayed leads | Withheld |
| --- | --- | --- | --- | --- | --- |
| Train Ticket (10 cases) | Metrics | 1 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 10 / 10 / 10 |
| Train Ticket | Traces | 1 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 10 / 10 / 10 |
| Train Ticket | Trace-aware task | 0 / 1 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 10 / 10 / 10 |
| Train Ticket | Trace changes | 1 / 1 / 1 | 0 / 0 / 0 | 0 / 0 / 0 | 10 / 10 / 10 |
| Online Boutique (6 cases) | Metrics | 6 / 6 / 6 | 6 / 6 / 6 | 0 / 0 / 0 | 0 / 0 / 0 |
| Online Boutique | Traces | 6 / 6 / 6 | 6 / 6 / 6 | 0 / 0 / 0 | 0 / 0 / 0 |
| Online Boutique | Trace-aware task | 6 / 6 / 6 | 6 / 6 / 6 | 0 / 0 / 0 | 0 / 0 / 0 |
| Online Boutique | Trace changes | 6 / 6 / 6 | 5 / 5 / 6 | 0 / 0 / 0 | 1 / 1 / 0 |

No adjacent step produced a fix or loss of a first-choice match in all three rounds. The candidate also produced no such fix against either original control. Train Ticket supplied no displayed guidance. Online Boutique had no original error to fix, and calculated changes lost correct displayed coverage in two rounds. Both application gates failed. Evaluation did not open and its 132 calls were not spent.

Frozen metric ML matched 6/10 Train Ticket targets and 4/6 Online Boutique targets. Change, resource and uncovered-duration rankings matched 0/0/3 out of ten and 6/5/0 out of six, respectively. These controls use the same cases. ML transfers its earlier Online Boutique training recipe; it does not fit these development recordings.

## What changed inside two cases

In [TQA-3ca0b978c13a](http://127.0.0.1:8769/trace-task?dataset=Train+Ticket&case=TQA-3ca0b978c13a&arm=trace_deltas&round=2&service=ts-route-service#input), the published target is ts-route-service. Its median inclusive span duration rises from 1,620.5 to 2,430.5 microseconds. Median uncovered duration rises from 1,032.5 to 1,533.0 microseconds. The new field makes these changes explicit: +49.98% and +48.47%. Recorded-span rate falls 7.06% after correcting the 900/901-second windows. Status codes remain unavailable.

The original trace input chooses the target only in round one, then chooses insufficient evidence. The trace-aware question chooses the target only in round two. Adding arithmetic selects it in all three rounds, at probabilities 0.4444, 0.3434 and 0.3737. This is a useful diagnostic change, but it is neither a three-round fix against the original trace input nor a displayed recommendation at 0.70. It does not establish that local duration identifies the originating fault.

In Online Boutique, adservice has metric evidence but no mapped spans. The question explicitly keeps it eligible. For [TQA-d350daa3263d](http://127.0.0.1:8769/trace-task?dataset=Online+Boutique&case=TQA-d350daa3263d&arm=trace_deltas&round=1&service=adservice#inspect), all four inputs select adservice correctly. Its probability drops from 0.97 with metrics, to 0.89 with traces, to 0.86 with the revised question, to 0.68 with arithmetic. The final step withholds the correct lead in round one. A different adservice case, [TQA-cdcb5a5f1bc8](http://127.0.0.1:8769/trace-task?dataset=Online+Boutique&case=TQA-cdcb5a5f1bc8&arm=trace_deltas&round=2&service=adservice#inspect), crosses just below the boundary in round two at 0.6970.

The extra fields describe other observed services; they cannot manufacture missing adservice evidence. These paired outputs show reduced displayed coverage, but do not establish why the model assigned lower probabilities. Reading the exact requests makes that uncertainty visible.

## Interpretation and next choice

This intervention does not establish that Jev performs well at originating-service diagnosis from these inputs. Explicit arithmetic stabilizes one Train Ticket target selection, without useful displayed coverage. Online Boutique succeeds with metrics alone on these groups; traces and arithmetic supply no accuracy gain. Zero displayed wrong leads in Train Ticket comes from withholding everything.

Another broad rewrite has little support here. My recommendation is to test a narrower task: identify which observed service shows a material local change and which evidence supports investigating it. That tests evidence assessment before asking Jev to assign an originating cause. It requires a new reference definition and protocol. Published injected-service labels cannot automatically serve as references for the most suspicious observed change, and these inspected cases cannot become held-out validation.

The alternative is a separate ML candidate-selection study with Jev assessing evidence for the shortlist. That changes the task and needs explicit comparison with the ML control, including targets the shortlist excludes. Neither alternative is authorized by this completed protocol. Keep all 22 evaluation cases, nine remaining RE3 reserves, RE3 Sock Shop and 140 RE1 reserves unopened until the next choice is made.

## Inspect and reproduce

Open the [four-step inspector](http://127.0.0.1:8769/trace-task). It shows all three recorded responses, hidden/revealed references, local rankings, original metrics, span coverage, calculated changes, exact questions and full request JSON. Browsing makes no model calls.

The largest frozen request was 78,476 bytes, below the unchanged 79,840-byte cap. Recorded input tokens peaked at 28,224. The development plan and exact protocol were committed before execution. The separate source modules, data, requests and assessment are frozen. Restore the seven versioned bundles described in [evidence](evidence.md), then run `python -m scripts.verify_public_trace_task` with the pinned environment. Verification reconstructs the inputs and results without inference.

## Later evidence-assessment diagnostic

The user selected the narrower task. The [evidence-assessment study](public-evidence-assessment.md) reuses these 16 inspected recordings and asks independent numerical change, coverage and strongest-channel questions. It does not reinterpret their injected labels as evidence references. Agreement is much higher, but calculated changes help one application and lose accuracy in the other. Its overall check fails and all protected telemetry remains unopened. The earlier cause-selection result stays unchanged.
