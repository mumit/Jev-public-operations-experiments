# Clarifying speech acts and assertion families

## Purpose

The sentence-review run judged and displayed every accepted Jev claim correctly, but lost ten claim opportunities during extraction. Service assignments were correct throughout. This diagnostic tests whether clearer task definitions recover useful claims without accepting wrong bindings.

## What changes

Four inputs form a paired comparison on the same nine inspected notes. Baseline repeats the exact earlier extraction request; role changes only the shared speech-act definition; meaning changes only the shared assertion-family definition; combined changes both. The combined input is the candidate. The single changes explain its behavior and cannot replace it after results.

| Dimension | Earlier definition | Added distinction |
|---|---|---|
| Speech act | One endorsed assertion; questions, requests and unendorsed quotes are non-assertions; independently checkable assertions form a compound. | Eligibility and its numeric condition form one bounded policy assertion. Zero or negative values still make a factual assertion. An ambiguous subject does not turn a claim into a request. Generic examples contrast requests, questions, one-property alternatives and compound claims. |
| Assertion family | Map metric magnitude/direction, duration magnitude, recorded span adequacy, health or cause. | A recorded-count statement concerns span adequacy, rather than service health. Explicit healthy/unhealthy wording belongs to health; an operational implication does not. Examples distinguish one family from a compound containing several. |

The new definitions apply to the bounded task already encoded in the references. They do not split arbitrary prose into atomic facts. Generic examples supply speech-act and family labels, without case service names, telemetry or reference verdicts. Every independent question sees the shared state, so changing one definition may also affect other dimensions.

The notes, sentence boundaries, observations, references, service/channel inventories, question instructions, option keys, other definitions and 0.70 boundaries stay fixed. Actual accepted bindings drive the unchanged bound-batch verdict task. Sentence-level quarantine preserves valid siblings without correcting invalid answers.

## Comparison and controls

Three fresh rounds include every note and input, with rotated input order. Historical baseline responses stay separate. The earlier parser and supplied-annotation results provide labeled historical context; this protocol does not rerun or pool them with the new calls. Earlier fitted ML predicts injected origin, a different target, and remains unscored here.

Scores retain every sentence and routable-claim opportunity. Report speech act, service and exact meaning separately from acceptance, conditional verdict accuracy, end-to-end correctness and whole-note coverage. A correct verdict on a wrong binding fails. Paired gains and losses remain visible even when totals tie.

## Protocol

The plan and producers commit before the exact extraction protocol, which permits 108 once-only calls: nine notes, four inputs, three rounds. Actual per-input bindings receive a separate committed verdict protocol before at most 108 dependent calls. Maximum budget: 216 calls and 9,072 answers. No retries, threshold fitting, post-result substitution, fresh measurements or protected-panel access.

Combined must pass the inherited absolute research checks in each application and round, accept no wrong binding, and lose no role, service, meaning, correct-binding or end-to-end count against its fresh baseline. Complete-note coverage still requires at least 90%. These are descriptive research criteria, not an operational error budget.

## Limits

The definitions respond to already inspected failures. The notes and annotations come from the experiment author and assistant, with only three fault groups. A favorable result would show inspected-data development, not independent report performance, specialist-reviewed semantics, causal diagnosis or telecom readiness. The earlier failures remain frozen.

## Results

All 216 calls completed with 8,385 valid answers. No sentence required quarantine. Each input had 54 claim opportunities in each of three rounds, or 162 repeated opportunities. These are repeated measurements on nine notes, not 162 independent reports.

| Input | Correct bindings and verdicts | Correct verdicts displayed | Paired gains / losses against fresh baseline |
|---|---:|---:|---:|
| Unchanged baseline | 153/162 | 153 | Reference |
| Speech-act changes only | 154/162 | 153 | 5 / 4 |
| Assertion-family changes only | 160/162 | 160 | 7 / 0 |
| Both changes, declared candidate | 142/162 | 142 | 3 / 14 |

Every accepted binding was correct, and every resulting verdict was correct. No nonclaim, compound or ambiguous-subject candidate passed acceptance; no unsafe verdict was displayed. Speech-act-only withheld one correct Train Ticket verdict in round three. The other losses occurred before verdict generation.

### Results by application and round

Each entry gives correct end-to-end claims in rounds one, two and three. Complete-note counts require all six routable claims to receive correct verdicts.

