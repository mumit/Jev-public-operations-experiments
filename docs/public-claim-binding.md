# Does explicit claim binding improve report judgments?

The report-reading diagnostic repeated two errors that direct questions judged correctly. This experiment puts each sentence’s exact text and service in its question, then tests question grouping and evidence scope separately.

## Four controlled steps

| Step | Question | Service facts | Report context | Calls per round |
|---|---|---|---|---|
| Numbered lookup | Locate the numbered sentence | Both service ledgers | Complete unchanged note | 16, six judgments each |
| Bound text | Claim ID, service and exact sentence | Both service ledgers | Complete unchanged note | 16, six judgments each |
| One claim | Same bound question, one at a time | Both service ledgers | Complete unchanged note | 96, one judgment each |
| Scoped facts | Same one-claim question | Only its named service’s ledger | Complete unchanged note | 96, one judgment each |

The extra one-claim control matters because questions share a request’s state. Removing another service’s facts for one claim requires separate calls. Comparing one-claim inputs with identical questions and report text isolates that evidence removal; comparing the bound batch with one-claim requests isolates grouping.

All 16 reports, 96 statements, 32 service cards and references stay unchanged. The lookup request exactly matches the earlier report request. Its fresh responses measure repeatability; earlier responses remain separate. The bound question adds C1–C6 identifiers, the explicit service and the sentence after “Statement:”. IDs name the existing numbered assertions; a text extractor does not generate them.

The numerical eligibility policy, verdict definitions, Jev model, context limit and inherited 0.70 display boundary stay fixed. Scoped requests retain assertions about the other service in the note but remove its ledger. Missing facts remain unknown.

## Frozen checks

Three serial rounds permit 672 calls and 1,152 verdicts, with no retries or warmup. A committed plan precedes preparation, and exact requests freeze before inference.

Each changed step must complete alongside its predecessor, reach 90% accuracy in each reference class, display no wrong verdict, correctly display at least half the supported claims, produce all six correct judgments on at least 90% of reports and match or exceed its predecessor’s correct count in each application and round. Each step has its own result. If the predecessor is already entirely correct, passing these checks establishes no accuracy improvement.

Whole-report scoring combines the six separately recorded responses in the one-claim and scoped steps. It never presents them as a single provider reply. References and correctness require explicit reveal in the explorer.

## Limits

Claim text and service bindings come from stored structured metadata. This experiment does not test extracting implicit assertions from authentic analyst notes. It reuses inspected controlled application faults, with correlated claims, services and rounds. Prior ML predicts incident origin and does not answer this task. The typed reference evaluator is exact by construction and does not parse unrestricted prose.

All 22 RE3 evaluation cases, nine RE3 reserves, RE3 Sock Shop and 140 RE1 reserves remain unopened. This diagnostic authorizes no fresh telemetry access. The display threshold remains uncalibrated for the task; passing the checks establishes neither operational reliability nor telecom readiness.
