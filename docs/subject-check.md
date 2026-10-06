# Check the subject before displaying a verdict

## Purpose

Wrong service bindings produced confident errors in the previous diagnostic, particularly when a sentence used a pronoun. This experiment asks Jev to check the proposed subject against the full note before the app displays a verdict.

The same 27 controlled notes contain six confirmed claims each, across nine inspected recordings. Four inputs run in three rounds: clean and wrong-service sentence baselines, plus clean and wrong-service versions of the checked request. The budget is 324 calls and 2,916 answers. Baselines ask six verdict questions; checked inputs ask six subject questions and six verdict questions in the same call.

## Input and display changes

The old question says, “Assess only the exact statement bound to service ts-config-service. Use only that service’s facts.” The checked question instead describes the binding as a proposal that may be incorrect and asks Jev to identify the sentence’s subject from the full note. Both original service ledgers, text and numerical policy remain available unchanged.

A separate subject question returns matched, conflict or unresolved. Matched means the note uniquely identifies the proposed service; conflict means it identifies another service; unresolved means the note does not identify one assertion with a unique subject. Measurements do not establish subject identity.

The app displays a checked verdict only when the subject answer is matched and both selected-answer probabilities reach 0.70. A conflicting, unresolved, low-probability or invalid subject answer blocks display. The app never substitutes a different service. Subject and verdict answers share a call; this is a combined question and instruction change, not a measured effect of adding one question alone.

## Scoring

Original sentence verdicts stay fixed. Subject references compare the proposal with the existing reviewed service annotation. Clean claims should return matched; every swapped-service claim should return conflict, including cases whose numerical verdict is unchanged by the swap.

Unsafe display means either the supplied service is wrong or the original-sentence verdict is wrong. Wrong-verdict display is also reported separately for comparison with earlier results. A coincidentally correct verdict about an incorrect subject does not count as safe guidance.

Every application, wording and round must recognize all clean and corrupted subjects, retain all clean verdicts and lose no correct clean displays versus the fresh baseline. The clean coverage minimum is 90%. Corrupted inputs must display no unsafe guidance and fewer wrong verdicts than the fresh wrong-service baseline. Missing answers remain in every denominator. These checks prevent blanket withholding from passing.

## Limits

The assistant authored and previously inspected these notes and annotations. Zero human or independent reviews occurred. All called claims have uniquely resolvable subjects, so this comparison does not test truly unresolved subjects, authentic reports or independently written text. Repeated wordings and rounds are not independent incidents. No protected recording opens.

## Results

All 324 calls completed with 2,916 valid answers. No fields needed quarantine. Train Ticket passes every application, wording and round check; Online Boutique fails all of them. The candidate fails overall and receives no promotion.

| Application / input | Correct verdicts, rounds 1–3 | Correct subject checks | Safe displayed | Unsafe displayed |
| --- | --- | --- | --- | --- |
| Train Ticket, clean baseline | 54, 54, 54 / 54 | Not asked | 54, 54, 54 | 0, 0, 0 |
| Train Ticket, clean checked | 54, 54, 54 / 54 | 54, 54, 54 / 54 | 54, 54, 54 | 0, 0, 0 |
| Train Ticket, wrong baseline | 36, 35, 35 / 54 | Not asked | 0, 0, 0 | 49, 48, 48 |
| Train Ticket, wrong checked | 40, 40, 40 / 54 | 54, 54, 54 / 54 | 0, 0, 0 | 0, 0, 0 |
| Online Boutique, clean baseline | 108, 108, 108 / 108 | Not asked | 108, 108, 108 | 0, 0, 0 |
| Online Boutique, clean checked | 106, 106, 105 / 108 | 99, 99, 99 / 108 | 81, 82, 83 | 0, 0, 0 |
| Online Boutique, wrong baseline | 78, 78, 78 / 108 | Not asked | 0, 0, 0 | 104, 103, 102 |
| Online Boutique, wrong checked | 89, 88, 88 / 108 | 101, 103, 101 / 108 | 0, 0, 0 | 1, 0, 0 |

The new subject gate reduces wrong verdict displays from eighteen per round to zero in Train Ticket, and from thirty to 1/0/0 in Online Boutique. Unsafe display counts are larger for the baseline because every deliberately swapped subject is wrong, including claims whose verdict remains correct. The app preserves the proposal rather than relabeling such guidance as safe.

### The benefit comes with a coverage loss

Train Ticket retains every clean verdict and display while correctly identifying every corrupted subject. Online Boutique loses 27/26/25 of its 108 previously correct clean displays. Its new instructions also lose 2/2/3 clean verdicts before display.

Nine clean Online Boutique subject classifications are wrong in every round. Additional withholding comes from low probabilities: eleven/ten/ten selected matched answers fall below 0.70; seven/seven/six remaining verdict probabilities do likewise. No threshold changes or retries follow these results.

### A confident subject error still passes both checks

In boundary note NWL-59bca7262cdd, “Both windows for this service meet the recorded-count minimum of 5 spans” refers to redis. Its trace mapping is missing, so the original claim is unanswerable. The wrong-service input proposes recommendationservice. In round one, the subject check selects matched at 0.76 and the evidence verdict selects supported at 0.89. The app displays a wrong verdict under the wrong service.

The clean version of that same claim also misclassifies the correct proposal, selecting conflict. This paired failure shows that adding a second model question does not make the subject assignment independently reliable. The full original note and both ledgers remain in the call.

### Cost and interpretation

Each input makes 81 calls. Checked inputs use 480,393 input tokens versus 332,187 for their matched baseline, an increase of 44.6%. Two decisions share the same request and evidence; no independent reviewer intervenes.

The result supports testing explicit subject verification, but this particular combined request fails to retain clean coverage and eliminate every unsafe display. The gate prevents many errors without establishing that the remaining guidance is reliable. Train Ticket’s success cannot substitute for the failed Online Boutique panel.

## Next experiment

Next, I will test a subject check that reads only the note and proposed binding, without numerical ledgers in that call. The evidence verdict can retain the earlier sentence/service request. This would separate text attribution from numerical assessment and test whether the same false conflict and false match recur. A new protocol must specify exact inputs, references, call budget and clean-case coverage before inference. It would still use inspected controlled notes unless a separate data allocation changes that boundary.

[Inspect the subject checks, verdicts and display decisions](http://127.0.0.1:8769/subject-check).
