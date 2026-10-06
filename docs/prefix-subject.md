# Resolve a subject before reading later text

Ending the note at the queried sentence improves Online Boutique's correct displays to 102/103/102 out of 108, versus 99 in every round for fresh full-note calls. It also blocks the one unsafe swapped display observed with full-note context. Subject errors, one quarantined reply and correct guidance lost to withholding remain. The prefix candidate fails overall; Train Ticket passes.

## Purpose

I tested whether later text distracts Jev from resolving a claim's subject. Both inputs ask one subject question per call. The full-note control includes the original note; the prefix ends exactly at the queried sentence.

The [earlier direct-subject batch](direct-subject.md) improved coverage but repeatedly assigned a redis pronoun to recommendationservice. Those results remain historical context. This comparison uses fresh one-question controls in both inputs, so their difference tests truncation under the same grouping.

## Data and setup

The same 27 inspected controlled notes supply six confirmed claims each, with plain, negated and boundary wording on nine recordings. Both inputs retain the literal question, answer options, complete observed service inventory and model profile. Only the note in the request state changes.

Three rounds use 972 subject calls: full and prefix for every confirmed claim. Another 162 calls ask the unchanged six numerical verdict questions under clean and deliberately swapped proposals, regardless of subject results. All 1,134 calls complete, returning 1,944 answers; 1,943 validate. No new recording or human review enters the experiment.

### What Jev sees

For NWL-59bca7262cdd, sentence s07, the full-note control includes all twelve source sentences. The prefix stops here:

> Status note.
> recommendationservice falls short of the eligible latency-90 absolute-scaled-change cutoff of 3.0.
> The same service falls short of the 25% absolute-relative-change cutoff for eligible duration_median_us.
> I attribute the incident to this service.
> Next action: inspect redis.
> redis has eligible cpu signed change above 0.
> Both windows for this service meet the recorded-count minimum of 5 spans.

The transformation removes the following health claim, later question, quoted allegation and compound or ambiguous statements. It preserves every character through s07, including the request and explicit redis assertion that introduce its antecedent. It does not rewrite the claim or supply a reference subject.

The selected subject question remains identical in both inputs. Its options include every observed service plus unresolved. Each subject call contains only this one question, the supplied note and service inventory. It receives no proposed binding or measurements. The numerical verdict call still receives the full note, unchanged ledgers and supplied binding.

## Display and scoring

Each subject reply supports both clean and swapped comparisons. Code compares the selected service with the supplied proposal; it never changes that proposal or the numerical verdict request. Display requires a matching service and both selected probabilities at or above 0.70. Missing answers and sentence quarantines withhold guidance.

Unique subject scoring counts each actual reply once. Both proposal conditions retain full denominators for safe and unsafe displays, withholding and original-verdict accuracy. Paired service and display gains and losses compare prefix with contemporary full-note calls by application, wording and round.

The frozen gate requires every subject comparison and clean verdict to be correct, no loss of correct clean baseline displays, at least 90% clean coverage and no unsafe swapped guidance in every panel and round. The full-note comparator cannot replace the candidate after inspection.

## Results

Values below correspond to rounds one, two and three.

| Application | Clean baseline displays | Full-note displays | Prefix displays | Full-note subject accuracy | Prefix subject accuracy |
| --- | --- | --- | --- | --- | --- |
| Train Ticket | 54/54/54 | 54/54/54 | 54/54/54 | 54/54/54 out of 54 | 54/54/54 out of 54 |
| Online Boutique | 108/108/108 | 99/99/99 | 102/103/102 | 106/105/105 out of 108 | 107/105/106 out of 108 |

Train Ticket passes every panel and round under both contexts. Online Boutique plain wording also passes throughout. Negated and boundary wording fail in every round.

| Online Boutique wording | Full-note displays | Prefix displays | Prefix subject accuracy |
| --- | --- | --- | --- |
| Plain | 36/36/36 | 36/36/36 | 36/36/36 |
| Negated | 32/31/31 | 32/33/32 | 35/34/34 |
| Boundary | 31/32/32 | 34/34/34 | 36/35/36 |

