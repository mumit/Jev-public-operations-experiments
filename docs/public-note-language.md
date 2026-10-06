# Family-only extraction on new wording

## Purpose

Assertion-family wording recovered seven claims in the earlier diagnostic without losing a correct binding. Combining it with speech-act changes regressed. This study selects family-only wording prospectively as the candidate and compares it with baseline on new controlled notes. It tests transfer across language on inspected measurements.

## Data and wording

Three notes describe each of the nine earlier recordings: plain paraphrases, negation and boundary-focused wording. The 27 notes retain the same six resolvable propositions per recording, facts and numerical reference verdicts. They supply 162 routable claims, 324 sentence candidates and 243 atomic assertions. Each input runs three rounds, giving 486 repeated claim opportunities. These repeats are not independent incidents or reports.

Each note retains a heading, two metric claims, a duration claim, a recorded-count claim, a health claim, a cause claim, a requested check, a question, an explicitly unendorsed allegation, a compound containing two assertions and a single assertion with an ambiguous subject. Code supplies generic sentence boundaries; compounds and ambiguous subjects go to review. Intact service blocks change position by a stable hash, preserving local pronoun antecedents.

| Property | Earlier wording | New examples |
|---|---|---|
| Recorded counts | Its recorded span count reaches five in both windows. | Each recorded window contains at least five spans; neither window has fewer than five; both windows meet the minimum of 5 spans. |
| Metric direction | Eligible signed change is greater than zero, or zero or negative. | Positive/nonpositive; not zero or negative/not greater than zero; above/at or below 0. |
| Metric magnitude | Absolute scaled magnitude at least/below 3.0. | Absolute scaled change of at least/below 3.0; not below/does not reach 3.0; meets/falls short of the cutoff. |
| Service health | That service is healthy. | The same service is in a healthy state; this service is healthy. |

The assistant wrote these notes and transferred the existing typed annotations by meaning before inference. Numerical references remain unchanged. The notes do not come from an independent analyst, and the source measurements have already been inspected. “New wording” describes new strings and presentation, not authentic reports or untouched incidents. Negative numerical claims retain their earlier polarity; the study does not introduce negative health or cause claims, or arbitrary thresholds.

## Inputs and policy

Both inputs receive identical new text, candidate boundaries, service/channel inventories and six independent questions per sentence. Baseline uses the original definitions. Candidate changes only the shared assertion-family definition to the exact family-only wording from the previous diagnostic. Role, service, channel, duration-measure and polarity definitions stay fixed; every question still sees the shared state.

The added definition distinguishes counts from health, keeps positive and negative properties in the same family, and maps magnitude, direction and duration claims to the existing numerical policy. No reference verdicts or measurements enter extraction. The dependent request uses only actual accepted text, Jev's assigned subjects and those subjects' fact ledgers. Code keeps arithmetic in the ledger. It does not repair bindings from the annotations.

Both extraction acceptance and verdict display require the unchanged 0.70 chosen-option probability. These probabilities are not calibrated operational risk estimates. Any invalid field quarantines its whole sentence; globally valid siblings remain eligible. Model, envelope, usage, context or network failures stop execution. No retry, repair, threshold fitting or input substitution is permitted.

## Frozen comparison

The plan and all new producers commit before data preparation. Exact extraction fingerprints and separate reference hashes commit before 162 once-only calls. Actual bindings, extraction evidence and exact dependent requests commit before at most 162 verdict calls. The maximum is 324 calls and 13,608 answers. No new measurement or protected panel opens.

Scores retain every claim, including withheld or missing answers. Applications, wording styles and rounds remain separate. A correct verdict on the wrong binding fails end-to-end scoring. Paired gains and losses stay visible alongside accepted correct bindings, full-note coverage, wrong accepted claims, unsafe displays and actual call costs. Historical results provide context only.

Family-only must pass the inherited absolute coverage and safety checks and lose no role, service, meaning, accepted-correct or end-to-end count against baseline in each application, wording and round. The all-wording panels must pass too. Passing would support this bounded controlled-language task; it would authorize neither protected-data access nor deployment.

## Results

All 324 calls completed. Five extraction fields had a selected option inconsistent with the distribution maximum; the frozen validator quarantined their sentences. They concern requests, unendorsed allegations and a compound, rather than the six routable claims. Valid siblings continued. No verdict field failed validation. The run preserves 12,543 raw answers and 12,538 validated answers without repairs.

| Input | Correct accepted bindings and end-to-end judgments | Wrong accepted bindings | Displayed verdicts | Displays failing the binding/verdict policy |
|---|---:|---:|---:|---:|
| Baseline | 447/486 | 2 | 449 | 2 |
| Fixed family-only definition | 430/486 | 0 | 430 | 0 |

Every correctly bound accepted claim received a correct, displayed verdict. Family-only recovered ten correct claims and lost twenty-seven against baseline, a net loss of seventeen. Train Ticket gained four overall; Online Boutique lost twenty-one. The candidate fails both all-wording application checks. Only Train Ticket's plain-paraphrase panel passes every-round criteria. No candidate is promoted.

