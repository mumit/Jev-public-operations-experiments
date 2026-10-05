# Clarify Jev's trace-aware task

The first trace addition produced no repeatable gain. I will now test whether a question that addresses all supplied telemetry and explicit arithmetic changes help Jev identify the originating service. Jev continues to consider every observed metric candidate; ML supplies an unchanged comparison, not a candidate shortlist or fallback.

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

Development opens 16 previously unopened RE3 recordings in four intact service/fault groups: ten Train Ticket cases and six Online Boutique cases. The earlier 13 trace-development recordings are excluded. The existing 22-case evaluation panel stays unchanged and unavailable until the new candidate passes development. Nine RE3 reserve cases, RE3 Sock Shop and all 140 RE1 reserves stay unopened.

Jev 1.13.0 runs each development input in three rounds: 192 calls, serial, with cyclic arm/case order, no retries and no warmup. Sources and allocation freeze before telemetry download; exact requests freeze before calls. The existing 32,768-token context and conservative 79,840-byte sizing cap apply. The 0.70 probability boundary, zero margin, at most one displayed lead and fitted metric ML remain fixed. There is no threshold search or training on these cases.

## Evaluation rule

The fourth input must fix at least one distinct original-trace failure in every round in each application, with no repeated loss of a metric or original-trace success. Every round must preserve first-choice accuracy and displayed correct coverage against both original controls, add no displayed wrong leads and supply some correct displayed guidance. Complete successful development is required.

If those descriptive criteria pass, a committed candidate can unlock 132 calls on the existing 22 evaluation cases: original trace input versus the frozen candidate, three rounds. Otherwise evaluation stays unopened. The criteria are research choices, not an operational error budget.

These are controlled public application code faults with supplied incident boundaries and published injected-service references. Repeated rounds are not independent incidents. The study does not establish operational reliability, analyst benefit or telecom readiness.
