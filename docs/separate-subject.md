# Identify the subject before reading measurements

## Purpose

The joint subject check reduced wrong-service displays but lost correct coverage in Online Boutique and retained one unsafe result. This diagnostic separates reading the note from judging its numerical evidence. The subject call receives only the full note and proposed service; a second call judges the exact statement with the earlier service binding and both observation ledgers.

I selected this split as the candidate and kept fresh joint requests as a comparator. Both clean and deliberately swapped service proposals run in three rounds on the same 27 controlled notes. No new recordings open.

## Exact input changes

The text-only state becomes `{"note": "<full original note>"}`. It contains neither service ledgers nor verdict questions. Its six subject questions remain byte-for-byte identical to the joint questions, including the original sentence, proposed service and matched/conflict/unresolved options. Removing measurements does not remove the policy thresholds written in the sentences themselves.

For example, the subject question asks whether a proposed recommendationservice binding matches “Both windows for this service meet the recorded-count minimum of 5 spans,” read in the full note. It sees the preceding redis assertion and requested check, but no redis or recommendationservice numerical facts.

The separate verdict call retains the earlier authoritative binding wording: “Assess only the exact statement bound to service … Use only that service’s facts.” It never receives or follows the subject result. A conflict blocks display; the app does not change the supplied service and rerun the verdict under a corrected one. This tests a guard around an imperfect binding, not service repair.

The fresh joint comparator retains the completed joint request exactly, including both ledgers and all twelve questions. These fresh responses distinguish the new workflow from another sample of the old one. The change removes ledgers and verdict questions from subject context and restores the earlier verdict wording. It does not isolate ledger removal alone.

## Execution and scoring

The frozen budget is 486 calls and 3,888 answers. The first phase makes 324 text-only/joint calls; the second makes 162 verdict calls regardless of subject results. Separate phase protocols record every exact body before inference. Each call runs once, with no retries or threshold search.

Separate display requires matched at probability at least 0.70 and a verdict probability at least 0.70. Invalid fields quarantine their sentence. A quarantine in either call blocks its combined display, without repairing the raw answer or discarding valid sibling sentences. Baseline and separate scoring deliberately share the same verdict replies, so their verdict accuracy is not an independent comparison.

Original numerical verdicts and reviewed service annotations remain the references. A wrong supplied service is unsafe even when its verdict coincides with the original answer. All confirmed subjects uniquely resolve; unresolved-subject performance is unmeasured.

Every application, wording and round must correctly classify every clean and swapped subject, retain all clean verdicts, lose no safe clean displays against the fresh baseline and reach at least 90% clean coverage. Wrong-service inputs must display no unsafe guidance and strictly fewer wrong verdicts than their baseline. The joint comparator faces the same checks but cannot replace the declared candidate after results.

## Limits

These are assistant-authored notes on nine inspected public application recordings, with zero human or independent reviews. Repeated rounds and wordings are correlated. Public-data exposure during model training is unknown. Passing would support a bounded diagnostic workflow, not authentic-report reliability, causal diagnosis or telecom readiness. Protected data remains unopened.

## Results

Not run yet. Inputs, references and acceptance checks will freeze before provider calls.