Against full-note controls, the prefix gains 4/4/3 correct displays and loses 1/0/0. The round-one loss is NWL-aa6833fe95e5, s07: the prefix selects the correct frontend-external subject at 0.67, below the display boundary. Service accuracy also retains regressions: paired subject gains are 2/1/3, while losses are 1/1/2.

Against the clean numerical baseline, the prefix still withholds 6/5/6 correct claims. Wrong or unresolved subjects account for 1/2/2; correct subjects below 0.70 account for 5/2/4. One additional reply is quarantined in round two. Raising coverage by changing the threshold after inspection would change the frozen policy.

### The redis subject improves, but remains uncertain

For NWL-59bca7262cdd, s07, full-note calls select recommendationservice at 0.70/0.52/0.50. Prefix calls select the correct redis at 0.51/0.47/0.45. The prefix fixes this repeated subject assignment but still withholds the clean verdict in every round.

In round one, the full-note subject clears the gate under the swapped recommendationservice proposal. The numerical verdict is supported at 1.00, while the original redis claim is unanswerable at 0.97 because trace coverage is missing. The app displays unsafe guidance. Prefix context instead identifies redis and blocks the swapped proposal.

Prefix produces no unsafe display in this run; full-note context produces one. That observed difference does not establish an operational error rate or consistent safety advantage. The neighboring health sentence, s08, still receives a wrong prefix subject in round two.

### One inconsistent reply remains quarantined

For NWL-42acf5afe858, negated s07 in round two, the prefix reply selects recommendationservice with probability 0.36 but assigns redis a higher probability, 0.37. The validator rejects that subject answer and quarantines its sentence. It does not select redis, invent a probability or retry the call.

The separate clean numerical verdict is valid and correct. The composed workflow counts only 107 eligible correct verdicts that round because the subject quarantine also blocks s07. This is an availability loss, not an additional numerical-model error. Valid sibling sentences remain eligible. Raw probabilities and the validation error remain inspectable.

## Cost

| Workflow, one proposal condition | Calls across all notes and rounds | Input tokens | Summed call latency |
| --- | --- | --- | --- |
| Clean numerical baseline | 81 | 332,187 | 18.52 seconds |
| Full-note subjects plus verdict | 567 | 1,115,208 | 105.75 seconds |
| Prefix subjects plus verdict | 567 | 1,064,601 | 101.97 seconds |

Prefix subject calls use 6.5% fewer input tokens than full-note subject calls. Including the unchanged verdict batches reduces the saving to 4.5%. Both workflows use six subject calls and one verdict batch per note. Compared with earlier batching, this grouping costs more calls; the earlier results do not isolate that cost from response variability.

Clean and swapped workflows share their subject replies and reuse their respective baseline verdicts. Their totals overlap. The experiment records 1,134 actual calls, not the sum of composed-workflow totals. Summed call latency is not end-to-end elapsed time.

## Limits and next experiment

The same assistant wrote and inspected these notes and references. Human and independent reviews remain zero. Every tested claim has a uniquely resolvable earlier subject; future-dependent and genuinely unresolved reports remain untested. Repeated calls are not independent incidents. The 22 cause-evaluation cases, 30 RE3 Sock Shop cases and 140 RE1 reserves remain unopened.

I will next test a shorter excerpt starting at the last sentence that explicitly names one observed service and ending at the queried claim. Code will select literal text using the observed inventory, without reference subjects or rewritten pronouns. If the latest named sentence mentions multiple services, the full prefix will remain. Fresh prefix controls, unchanged verdict calls and a new frozen protocol will test gains and regressions. This rule is a diagnostic for the inspected notes, not a general report-reading policy.

[Compare the redis subject and the unsafe full-note display](http://127.0.0.1:8769/prefix-subject?dataset=Online+Boutique&wording=boundary&card=NWL-59bca7262cdd&arm=wrong_full&round=1&sentence=s07).
