# Can Jev judge a written claim against telemetry?

This diagnostic tests a narrower task than cause selection: does the supplied evidence support a written statement, contradict it, or leave it unanswerable? The previous study exposed numerical reading errors. Here, code can make the arithmetic explicit while Jev matches a statement to the resulting facts.

## Data and references

The study reuses 32 service cards from 16 inspected public RCAEval recordings: ten Train Ticket and six Online Boutique recordings. Each card has three constructed statements, one per verdict. A deterministic hash selects a decidable proposition and its opposite, then an unanswerable proposition, and shuffles their positions. This balance stays out of the requests.

Statements cover metric magnitude, signed direction, duration change and recorded span counts. Unanswerable statements include insufficient measurements, service health and incident causality. For example, a socket change of −3 with both missing fractions at 20% supports “The socket metric meets the material-change policy” and contradicts its opposite. At 21% missing, either statement becomes unanswerable under the declared policy. A missing trace mapping supplies no count; an explicitly recorded zero supplies a count. Neither proves health or cause.

A separate evaluator calculates references from typed propositions and original observations. It is exact by construction, not a parser for unrestricted reports. The earlier fitted ML predicts an originating service and cannot be scored against this different target. No new ML model is trained.

These are authored test statements: fixed templates applied to public measurements. They are not authentic incident reports, specialist-reviewed judgments or held-out incidents. Opposite statements, repeated cards and repeated rounds remain correlated. Balanced templates can create shortcuts that real reports do not offer.

## The input comparison

Both inputs receive identical statements and policy definitions. Each of three independent Choice questions asks for one verdict; the questions cannot see one another’s replies.

- **Observations:** original metrics, missing fractions, spans and durations for one service.
- **Fact ledger:** the same original measurements, with metric eligibility, absolute scaled changes and eligible duration arithmetic made explicit. It retains trace observations and missing values. It contains no claim-specific verdict, injected answer or material/quiet classification.

For an eligible signed change of −3, the ledger adds `absolute_scaled_change: 3` and `eligible_for_change_policy: true`. For duration 100 → 75 microseconds with five spans in each window, it adds `relative_change: -0.25`. With four ending spans, eligibility becomes false and the calculated change remains null. This lets code handle arithmetic while Jev handles the written claim.

## Frozen diagnostic checks

The plan precedes preparation; a committed protocol fixes every request before inference. Three rounds compare both inputs: 192 calls and 576 individual answers. Calls run serially without retries or warmup.

The ledger is the predeclared candidate. Each application and round must reach 90% accuracy for every reference class, display no false supported statement, display at least half of supported references correctly, and match or exceed observations-only total accuracy. All calls must succeed. A selected-answer probability of at least 0.70 controls display; it is an inherited diagnostic boundary, not calibrated reliability.

Passing these author-set checks does not open protected data or establish operational fitness. All 22 RE3 evaluation cases, nine remaining RE3 reserves, RE3 Sock Shop and 140 RE1 reserves stay unopened. Results and the next decision will follow the bounded run.
