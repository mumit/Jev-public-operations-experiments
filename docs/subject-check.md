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

## Status

The plan and producers precede preparation. Exact requests and references will be committed before once-only calls. Results are not yet measured.
