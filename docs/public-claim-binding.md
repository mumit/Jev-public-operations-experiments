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

## Results

All 672 calls succeed, returning 1,152 valid verdicts. The largest request contains 16,550 bytes; input usage peaks at 4,312 tokens. The fresh lookup control repeats both earlier errors. Explicit binding corrects both in every round, without verdict regressions.

| Application and step | Correct claims, rounds 1 / 2 / 3 | All-six reports correct | Displayed correct | Wrong displayed | Correct displayed support | Complete report display |
|---|---|---|---|---|---|---|
| Train Ticket, lookup | 59 / 59 / 59 of 60 | 9 / 9 / 9 of 10 | 58 / 58 / 59 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 8 / 8 / 9 of 10 |
| Train Ticket, bound | 60 / 60 / 60 of 60 | 10 / 10 / 10 of 10 | 60 / 59 / 59 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 10 / 9 / 9 of 10 |
| Train Ticket, one claim | 59 / 60 / 60 of 60 | 9 / 10 / 10 of 10 | 59 / 59 / 60 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 9 / 9 / 10 of 10 |
| Train Ticket, scoped | 60 / 60 / 60 of 60 | 10 / 10 / 10 of 10 | 60 / 60 / 60 | 0 / 0 / 0 | 18 / 18 / 18 of 18 | 10 / 10 / 10 of 10 |
| Online Boutique, lookup | 35 / 35 / 35 of 36 | 5 / 5 / 5 of 6 | 33 / 33 / 32 | 0 / 0 / 0 | 10 / 10 / 9 of 11 | 4 / 4 / 4 of 6 |
| Online Boutique, bound | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 36 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 6 / 6 / 6 of 6 |
| Online Boutique, one claim | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 36 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 6 / 6 / 6 of 6 |
| Online Boutique, scoped | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 36 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 6 / 6 / 6 of 6 |

Binding passes both applications’ checks. One-claim requests fail Train Ticket’s no-lower-accuracy check by introducing an error in round one; their Online Boutique check passes. Scoping passes both applications’ checks. The full four-step sequence therefore fails its overall gate. A correct final step does not erase the intermediate regression.

No step displays an incorrect verdict. Train Ticket’s bound batch withholds one correct duration judgment in rounds two and three. The one-claim step withholds the same statement in rounds one and two, judging it incorrectly in the first. Scoped answers are correct and displayed throughout. Online Boutique’s bound and later steps display every correct answer; their predecessors are already correct, leaving no further accuracy error opportunity.

## The exact binding change

For adservice memory in RPT-ddcba9332c6e, the lookup question ends:

> Assess only sentence 4 in the supplied report. Use only facts for its explicitly named service; do not transfer evidence between services.

The bound question replaces that suffix with:

> Claim ID C4, sentence 4 of the supplied report. Assess only this exact statement for service adservice. Use only its own service facts; do not transfer evidence between services. Statement: For service adservice: The eligible signed change for mem is greater than zero.

Both questions keep identical preceding policy instructions and Choice criteria. Both requests keep the same two ledgers and original report text. This is a bundle of explicit ID, service and sentence changes; the experiment does not isolate which addition explains the gain.

The memory change remains 0.038857363, with 39.53% after-window missingness. Its reference is unanswerable. Fresh lookup selects supported at 0.51 / 0.44 / 0.47; bound selects unanswerable at 0.94 / 0.94 / 0.96. Every bound verdict displays. Neither the input measurements nor the eligibility policy changes.

For the sixth claim of RPT-5e9c57b96fdc, ts-preserve-other-mongo has an eligible socket change of zero. The claim asserts positive change and is contradicted. Fresh lookup selects supported at 0.50 / 0.57 / 0.54; bound selects contradicted at 0.98 / 0.96 / 0.96. Both historical failures recur in the fresh control and improve in all bound rounds.

## Grouping and scope do not behave identically

The third sentence of RPT-5e9c57b96fdc names ts-route-mongo and claims material median-duration change. That service has no eligible trace duration, so its reference is unanswerable. The bound batch selects unanswerable at 0.75 / 0.58 / 0.51. Its question, copied unchanged into a one-claim request with both ledgers, instead selects contradicted at 0.50 in round one, then unanswerable at 0.61 / 0.75. All sub-threshold answers remain withheld.

Scoping removes only the other service’s ledger, retaining the identical one-claim question and full note. It selects unanswerable at 0.98 / 0.99 / 0.99. This corrects one observed grouping error and displays the previously withheld correct judgments. It is not a repeated three-round accuracy fix: the one-claim control is already correct in rounds two and three. No recorded reasoning establishes why grouping or scoping changes these responses.

The explorer keeps raw replies separate. Batch steps contain six judgments in one provider reply; one-claim and scoped steps use six replies per report. Whole-report correctness combines the latter in application code. Per-round provider probabilities remain diagnostic, not calibrated reliability.

## What this supports

Explicit claim text and service binding improve this bounded report task on inspected evidence. The practical candidate retains numerical calculations in code, preserves the original note for inspection and supplies an explicitly scoped assertion to Jev. The bound batch already judges every claim correctly; splitting it introduces a small regression, so more calls alone do not improve reliability.

Service-scoped requests also judge every claim correctly and display them throughout. That makes scoping a separate candidate worth confirming, with its higher call count and the one-round error opportunity reported. It does not turn the full sequence into a passing experiment or establish real-report extraction.

## Next experiment

Freeze bound-batch and scoped candidates before testing independently authored reports on new public measurements. Allocate fresh cases separately and keep evaluation sealed until the text, service-attribution rules, references and budget are fixed. Evaluate claim extraction and service assignment separately from Jev’s verdicts; a correct verdict on an incorrectly extracted assertion can still mislead an analyst.

The current lookup, bound, grouping and scoping results remain unchanged. No protected recording opens under this completed diagnostic. Inspect [the binding explorer](http://127.0.0.1:8769/claim-binding) for exact requests, service scope, earlier versus fresh lookup responses and each repeated or isolated failure.
