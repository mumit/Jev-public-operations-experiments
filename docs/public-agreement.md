# When Jev and ML disagree

I tested whether disagreement with ML could identify misleading Jev recommendations. The rule first applies Jev's frozen 0.70 probability boundary, then marks an eligible lead as review-required when ML chooses another service. ML does not replace Jev's answer. Both choices remain visible to the analyst.

## Data

The [RCAEval RE1 collection](https://github.com/phamquiluan/RCAEval) provides fresh metric recordings from the same applications and five familiar fault types: CPU, memory, disk, network delay and network loss. These cases had not entered the earlier RE2 experiments. They test transfer across recordings, not unseen fault families or a new network.

A committed schema audit opened five Train Ticket auth-service CPU cases and five Sock Shop carts CPU cases. Both groups became development and stayed outside evaluation. Their source labels fit the existing pipeline without conversion.

The evaluation contains 50 Train Ticket and 50 Sock Shop cases. Each application has ten service/fault groups, all five repetitions intact and ten cases per fault type. The committed selection uses sorted service index minus fault index modulo five, keeping offsets one and two. Seventy cases per application remain unopened. Selection preceded telemetry inspection; preparation rejects duplicate metric bytes, unsupported schemas, missing published candidates and inconsistent timelines rather than replacing cases.

These are controlled faults with supplied injection boundaries and published injected-service references. Public model pretraining exposure is unknown. The experiment does not measure incident detection, analyst investigation time or telecom readiness.

## Setup

The experiment keeps Jev 1.13.0, named summaries, the originating-service question, all observed candidates and the fitted Online Boutique ML unchanged. Train Ticket has 64 observed candidates; Sock Shop has 15. Jev receives before/after medians, baseline-scaled changes and missing fractions in source units. References, ML choices and display boundaries stay outside its request.

RE1 lacks the disk I/O and socket series used in the earlier collection. The frozen ML records those features as unavailable; placeholder zeros are not observed measurements. This is a fixed transfer model, not ML trained specifically for either application.

Three serial rounds made 300 calls with rotated case order and no retries or warmup. All succeeded. Exact request fingerprints were committed before execution. The largest request is 50,440 bytes, below the unchanged empirical cap. No prompt changes, fitting or threshold search occurred.

Each saved response receives two paired decisions: the original single-lead-or-withhold rule, and that rule with the ML agreement check. This isolates the effect of routing from new model calls. “Review required” means investigating the conflicting choices; “withheld” means the original Jev boundary offered no lead. Retained leads still require analyst review.

The descriptive gate requires every round to start with an erroneous eligible Jev lead, route at least one error to review, retain correct guidance and reduce the wrong fraction among retained leads. It is not an operational error budget. Rounds without eligible errors cannot establish error reduction.

## Results

| Application | Round | Original boundary: correct / wrong | With agreement: correct / wrong | Wrong sent to review | Correct sent to review | Already withheld |
|---|---:|---:|---:|---:|---:|---:|
| Train Ticket | 1 | 27 / 0 | 25 / 0 | 0 | 2 | 23 |
| Train Ticket | 2 | 25 / 0 | 22 / 0 | 0 | 3 | 25 |
| Train Ticket | 3 | 25 / 0 | 22 / 0 | 0 | 3 | 25 |
| Sock Shop | 1 | 42 / 0 | 41 / 0 | 0 | 1 | 8 |
| Sock Shop | 2 | 40 / 0 | 40 / 0 | 0 | 0 | 10 |
| Sock Shop | 3 | 43 / 1 | 42 / 1 | 0 | 1 | 6 |

Disagreement catches no eligible wrong lead. Every additional review case contains a correct Jev choice and an incorrect ML choice. These referrals involve three distinct Train Ticket cases and one Sock Shop case, all network-loss faults. Repeated referrals are not separate incidents.

Train Ticket has no eligible Jev errors to test. Sock Shop has one in round three, and the agreement check retains it. Removing a correct lead raises that round's wrong fraction from 1/44 to 1/43. Neither application establishes the intended benefit. The frozen assessment's `no_error_opportunity` status means the every-round opportunity requirement was not met; it does not mean Sock Shop had no error.

Unfiltered Jev matches 42/43/43 Train Ticket references and 49/49/47 Sock Shop references across the three rounds. Frozen ML matches 37/50 and 48/50; change ranking matches 41/50 and 46/50. The original probability boundary already withholds 15/18/18 correct Train Ticket choices and 7/9/4 correct Sock Shop choices. Agreement adds withholding without correcting the model itself.

Routing stays stable on 46/50 Train Ticket and 44/50 Sock Shop cases. Consistent choices and consistent display decisions remain different properties.

## Agreement on the wrong service

In `AGR-6362c127a31c`, the published cause is user-service network loss. Jev and ML both choose orders. Jev's choice probability changes from 0.63 to 0.61 to 0.72, so the frozen boundary withholds twice and retains the wrong lead in round three. Agreement provides no warning.

User latency-90 changes from 0.009005 to 0.244669, a baseline-scaled shift of 2617.10. Orders changes from 0.023805 to 0.416129, a shift of 993.52. Change ranking selects user; ML ranks orders, front-end and user. The inspector exposes these competing symptoms and the fitted feature contributions. The measurements do not reveal Jev's internal reasoning.

## Disagreement on a correct lead

In `AGR-5fb5dffa8521`, Jev correctly selects auth-service for a network-loss fault in all three rounds, at probabilities about 0.78, 0.75 and 0.78. ML selects inside-payment-service, so the agreement check sends every eligible correct lead to review.

Auth latency-50 changes from 0.203984 to 0.404275, with a scaled shift of 6.41. Inside-payment changes from 0.025 to 0.023750, with a shift of -0.12. Change ranking also selects auth. ML's highest score is -3.88 for inside-payment; this ranks candidates and is not a calibrated cause probability. A transferred ML model can suppress useful Jev guidance as well as challenge an error.

## Next decision

This panel does not support adding agreement as a reliability filter. Disagreement can still help an analyst compare competing explanations, but it cannot decide which model is right. Agreement can hide a shared mistake.

I will preserve both rules and their evidence. The next choice is whether to add causal evidence to Jev, train a stronger ML comparator, or confirm the unchanged rule on the remaining RE1 reserves. Richer causal evidence is the recommended direction because the fresh panel includes a mistake both models share. Any new input or fitting needs a separate protocol and untouched cases; the current evaluation cannot validate its success.

Inspect [the shared wrong lead](http://127.0.0.1:8769/agreement?dataset=Sock+Shop&case=AGR-6362c127a31c&round=3#inspect) and [correct guidance sent to review](http://127.0.0.1:8769/agreement?dataset=Train+Ticket&case=AGR-5fb5dffa8521&round=1#inspect).
