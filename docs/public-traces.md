# Add trace evidence to Jev

I will compare the existing named metric input with the same input plus trace evidence. The addition must preserve the measurements, question and observed candidate set. Parent-child links describe observed dependencies; they do not prove that a service caused a fault.

The remaining RE1 recordings contain metrics only. The [RCAEval data description](https://github.com/phamquiluan/RCAEval) identifies traces in RE3 Train Ticket and Online Boutique, a separate collection of code faults. This experiment changes the fault collection as well as adding a telemetry source. Its metric-only control will run on those same cases, so any measured input gain will come from a paired comparison within RE3, not a comparison with old RE1 scores.

A committed audit opens all four Train Ticket auth-service F1 recordings and all three Online Boutique ad-service F3 recordings. Both service/fault groups become development and cannot enter evaluation. The audit checks trace schema, time and duration scales, service-name alignment, duplicate span IDs, missing parent links and coverage. It makes no Jev calls. All other RE3 telemetry and the 140 RE1 reserve cases remain unopened.

Trace IDs, operation text, source filenames, injected fault names and reference answers must stay outside model requests. The eventual addition will contain only validated service names and calculated observations, with unresolved mappings and incomplete coverage reported explicitly. Missing links cannot become evidence that a dependency does not exist.

The next protocol will freeze the summaries, comparison arms, grouped case allocation and call budget after the audit establishes what the source supports. Display remains single-lead-or-withhold at the existing 0.70 boundary unless a separate experiment explicitly changes it. The fitted ML remains a metric-only transfer control; any trace-based ranking will be labeled separately.
