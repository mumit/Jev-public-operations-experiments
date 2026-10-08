# Jev reads single-incident reports well, but misses scope in a monthly report

The first publisher-report comparison is complete: 48 claims across eight reports, repeated in three rounds, with 144 once-only Jev calls. Development passes every frozen criterion. Evaluation fails because Jev confidently reverses two claims in GitHub’s multi-incident monthly report, repeating both errors in all three rounds.

This is evidence of useful bounded reading ability alongside a specific limitation. It supports continued research into an analyst assistant; it does not support automatic acceptance of Jev’s judgments. All correctness scores use the frozen assistant-reviewed references, with zero human or independent specialist reviews.

## What ran

The [frozen design](report-evidence.md) allocates four development incident/report groups and four evaluation groups. Each primary report has two claims about impact, two about cause certainty and two about recovery. Report text comes from Cloudflare, GitHub, AWS and Fastly; the claim questions and references were written for this study.

Every request supplies one claim and the unchanged contiguous prefix of complete report blocks, up to 14,000 UTF-8 bytes. The question distinguishes supported, contradicted and not established. Its instructions require matching subject, time, scope and certainty, and explicitly distinguish an unconfirmed explanation from a contradiction. Source URLs, allocation metadata and reference answers do not enter the request.

Claims, reference spans, rule code, composition, exact request hashes and the 144-call budget were committed before inference. Development results were committed and verified before evaluation. No thresholds, references or report text changed after outcomes. All 144 responses were valid; no call was retried and no telemetry recording opened.

## Results

Counts below are repeated claim judgments, not independent incidents. Each phase contains 24 unique claims from four report groups.

| Phase and method | Correct choices | Correct displayed | Wrong displayed | Sent to review |
|---|---:|---:|---:|---:|
| Development: literal rules | 9/72 | 9/72 | 0 | 63 |
| Development: Jev | 72/72 | 72/72 | 0 | 0 |
| Development: hybrid | 72/72 | 72/72 | 0 | 0 |
| Evaluation: literal rules | 0/72 | 0/72 | 0 | 72 |
| Evaluation: Jev | 64/72 | 63/72 | 6 | 3 |
| Evaluation: hybrid | 64/72 | 63/72 | 6 | 3 |

The rules match literal sentences, final clauses or simple negation opposites. They decline blocks containing uncertainty or exception language. They have no learned parameters or reference lookup. This deliberately narrow baseline supplies three correct development answers per round and none in evaluation. Gains over it do not establish superiority over a trained semantic classifier.

The hybrid uses an applicable rule first and otherwise uses an eligible Jev answer. A valid disagreement between displayed answers requests review. Invalid Jev answers also require review. In this run, the methods agree wherever a rule applies. The hybrid therefore reproduces Jev’s coverage and errors; combining them provides no observed error reduction.

Jev’s display boundary stays at 0.70. Evaluation contains 21 correct displays, two wrong displays and one withheld answer in every round. Three single-incident evaluation reports receive all 18 correct displays each. GitHub’s monthly report receives nine correct displays, six wrong displays and three withheld judgments across its 18 repeated opportunities. The overall, monthly-report, impact and recovery panels fail the no-wrong-display criterion in every round.

## Where the judgments fail

### Affected users: the active-notice condition

The March 31 claim says that the pull-request files issue affected repository admins who still had the relevant notice active. The [monthly report](https://github.blog/news-insights/company-news/github-availability-report-april-2023/) narrows impact to admins who had neither enabled the new feature nor dismissed its promotional notification. The reference reads those negated conditions together and marks the claim supported.

Jev selects contradicted at probabilities 0.74, 0.72 and 0.81. All three display. These replies contain choices and probabilities, so they do not establish why Jev interpreted the condition differently. Possible trouble with the coordinated negation needs a separate test. The reference remains an assistant interpretation of the publisher’s wording, not an independent adjudication.

### Recovery: the first improvement versus final backlog clearance

The March 29 claim says the first recovery period permanently cleared the Actions backlog. The same [report](https://github.blog/news-insights/company-news/github-availability-report-april-2023/) describes initial improvement, renewed degradation and later complete backlog recovery. The reference marks the claim contradicted.

Jev selects supported at probabilities 0.83, 0.81 and 0.78. All three display. The claim’s word “first” matters: a later statement of complete recovery does not establish that the initial improvement was permanent. Incident and phase selection are plausible failure points, but the replies provide no causal explanation.

### An unresolved cause: withholding is useful, but the choice still varies

The April 26 Copilot claim says the report confirms the contributing factors. The publisher says investigation is ongoing and defers the detailed explanation to a later report. Under the frozen policy, the reference is not established.

Jev selects contradicted in the first two rounds and not established in the third. All three probabilities remain below 0.70, so each answer goes to review. Withholding prevents a wrong displayed judgment here, while the changing underlying choice remains visible. It also withholds the correct third-round choice.

## What the result means for Jev

Jev interprets many paraphrases, dependencies and partial-recovery statements correctly on this panel. The evaluation errors show that the unchanged full-report input is insufficient for reliable display when several incidents and recovery stages share one document.

A higher threshold would conceal observed errors by changing coverage on inspected cases. This study does not select another threshold. The more useful next investigation concerns input scope: identify the incident being checked, retain its complete evidence and preserve qualifications about affected users and recovery stages.

The sample is small and purposive. All sources were inspected during the audit, the reports may appear in pretraining, and postmortems contain hindsight. The assistant wrote the claims and reviewed the references. Passing development and failing evaluation are research results on this bounded task, not live triage accuracy, production reliability or telecom readiness.

## Follow-up: explicit incident selection

The user selected explicit analyst incident selection on October 7. The [separate scope diagnostic](incident-scope.md) compares fresh full-report calls, a selection field with the full report and the selected incident section. It is now complete and fails: correct displayed coverage stays unchanged, while narrowing the input makes the unresolved-cause confirmation claim more confident under the historical policy.

That disagreement distinguishes judging a claim about what a report confirms from judging whether its underlying cause is established. The user selected literal claim judgment for the next diagnostic. Historical references and scores stay unchanged; a separate contract, reference version and protocol must precede further calls.

## Inspect and replay

Open [the comparison](http://127.0.0.1:8769/report-comparison) to inspect each claim, method, round, probability and reference rationale. This checkout retains the exact full-text requests for local inspection. Browsing invokes no model.

The public supplement preserves original provider answer projections, usage, validation, hashes and execution summaries. Protocols, claims, references and scored outcomes remain in Git. These replies contained only model, answers and usage, so the projected provider payloads preserve every received field. Complete publisher reports and full-text requests are excluded from the release.

Public replay recomputes choices, display decisions, hybrid composition, denominators and gates using the precommitted literal-rule projections. Exact request and literal-rule reconstruction also require the matching local source snapshots. Those are different verification boundaries; the public bundle does not reproduce missing source text.