| Input | Train Ticket claims, out of 18 | Train Ticket complete notes, out of 3 | Online Boutique claims, out of 36 | Online Boutique complete notes, out of 6 |
|---|---|---|---|---|
| Baseline | 15, 16, 15 | 0, 1, 1 | 36, 36, 35 | 6, 6, 5 |
| Speech act | 17, 17, 16 | 2, 2, 1 | 35, 34, 35 | 5, 4, 5 |
| Assertion family | 16, 18, 18 | 1, 3, 3 | 36, 36, 36 | 6, 6, 6 |
| Combined | 15, 16, 15 | 1, 1, 0 | 32, 32, 32 | 3, 3, 3 |

The combined candidate fails both application checks. Train Ticket's unchanged totals conceal three recovered and three lost claims across rounds. Online Boutique loses eleven claims without a gain. Pooling these outcomes would obscure the repeated regression.

Assertion-family wording is the useful diagnostic lead: six gains in Train Ticket and one in Online Boutique, with no lost correct binding. It was not the declared candidate and cannot replace the combined input after inspection. It also falls short of the inherited Train Ticket coverage requirement in round one. Its Online Boutique speech-act correctness falls from 71/72 to 70/72 in round two despite improved accepted-claim coverage, so it does not uniformly improve every extraction measure.

### Follow a recovery and a regression

In Train Ticket note NEX-ca19c97a64d8, sentence s07 reads: “Its recorded span count reaches five in both windows.” The antecedent is ts-preserve-other-mongo. Baseline round one selects the correct span-count family but assigns it probability 0.68, below the unchanged 0.70 gate. Assertion-family wording raises that selected-family probability to 0.94. All required fields pass; the verdict is correctly unanswerable because the ledger lacks the required counts. This recovers an honest limit of the evidence, rather than declaring the service healthy.

The added family definition explicitly says:

> A sentence about recorded span counts is span_adequacy; it does not assert service health.

Online Boutique note NEX-07ced3f518de, sentence s06 reads: “adservice has an eligible signed latency-90 change that is greater than zero.” Baseline round one correctly classifies a single assertion with probability 0.74 and displays a supported verdict. Speech-act-only lowers that probability to 0.66; combined lowers it to 0.63. Both retain the correct selected labels but withhold the claim. In round three, assertion-family-only recovers this same claim by moving the selected assertion probability from baseline's 0.68 to 0.86.

The speech-act addition intended to clarify that an eligibility qualifier and its numeric condition form one policy assertion. Its examples did not reliably increase acceptance. Every question receives the entire shared definition set, so even a family-only change can alter the role probability. The recorded outputs show this interaction; they do not reveal Jev's internal reasoning or establish calibrated confidence. More detailed instructions are not automatically better.

[Inspect the span-count recovery](/extraction-contrast?dataset=Train+Ticket&card=NEX-ca19c97a64d8&arm=meaning&round=1&sentence=s07&dimension=kind#input) or [compare the combined regression](/extraction-contrast?dataset=Online+Boutique&card=NEX-07ced3f518de&arm=combined&round=1&sentence=s06&dimension=role#input). The inspector shows baseline and selected definitions, each field's actual distribution, the acceptance decision and the dependent verdict. Reference answers appear only after explicit reveal.

### Calls and input size

Each input used 27 extraction and 27 verdict calls. Provider-reported input tokens and summed measured request latency cover both phases:

| Input | Input tokens | Summed latency, seconds |
|---|---:|---:|
| Baseline | 580,448 | 14.20 |
| Speech act | 586,266 | 13.53 |
| Assertion family | 586,559 | 13.99 |
| Combined | 586,084 | 13.83 |

Latency sums are observations from this run, not throughput or service guarantees. The extraction definition additions increase extraction tokens; fewer accepted claims shorten the combined verdict requests. Earlier parser and annotation scores remain historical context, without new calls.

## Next experiment

The next candidate should keep only the assertion-family changes and compare them with baseline on new controlled wording, frozen before inference. Keep the same numerical policy and thresholds, score extraction separately from verdicts, and include count-versus-health contrasts, eligibility qualifiers, negative values, pronouns, compounds and ambiguous subjects. A new note set can test transfer across language while reusing inspected telemetry; it cannot establish fresh-incident or authentic-report performance.

Before another run, choose that controlled-language diagnostic or an independently authored report study. The former can proceed with the existing public measurements. The latter needs another author's notes and references. Protected telemetry remains unopened: 22 cause-evaluation cases, 30 RE3 Sock Shop cases and 140 RE1 reserves. No candidate has been promoted or deployed.

The separate [new-note wording test](public-note-language.md) now selects family-only prospectively. Its ten gains and twenty-seven losses fail both application checks; the earlier seven-claim gain does not transfer uniformly. The earlier results above remain frozen.
