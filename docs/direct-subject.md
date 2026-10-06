# Identify the subject without a proposed binding

Direct extraction improves displayed coverage, but the candidate still fails overall. Train Ticket passes every panel and round. Online Boutique displays 97/101/99 correct clean claims out of 108, versus 90/90/92 for fresh proposal checks and 108 for the unchecked baseline. Both checked workflows withhold every swapped display in this run.

## Purpose

I separated subject identification from proposal checking to test a different question: which service does this sentence describe? Jev selects a service from the note; application code compares it with the supplied binding. The numerical verdict still uses that supplied service. The app does not repair the binding.

This follows the [separate-call comparison](separate-subject.md), which improved coverage but still misclassified subjects. This new task changes instructions and answer options as well as removing proposals. Its results cannot establish proposal anchoring as the cause of earlier failures.

## Data and controls

The diagnostic reuses 27 controlled notes on nine inspected recordings, with plain, negated and boundary wording. Each note contains six confirmed claims. Train Ticket supplies 68 observed service names; Online Boutique supplies 12. The complete inventories come from input packets, not subject annotations.

Each of three rounds includes one direct subject call per note, two fresh proposal checks (clean and deliberately swapped) and two unchanged numerical verdict calls. All 405 calls complete; all 2,430 answers validate, without quarantines. Every verdict call runs regardless of subject results.

The proposal-check and numerical verdict bodies remain exact controls from the earlier comparison. The direct request contains only the full note and observed service names. Six questions ask for the unique subject, or unresolved. It contains no proposed binding, measurements or reference answers.

## What changed in the request

Consider sentence s07 in NWL-59bca7262cdd:

> Both windows for this service meet the recorded-count minimum of 5 spans.

The relevant preceding text says “Next action: inspect redis.” and “redis has eligible cpu signed change above 0.” The original subject is redis.

The proposal-check question includes “Proposed service: redis.” for the clean input, or recommendationservice for the swapped input. Its options are matched, conflict and unresolved.

The direct question instead asks: “Identify the subject of the EXACT sentence in the full note context.” It includes the literal sentence and offers all 12 observed service names plus unresolved. The state contains the unchanged note and service-name inventory. Neither the clean nor swapped proposal enters this call.

One recorded direct reply serves both comparisons. If Jev selects redis, code marks the clean proposal matched and the swapped proposal conflict. If Jev selects recommendationservice, those comparisons reverse. An unresolved answer matches neither proposal. Code never substitutes the extracted service into the verdict request.

## Display and scoring

Display requires the numerical verdict probability to reach 0.70. A proposal check must also return matched at 0.70 or above. Direct extraction must select the supplied service at 0.70 or above. Missing answers and the union of sentence quarantines block display.

The frozen gate requires every subject comparison and clean verdict to be correct, no loss of correct clean baseline displays, at least 90% clean coverage, and zero unsafe swapped displays in every application, wording and round. Swapped guidance is unsafe even when its verdict coincides with the original reference.

Unique direct-service accuracy counts each shared reply once. Display scoring retains both proposal conditions and their full denominators. The unchanged verdict replies supply all three workflows; their equal verdict accuracy is not a new inference gain.

## Results

Values below correspond to rounds one, two and three.

| Application | Clean baseline displays | Proposal-check displays | Direct displays | Direct subject accuracy |
| --- | --- | --- | --- | --- |
| Train Ticket | 54/54/54 | 53/53/54 | 54/54/54 | 54/54/54 out of 54 |
| Online Boutique | 108/108/108 | 90/90/92 | 97/101/99 | 105/107/105 out of 108 |

Train Ticket preserves every correct baseline display and blocks every swapped proposal. Online Boutique plain wording also passes throughout. Its negated and boundary panels fail in every round.

| Online Boutique wording | Proposal-check displays | Direct displays | Direct subject accuracy |
| --- | --- | --- | --- |
| Plain | 36/36/36 | 36/36/36 | 36/36/36 |
| Negated | 26/25/26 | 30/33/31 | 35/36/34 |
| Boundary | 28/29/30 | 31/32/32 | 34/35/35 |

Direct extraction gains 7/11/8 correct Online Boutique displays against the fresh proposal check and loses 0/0/1. The round-three loss is NWL-9dc6904d0134, s08: “I attribute the incident to this service.” Jev selects the correct productcatalogservice at 0.62, below the display boundary. The proposal check displays that claim.

Against the clean baseline, direct extraction still withholds 11/7/9 correct Online Boutique verdicts. Incorrect or unresolved subjects account for 3/1/3; correct subjects below 0.70 account for the remaining 8/6/6. Lowering the threshold after inspection would change the frozen policy, not validate this candidate.

### The repeated redis failure remains

For NWL-59bca7262cdd, s07, direct extraction selects recommendationservice at 0.61/0.56/0.43 rather than redis. Removing the proposal does not fix this repeated subject error.

The clean verdict remains correctly unanswerable at 0.98 because redis lacks eligible trace coverage. The swapped verdict is supported at 1.00 for recommendationservice. Under the swapped proposal, code therefore finds a match to Jev’s incorrect subject, but withholds because subject probability stays below 0.70. Zero unsafe display here depends on withholding; it does not mean the model resolved every conflict.

Both current checked workflows display zero unsafe guidance. This run demonstrates a coverage gain over the proposal check, not a safety advantage over that comparator.

## Cost

| Workflow, one proposal condition | Calls across all notes and rounds | Input tokens | Summed call latency |
| --- | --- | --- | --- |
| Clean numerical baseline | 81 | 332,187 | 15.29 seconds |
| Clean proposal check plus verdict | 162 | 483,627 | 29.14 seconds |
| Clean direct extraction plus verdict | 162 | 871,563 | 32.74 seconds |

The direct workflow uses about 80% more input tokens than the proposal-check workflow, mainly from the complete service-choice inventory. Clean and swapped direct workflows share the same 81 direct calls; both checked workflows also reuse their respective baseline verdicts. Their workflow totals overlap. The experiment records 405 actual calls, not the sum of displayed workflow totals. Summed call latency is not end-to-end elapsed time.

## Limits and next experiment

The same assistant wrote and previously inspected these notes and references. Human and independent reviews remain zero. Every tested subject uniquely resolves; authentic reports, genuinely unresolved subjects and analyst usefulness remain untested. Repeated replies are not independent incidents. The 22 cause-evaluation cases, 30 RE3 Sock Shop cases and 140 RE1 reserves remain unopened.

I will next test whether later mentions distract subject resolution. A fixed transformation can give the subject call only the unchanged note prefix ending at the queried sentence, retaining every earlier antecedent and the full observed inventory. Both full-note and prefix controls will ask about one subject per request, so another question’s longer prefix cannot reintroduce later text. The earlier batch results will remain historical context, and numerical verdict calls will stay unchanged. This removes later questions and compound statements without inserting a reference subject or rewriting the claim. A new committed protocol must precede that comparison; these inspected notes will remain development diagnostics.

[Inspect the exact calls](http://127.0.0.1:8769/direct-subject?dataset=Online+Boutique&wording=boundary&card=NWL-59bca7262cdd&arm=wrong_direct&round=1&sentence=s07).

The [prefix-context follow-up](prefix-subject.md) is now complete. Its contemporary full-note controls use one question per call. Prefix improves coverage and blocks the one observed unsafe full-note display, but retains subject errors and fails overall. These earlier batch replies remain historical context.
