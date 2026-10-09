# Correct interpretation, fewer displayed answers

Report-knowledge definitions correct the earlier error in every round and choose all 90 repeated reference answers correctly. They display 85 correctly and withhold five. The unchanged literal control chooses 87 correctly, displays 87 correctly and one incorrectly, and withholds two. The candidate fails eight of twelve frozen checks because it loses correct displays. New-report confirmation remains unopened.

## Question and data

The [whole-report transfer](cross-reports.md) exposed a persistent distinction: a claim about what a report establishes differs from a claim about the underlying event. I selected one controlled diagnostic of that distinction before allocating further reports.

All 27 earlier claims and references remain unchanged. Three companion claims use the same power-failure report, bringing the panel to 30 distinct claims. The three Cloudflare reports, full extraction, titles and source snapshots stay fixed. This is development on inspected reports, not fresh validation. The assistant wrote and reviewed the companions before model outcomes; human entries and independent reviews remain zero.

The power report explicitly says the breaker configuration time is unknown. Four claims distinguish the propositions:

| Claim | Reference |
|---|---|
| The report establishes when the breaker settings involved in the March 26 failure were configured. | Contradicted |
| The breaker settings were configured in 2022. | Not established |
| The report says the configuration time of the breaker settings is unknown. | Supported |
| The report says there is no remaining uncertainty about when the breaker settings were configured. | Contradicted |

Explicit uncertainty conflicts with the first and fourth reporting assertions. It neither supports nor contradicts the second event-date assertion. These references follow the previously selected literal-claim contract, not an independently reviewed standard.

## Exact transformation

Both arms receive byte-identical state: the original claim, exact whole-report title and complete extracted report. No semantic classification, answer, evidence annotation or reference enters state. The literal control reproduces the earlier literal request exactly. The candidate changes only the question instructions and three verdict descriptions.

The added instructions read:

> First identify the proposition being asserted: an underlying incident fact, or what this report says, knows, identifies or establishes. For a report-knowledge assertion, evaluate the claimed reporting status itself. Explicit uncertainty can contradict an assertion of established knowledge even though the underlying event fact remains unknown. For an incident-fact assertion, an unknown fact remains not established unless an incompatible fact is stated. Return the verdict for the original complete claim. Do not substitute the underlying fact for a reporting assertion.

The criteria reinforce that distinction. Supported requires the complete claim to match the report, including its uncertainty. Contradicted includes explicit uncertainty that conflicts with asserted report knowledge. Not established covers unreported or unknown underlying facts, while excluding reporting assertions that explicitly conflict with stated uncertainty.

Open “Exact Jev inputs” in the [inspector](http://127.0.0.1:8769/report-knowledge?claim=cf-power-2024-c5&round=1&input=knowledge) and switch definitions to compare the complete instructions, criteria and identical source text. The committed producer retains the exact wording; the summary above does not replace its wire evidence.

## Frozen setup and requirements

The committed plan, companion annotations, reference pack and exact protocol precede 180 once-only calls: 30 claims, two definitions and three rounds. Jev remains 1.13.0 with 32,768 context tokens and the fixed 0.70 display boundary. The largest request is 26,782 bytes under the 64,000-byte cap. All calls succeeded and validated, using 952,146 input tokens. No retry, reference correction, threshold fitting or telemetry access occurred.

Every round must correct and display the original failure and all companions, gain at least one correct choice, lose no correct choice or display, and display no wrong answer. Each report must also display at least six correct answers and represent all three classes. Failure blocks new-source confirmation under this plan.

## Results and losses

| Definitions | Correct choices | Correct displayed | Wrong displayed | Sent to review |
|---|---:|---:|---:|---:|
| Literal control | 87/90 | 87/90 | 1 | 2 |
| Report knowledge | 90/90 | 85/90 | 0 | 5 |

The candidate correctly chooses and displays “contradicted” for the original establishment claim at 0.99 in all three rounds. The control still chooses “not established,” at 0.64, 0.71 and 0.69. Its middle-round answer crosses 0.70 and displays incorrectly. Historical transfer outcomes remain unchanged; these are fresh replies on inspected cases, illustrating variability rather than a revised historical score.

The candidate gains three correct choices and displays on that one repeated claim, with no correct choice losses. It loses five correct displays on two other distinct claims:

| Correct answer withheld by candidate | Reference | Candidate probabilities, rounds 1/2/3 |
|---|---|---|
| The breaker settings were configured in 2022. | Not established | 0.63 / 0.65 / 0.72 |
| A single identified customer sent every request that poisoned a process during the June 20 incident. | Not established | 0.63 / 0.69 / 0.63 |

The control displays both correctly throughout. The date companion passes display eligibility only in round three. The single-customer claim remains below the boundary in every round. Consequently all global checks and all CDN report checks fail; the power report passes only round three. DNS passes throughout. Four of twelve checks pass.

Choosing the correct class and displaying useful guidance are separate outcomes. The revised definitions improve this panel’s interpretation, but their coverage loss prevents promotion. Provider probabilities are not calibrated operational error estimates. Lowering the threshold after inspection would change the experiment rather than satisfy its frozen criteria.

The exact-string rule matches none of these claims and withholds every answer. It is a narrow control; no new ML model was trained for this text task.

## What remains

New-report confirmation is blocked by failed development gates. No new report was allocated or opened. Earlier failures, references and protected telemetry allocations remain intact.

The next decision is whether to pursue another separately frozen question diagnostic or change the analyst-facing display objective. My recommendation is to preserve this candidate as an interpretation finding and first define the acceptable cost of review: how much correct coverage can be lost to avoid a wrong display? That decision needs an explicit prospective requirement and fresh confirmation. This panel cannot establish analyst benefit, independently agreed interpretation or telecom readiness.

## Inspect and replay

The inspector exposes both verdict distributions, every class/report/global gate, the original replies, reference rationales and locally retained full inputs. Browsing makes no model calls. Public answer evidence excludes publisher text and full-text requests; replay checks original payloads, fixed rule projections, fingerprints, denominators and gates. Matching local snapshots additionally allow exact request reconstruction. See [restoration](evidence.md).
