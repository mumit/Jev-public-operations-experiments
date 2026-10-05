# Do the report candidates hold up on fresh measurements?

Exact claim binding fixed the two repeated report-reading errors. Service-scoped requests also judged every claim correctly, while one-question grouping introduced an isolated error. This confirmation compares the two successful candidates on nine untouched public recordings and new controlled notes.

## Purpose

The question is whether either fixed approach retains accurate, useful verdicts on fresh measurements. Bound requests ask six questions against both service ledgers in one call. Scoped requests ask the same questions separately, each against only its own service ledger. Both retain the entire note.

This comparison changes question grouping and evidence scope together. The earlier four-step diagnostic isolates those changes; this study compares their final candidates and call costs.

## Data and notes

The new allocation consumes the nine remaining RE3 reserves: three Train Ticket auth f4 recordings, three Online Boutique email f4 recordings and three email f5 recordings. All repetitions of each service/fault group stay together. The earlier 22-case cause-evaluation panel, RE3 Sock Shop and 140 RE1 reserves remain unopened.

The user chose controlled notes written before measurement access. Their literal wording, proposition kinds, polarity rules and selection logic freeze before download. Preparation chooses two services from observations alone: the largest observed change and a coverage gap, or the smallest observed change if every service has traces. It supplies six assertions about metric magnitude, duration magnitude, causality, metric direction, recorded span counts and health. Hashes choose wording and polarity without consulting verdicts. The strongest eligible metric supplies the metric channel; missing eligibility uses a deterministic channel fallback.

These are newly authored controls, not notes from an independent analyst or authentic incident reports. New measurements and new wording change together, so differences from historical results cannot isolate those effects. Fault repetitions and three model rounds are correlated, not additional independent cases.

## References and input

The unchanged typed evaluator computes references from recorded observations under the frozen numerical policy. Eligible metrics need numeric change and at most 20% missingness in both windows. Material magnitude starts at three scaled units. Duration change needs at least five spans per window and a positive starting duration; material magnitude starts at 25%. Recorded counts describe sampling. Measurements alone establish neither health nor causality.

Code computes ledger facts. Jev receives the full note, exact claim text, explicit service name and the applicable ledger or ledgers. Neither proposition metadata nor references enter requests. Claim spans and service bindings come from preparation annotations. Their audit checks the supplied text byte-for-byte; automatic extraction and service attribution are separately marked **not evaluated**. Prior ML predicts incident origin and does not answer this verdict task.

## Frozen experiment

The source, text and allocation plan commits before download. Exact notes, references and request hashes commit before inference. Three serial rounds permit 27 bound calls and 162 scoped calls, yielding 324 verdicts on 54 claims. There are no retries, warmup calls, threshold searches, case replacements or text changes after preparation.

Each candidate must complete all calls in each application and round, reach 90% correctness in each reference class, display no wrong verdict, correctly display at least half the supported claims and judge all six claims correctly in at least 90% of reports. An absent reference class makes the check insufficient to assess, rather than passing. The inherited 0.70 display boundary remains uncalibrated for this task.

Both candidates receive separate results. Paired fixes, losses, repeated choices, display variability and actual call costs remain visible even if aggregate checks pass. Missing replies retain their planned denominators. A wrong contradiction counts as a displayed error just as a wrong supported claim does.

## Results

All 189 calls succeed, returning 324 valid verdicts. The largest request contains 16,521 bytes; recorded input usage peaks at 4,371 tokens. Both candidates pass the frozen checks in both applications. Every claim receives the correct verdict in all three rounds.

| Application and candidate | Correct claims, rounds 1 / 2 / 3 | All-six reports correct | Displayed correct | Wrong displayed | Correct displayed support | Complete report display |
|---|---|---|---|---|---|---|
| Train Ticket, bound batch | 18 / 18 / 18 of 18 | 3 / 3 / 3 of 3 | 18 / 18 / 18 | 0 / 0 / 0 | 6 / 6 / 6 of 6 | 3 / 3 / 3 of 3 |
| Train Ticket, scoped | 18 / 18 / 18 of 18 | 3 / 3 / 3 of 3 | 18 / 18 / 18 | 0 / 0 / 0 | 6 / 6 / 6 of 6 | 3 / 3 / 3 of 3 |
| Online Boutique, bound batch | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 36 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 6 / 6 / 6 of 6 |
| Online Boutique, scoped | 36 / 36 / 36 of 36 | 6 / 6 / 6 of 6 | 35 / 36 / 36 | 0 / 0 / 0 | 11 / 11 / 11 of 11 | 5 / 6 / 6 of 6 |

Train Ticket has six supported, three contradicted and nine unanswerable references; Online Boutique has eleven, six and nineteen. Every class is present without balancing or case replacement. No paired accuracy fix or loss occurs because both candidates are already correct throughout.

Bound verdicts and display decisions stay stable for all claims. Scoped verdicts also stay stable, but one Online Boutique display decision changes. In FRC-884b59dfe067, the fifth assertion reads:

> Neither recorded window count for adservice is below five spans.

Adservice has no mapped trace, so both recorded counts are unknown. The reference is unanswerable. Bound selects that verdict at 0.99 in every round; scoped selects it at 0.65 / 0.80 / 0.72. The first scoped answer is correct but withheld at the unchanged 0.70 boundary. Later answers display. Missing observations never become zero counts.

## Call cost and candidate choice

| Candidate | Calls across all rounds | Recorded input tokens | Summed call latency |
|---|---|---|---|
| Bound batch | 27 | 111,006 | 5.45 seconds |
| Scoped facts | 162 | 253,080 | 28.09 seconds |

Scoped requests use six times as many calls and about 2.28 times as many input tokens, without an accuracy gain. Summed latency adds the recorded duration of serial calls; it is not a production throughput estimate or a controlled provider speed benchmark. The study records no billed monetary cost.

Bound batch is the preferred candidate for the next bounded workflow: it displays every correct verdict, uses fewer calls and retains both ledgers for inspection. Scoping remains a preserved comparator. The previous inspected-data scoping success does not establish that it will outperform a bound batch on fresh inputs.

Inspect [the fresh confirmation](http://127.0.0.1:8769/fresh-claims?dataset=Online+Boutique&card=FRC-884b59dfe067&field=statement_e&arm=scoped&round=1#inspect) for the exact note, supplied bindings, missing trace facts and each actual response. Historical comparisons remain separate.

## Limits and next step

Nine recordings in three fault groups can reveal failures but cannot establish an operational error rate. Typed references are exact for these authored propositions; they are not specialist judgments about unrestricted prose. This result supports bounded claim checking with supplied bindings. It does not establish causal diagnosis, automatic report extraction, analyst benefit or telecom readiness.

The next useful experiment should remove the supplied claim and service bindings. That requires a defined extraction task and a separately annotated collection of ordinary notes, with extraction completeness, claim meaning and service attribution scored before verdict accuracy. An analyst workflow that accepts explicit claims is the simpler alternative. Neither path opens another protected recording without a new allocation protocol.
