# Reading publisher-written incident reports

The next comparison asks whether Jev can interpret operational language more usefully than literal rules. The task is narrow: judge whether a claim about service impact, cause certainty or recovery follows from a supplied report excerpt. A correct answer describes what the publisher reports; it does not independently verify the incident.

The source audit is complete and the experiment design is frozen. Claim annotation, baseline implementation and exact request preparation come next. **No new model calls or telemetry downloads have occurred.** The earlier clarification comparison remains a failed candidate; this study starts with different source material and its own allocation.

## What the source audit found

Twelve documents cover ten incident or monthly-report groups across Cloudflare, GitHub, AWS and Fastly. Ten passed extraction and identity checks. The two shorter GitHub updates were retrieved but failed the frozen check: it expected the month in the body, while the date appeared in the page title. Their failed records and raw snapshots remain preserved; neither becomes an extra trial.

Eight primary reports passed the audit. Four incident groups supply development claims; four supply evaluation claims. Two other groups remain audit-only. All three GitHub documents about the October 2018 outage stay in the development group. A monthly availability report stays intact, including incidents mentioned outside its nominal month.

| Publisher report | Allocation | A useful distinction |
|---|---|---|
| [Cloudflare control plane, November 2023](https://blog.cloudflare.com/post-mortem-on-cloudflare-control-plane-and-analytics-outage/) | Development | Configuration and analytics availability differ from traffic delivery. |
| [GitHub incident analysis, October 2018](https://github.blog/news-insights/company-news/oct21-post-incident-analysis/) | Development | Database metadata and Git repository data have different impact scopes. |
| [AWS service event, December 2021](https://aws.amazon.com/message/12721/) | Development | Internal network failures affect dependent services at different times. |
| [Fastly outage, June 2021](https://www.fastly.com/blog/summary-of-june-8-outage) | Development | Restoring most traffic differs from complete recovery. |
| [Cloudflare Workers KV, October 2023](https://blog.cloudflare.com/cloudflare-incident-on-october-30-2023/) | Evaluation | A dependency outage differs from an outage of every deployment. |
| [Cloudflare WAF outage, July 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/) | Evaluation | A deployed rule, its resource effect and mitigation are distinct statements. |
| [GitHub availability, April 2023](https://github.blog/news-insights/company-news/github-availability-report-april-2023/) | Evaluation | Several incidents need separate service and recovery scopes. |
| [AWS S3 disruption, February 2017](https://aws.amazon.com/message/41926/) | Evaluation | Recovery of one subsystem does not establish recovery of every operation. |

The [July 2020 Cloudflare report](https://blog.cloudflare.com/cloudflare-outage-on-july-17-2020/) and [March 2022 GitHub availability report](https://github.blog/news-insights/company-news/github-availability-report-march-2022/) are audit-only. The [initial GitHub report](https://github.blog/news-insights/company-news/october21-incident-report/) and [recovery update](https://github.blog/news-insights/incident-update/) remain related, failed audit entries.

These are independently publisher-written reports. The claims and reference judgments will be assistant-written and assistant-reviewed. Those are separate facts: independent report authorship does not provide independent reference validation.

## What Jev will receive

Each request will contain one claim and a contiguous excerpt from its report. Extraction keeps the publisher's wording and paragraph order, normalizes HTML whitespace and separates table cells. The excerpt stops before the first complete block that would exceed 14,000 UTF-8 bytes. It does not skip ahead to find a useful answer or cut a paragraph halfway through a qualifier.

Some GitHub article containers include a trailing author credit. That page text is outside the operational claim task; annotations must cite incident content.

The input will omit the source URL, split assignment, identity checks and reference answers. It will preserve service names, times, negation and qualifications in the report text. There will be no generated summary or calculated causal features.

For example, an impact claim may incorrectly extend a configuration outage to traffic delivery. A recovery claim may turn recovery of most traffic into complete recovery. Jev must judge that extension against the supplied wording. These examples describe the task; the exact claim pack has not yet been written.

References will cite exact blocks in the supplied excerpt, identify the affected service or operation and explain the judgment. Material outside the excerpt cannot justify an answer. If the excerpt does not resolve a claim, the answer is **not established**, even if the full postmortem or external knowledge supplies a likely answer. An ambiguous reference stays visible as an unscored slot rather than being replaced silently.

## The frozen comparison

Each of the eight primary reports has six planned claim slots: two about impact, two about cause certainty and two about recovery. That gives 48 unique claims, repeated in three rounds. Development permits 72 once-only Jev calls. Evaluation permits another 72 only if the development candidate passes. There are no retries or additional calls for the hybrid.

| Method | Responsibility |
|---|---|
| Literal rules | Answer only when a fixed wording and scope condition applies; otherwise request review. No fitted parameters or reference lookups. |
| Jev | Choose supported, contradicted or not established from the unchanged excerpt and claim. The fixed model is Jev 1.13.0. |
| Rules with Jev assistance | Use an applicable rule first; otherwise use an eligible Jev answer. Conflicts and invalid answers require review. This is the sole candidate. |

The hybrid and standalone Jev reuse the same reply. Their probability boundary remains 0.70. That boundary controls display; it does not establish a calibrated error rate.

Before inference, a separate protocol must freeze the claims, references, rule implementation, composition, instructions, choices, exact requests, source fingerprints and request-size checks. The current checkpoint freezes the design, **not an executable inference protocol**.

## What counts as an improvement

Every development round must meet all of these criteria:

- No wrong displayed judgment in any incident or topic panel.
- At least 80% of planned claims correctly displayed in every incident panel and every topic panel.
- At least two additional correct displays over rules, with no correct rule display lost.
- Complete recorded evidence for all planned calls. Invalid or missing replies count as withheld in the planned denominators.

These criteria prevent withholding everything from looking successful. Scores will separate answer accuracy, display coverage, wrong displays, supported/contradicted/not-established judgments and paired gains or losses. Each incident, topic and round remains visible.

A failed development criterion stops evaluation calls. A passing candidate proceeds unchanged to the four evaluation groups, under the same criteria. Standalone Jev results cannot replace the declared hybrid candidate after outcomes are known. Threshold changes or new wording require another experiment.

## What this study can establish

This is a small, purposively selected public sample. All sources were inspected during the audit, and some may appear in model pretraining. Evaluation separates incident groups; it is not wholly unseen material to the assistant. Postmortems also contain hindsight that an analyst would lack during an outage.

A useful result would show a repeatable gain over rules on this bounded reading task. It would not establish live triage accuracy, root-cause discovery, anomaly detection or telecom readiness. References will have zero human or independent specialist reviews. Any remaining uncertainty in their interpretation must stay explicit.

## Preservation and next step

The repository records the source URLs, allocations, hashes, extraction provenance, failed audit entries and frozen design. Full HTML and report text stay in the ignored local cache. Future public evidence will contain scoped paraphrases, judgments, probabilities, failures and paired scores, rather than complete publisher reports or full-text requests. Exact replay requires matching source snapshots; a later publisher page may differ.

The next step is to write and review the claim pack against the retained excerpts, implement the rules and freeze the exact request protocol. Only then can the development comparison begin. Existing telemetry allocations and completed studies remain unchanged.

Inspect [the source audit](http://127.0.0.1:8769/report-evidence). Verify retained source snapshots with `python -m scripts.audit_report_sources verify`; use `verify-catalog` to check public provenance without the local cache. Neither action invokes Jev.
