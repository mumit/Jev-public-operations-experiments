# Confirming the claim before judging it

The latest wording test exposed a practical tradeoff. The family-definition candidate displayed no wrong bindings, but accepted 430 correct claims across 486 repeated opportunities, compared with the baseline's 447 correct and two wrong bindings. Once an accepted claim had the correct binding, Jev judged its evidence correctly. Extraction remains the weak step.

I added an analyst review workflow to examine whether confirming the service and meaning makes this bounded task useful. Open [Claim review](http://127.0.0.1:8769/claim-review). This stage builds and checks the workflow; it has no new model results.

## What the reviewer sees

The page uses the 27 controlled notes from the [wording study](public-note-language.md), on nine already inspected recordings. Each note contains twelve sentence candidates, including questions, requests, unendorsed quotations, compound assertions and unresolved subjects. These are assistant-written notes, not authentic incident reports.

Every proposal comes from the family-definition arm's first recorded round. That choice applies to all notes; it does not select the best round for each sentence. The page shows the full note, Jev's proposed fields and its automatic acceptance status. Its minimum relevant probability is an uncalibrated model output, not an estimate of correctness.

Reference answers and recorded verdicts stay off this page. Reviewers can still access the older inspectors, so this is not a blinded study. Previous familiarity with these notes must be disclosed when interpreting a review.

## How to review a note

1. Choose an application, wording and note. Read the full note before resolving local pronouns.
2. Inspect each sentence's role, subject service, assertion family and polarity. For metric or duration claims, also check the named channel or measure.
3. Confirm only one endorsed assertion with a unique subject and a meaning inside the declared policy. Correct fields before confirming when needed. Withhold questions, requests, unendorsed quotations, compounds, unresolved subjects and meanings outside the policy. The tool does not split compounds or rewrite the source text.
4. Inspect the request preview. Complete all twelve sentence decisions, then download the review JSON. A draft download lets you resume elsewhere.

Positive polarity asserts the family's defined property; negative asserts its opposite. For example, “neither window has fewer than five spans” asserts the positive span-count property even though it uses grammatical negation. “The service did not cause the incident” asserts negative causality. The numeric rules cannot establish either causal attribution or overall service health; their verdict remains unanswerable under this policy.

Confirmation records the reviewer's judgment. A clear assertion can receive human confirmation even when Jev withheld it below 0.70. The workflow does not change that historical automatic boundary or invent a replacement model probability. Structural validation checks inventories and required fields, not whether the reviewer understood the sentence correctly.

## What changes in the input to Jev

Earlier bound requests passed the exact sentence, model-assigned service, full note context and service facts. The extracted family mainly controlled acceptance and scoring; it did not explicitly enter the verdict question.

The new preview passes the **analyst-confirmed service and bounded meaning**, followed by the exact original sentence. A reviewed count assertion, for example, includes:

```json
{"channel":"none_or_unclear","kind":"span_adequacy","measure":"none_or_unclear","polarity":"positive","service":"example-service"}
```

The actual inventory determines the service name. The request supplies only the confirmed services' ledgers. Numerical eligibility, thresholds and supported/contradicted/unanswerable definitions remain unchanged. Only confirmed sentences receive questions; withholding every sentence produces no request.

This makes a correction visible in the actual model input. It also creates a new treatment whose accuracy must be measured. Human confirmation does not guarantee a correct binding, and these previews are not evidence that the new request performs well.

## What the export records

The JSON contains the workflow fingerprint, note ID, original recorded Jev proposals and final confirm/withhold decisions. Local validation reconstructs corrections and the exact request from verified public evidence. It rejects incompatible fingerprints, changed proposals, unknown options, duplicate JSON keys and incomplete notes. No name, credential, invented probability or verdict answer enters the export.

Drafts stay in the browser's local storage until cleared. Downloading exports nothing to the server. The app remains read-only and makes no model calls. Browser imports help resume drafts; the strict Python validator is required before an exported review can support an experiment.

After downloading a completed review, validate it from the repository:

```bash
uv run --locked --extra public-data python -m scripts.validate_claim_review /path/to/NWL-example-review.json --preview-output /path/to/new-preview.json
```

The validator checks the full historical evidence chain and creates a local preview, not a runnable hosted protocol. The output path must be new. Keep review files out of Git unless their reviewer has agreed to publication.

## What comes next

The first blocker is an actual human review. Complete one whole note and supply its export to test the handoff. Automated browser checks exercise the controls but do not count as analyst decisions or measured correction effort.

Then freeze the review set, final decisions, comparison, exact requests and call budget before any once-only verdict run. Compare automatic proposals with human-confirmed bindings, reporting corrected fields, withheld sentences, new mistakes and verdict coverage separately. A pilot can report the number of final corrections; these exports do not measure elapsed review time, intermediate edits or the time saved against unaided reading. Measuring those needs a separate prospective protocol and genuine human sessions.

No protected recordings open in this stage. The previous model results, frozen sources and seventeen public evidence assets remain unchanged.