### Application, style and round

Entries give correct end-to-end claims in rounds one, two and three. Each Train Ticket style has 18 routable claims; each Online Boutique style has 36.

| Application | Style | Baseline | Family-only | Family-only complete notes per round |
|---|---|---|---|---|
| Train Ticket | Plain paraphrases | 17, 17, 18 | 18, 18, 18 | 3/3, 3/3, 3/3 |
| Train Ticket | Negation | 15, 16, 16 | 16, 17, 16 | 2/3, 2/3, 2/3 |
| Train Ticket | Boundary wording | 16, 18, 17 | 17, 17, 17 | 2/3, 2/3, 2/3 |
| Online Boutique | Plain paraphrases | 36, 36, 36 | 34, 34, 34 | 4/6, 4/6, 4/6 |
| Online Boutique | Negation | 30, 29, 28 | 27, 27, 25 | 1/6, 1/6, 0/6 |
| Online Boutique | Boundary wording | 34, 35, 33 | 32, 31, 32 | 2/6, 2/6, 2/6 |

Pooled candidate coverage remains high in Train Ticket, at 51/54, 52/54 and 51/54, but incomplete notes and regressions in separate styles fail the frozen criteria. Online Boutique falls to 93/108, 92/108 and 91/108. The negation panel exposes the largest loss; even the plain panel loses two claims in every round. These results do not justify replacing the original definition across ordinary notes.

### What fails inside

Boundary note NWL-0f527b766ed7, sentence s06, says: “adservice has eligible latency-90 signed change above 0.” Both inputs select the correct service, family and polarity. Baseline round one assigns metric-direction probability 0.86 and displays a correct supported verdict. Family-only assigns 0.52 and withholds it. This claim is lost in all three rounds. The definition changed, while the note, questions, facts and 0.70 gate did not. The saved probabilities show the loss mechanism; they do not explain Jev's internal reasoning.

In negated Train Ticket note NWL-7432a7ac9d8b, sentence s04, “Neither recorded window for this service has fewer than five spans” refers to ts-ticket-office-mongo. Baseline round one assigns ts-admin-travel-service with probability 0.71, accepts the wrong subject and displays supported using that service's counts. The intended service lacks counts, so the reference is unanswerable. Family-only selects the correct subject at 0.67 and withholds it. This avoids an incorrect display through review; it does not recover a correct automated judgment.

Online Boutique boundary note NWL-59bca7262cdd, sentence s06, says: “redis has eligible cpu signed change above 0.” Baseline round two labels it recorded span adequacy at 0.77 and accepts it. The dependent request still contains the raw metric claim, so its supported verdict happens to match the reference. The wrong family makes it fail end-to-end scoring. Family-only selects metric direction at 0.57 and withholds it. One baseline display therefore has a wrong verdict from a wrong subject; the other has a correct verdict alongside a wrong extraction label. Both violate the declared binding policy, but they are different failures.

[Inspect the repeated coverage loss](/note-language?dataset=Online+Boutique&wording=boundary&card=NWL-0f527b766ed7&arm=meaning&round=1&sentence=s06&dimension=kind#input), [the wrong-subject display](/note-language?dataset=Train+Ticket&wording=negated&card=NWL-7432a7ac9d8b&arm=baseline&round=1&sentence=s04&dimension=service#input), or [the coincidentally correct verdict](/note-language?dataset=Online+Boutique&wording=boundary&card=NWL-59bca7262cdd&arm=baseline&round=2&sentence=s06&dimension=kind#input).

### Costs and limits

Each input used 81 extraction and 81 verdict calls. Baseline consumed 1,738,945 provider-reported input tokens and 38.50 summed request seconds; family-only used 1,743,962 tokens and 38.97 seconds. These latency sums describe this run, not throughput or a service guarantee. Fewer accepted claims shorten the candidate's verdict requests despite its longer extraction definition.

The earlier seven-claim gain was specific to its wording and replies. The new controlled text shows an uneven safety/coverage trade-off, not a reliable general improvement. Both inputs still misclassify some nonclaim or compound roles, although none passes acceptance. Family-only has some wrong service or family choices too; withholding keeps them out of displayed verdicts. No observed wrong candidate display is an operational error-rate estimate.

## Next experiment

The next choice concerns the analyst workflow. A structured claim entry or confirmation step could make the service and intended property explicit before Jev checks the telemetry. Earlier supplied-binding studies support testing that path; they do not prove an interactive workflow's usefulness. An alternative is another free-text extraction study, with new wording and a separate frozen definition or service-resolution change.

Analyst confirmation is the recommended next step: show the original sentence, proposed subject and normalized property; require confirmation or correction before the verdict request. Measure correction burden, missed claims and verdict accuracy separately. This would test whether Jev helps after the analyst resolves the fragile extraction step. It requires a new task and protocol; no threshold is lowered or failed input promoted here. Protected telemetry remains unopened.
