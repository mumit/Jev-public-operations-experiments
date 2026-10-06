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

All 486 calls completed with 3,888 valid answers and no quarantined fields. Train Ticket passes every wording and round; Online Boutique passes plain wording but fails negated and boundary wording. The separate candidate fails overall and receives no promotion.

Counts below use all wording styles. Each tuple gives rounds one, two and three; denominators are 54 Train Ticket claims and 108 Online Boutique claims per round.

| Application / workflow | Correct verdicts | Correct subject checks | Safe displayed | Unsafe displayed |
| --- | --- | --- | --- | --- |
| Train Ticket, clean baseline | 54, 54, 54 | Not asked | 54, 54, 54 | 0, 0, 0 |
| Train Ticket, clean joint | 54, 54, 54 | 54, 54, 54 | 54, 54, 53 | 0, 0, 0 |
| Train Ticket, clean separate | 54, 54, 54 | 54, 54, 54 | 54, 54, 54 | 0, 0, 0 |
| Train Ticket, wrong baseline | 35, 35, 34 | Not asked | 0, 0, 0 | 49, 49, 48 |
| Train Ticket, wrong joint | 41, 41, 40 | 54, 54, 54 | 0, 0, 0 | 0, 0, 0 |
| Train Ticket, wrong separate | 35, 35, 34 | 54, 54, 54 | 0, 0, 0 | 0, 0, 0 |
| Online Boutique, clean baseline | 108, 108, 108 | Not asked | 108, 108, 108 | 0, 0, 0 |
| Online Boutique, clean joint | 105, 106, 105 | 100, 99, 100 | 84, 83, 83 | 0, 0, 0 |
| Online Boutique, clean separate | 108, 108, 108 | 101, 102, 100 | 92, 91, 91 | 0, 0, 0 |
| Online Boutique, wrong baseline | 78, 78, 78 | Not asked | 0, 0, 0 | 102, 105, 102 |
| Online Boutique, wrong joint | 88, 90, 88 | 101, 101, 100 | 0, 0, 0 | 0, 0, 0 |
| Online Boutique, wrong separate | 78, 78, 78 | 104, 103, 103 | 0, 0, 0 | 0, 0, 0 |

### Coverage improves, but subject errors remain

The separate workflow retains every clean numerical verdict, because it uses the unchanged baseline verdict replies. That is a property of the composition, not a new independent verdict-accuracy gain. The joint instructions lose 3/2/3 Online Boutique verdicts; their errors remain withheld.

Against the fresh joint comparator, separate Online Boutique display gains are 9/9/10 claims and losses are 1/1/2, for a net gain of eight in each round. The same negated note, NWL-fe6c9911a37a sentence 7, loses a correct joint display in every round. Train Ticket gains one display in round three and loses none.

Online Boutique still loses 16/17/17 correct displays against baseline. Incorrect subject choices account for 7/6/8 losses; correctly selected matched answers below 0.70 account for the remaining 9/11/9. None comes from the separate clean verdict probability. All 36 plain-wording claims display correctly in each round, while negated and boundary text retain attribution errors and low probabilities.

### Withholding does not mean the subject was understood

The earlier unsafe example remains instructive. In NWL-59bca7262cdd sentence 7, “Both windows for this service meet the recorded-count minimum of 5 spans” refers to redis. The correct redis proposal receives conflict at 0.65 in the text-only call, despite the separate verdict correctly returning unanswerable at 0.98.

The swapped recommendationservice proposal receives matched at 0.52. Its authoritative verdict call returns supported at 1.00. The app withholds it because the subject probability falls below 0.70, not because Jev correctly recognizes the conflict. The fresh joint call also selects matched, at 0.69, and withholds its supported verdict at 0.90. The historical joint error no longer displays in either fresh treatment, so this run does not establish a safety advantage over the fresh joint comparator.

Every swapped-service baseline display is unsafe, even when its verdict happens to match the original reference. Both subject workflows block every swapped display in this run. Original-verdict accuracy under the wrong binding remains visible; no service replacement hides those errors.

### Cost and interpretation

Across all notes and rounds, each clean or wrong joint workflow uses 81 calls and 480,393 input tokens. Each corresponding separate workflow uses 162 calls and 483,627 tokens, just 0.7% more tokens but twice as many calls. Clean summed call latency rises from 16.65 to 28.28 seconds; wrong-service latency rises from 17.87 to 29.15 seconds. These sums are not end-to-end elapsed time.

The text-only subject portion consumes 151,440 tokens; its verdict portion consumes 332,187. Those verdict calls also supply the baseline scores and are counted once in the 486-call run budget. Workflow comparisons include both required calls.

The split improves useful coverage on these inspected notes, preserves numerical verdicts and contains every corrupted display observed here. It still fails the requirement to resolve every clean and corrupted subject and preserve all clean displays. This supports a narrower follow-up on attribution, not promotion or an operational reliability claim.

## Next experiment

Next, I will ask Jev to identify the actual subject from the note without seeing a proposed binding. Code can then compare that answer with the proposal. This removes the proposed service as a possible anchor while keeping numerical assessment separate. The comparison needs fresh controls, the same clean-coverage checks and a new frozen protocol; current notes remain inspected development evidence.

[Inspect separate calls, fresh joint controls and display decisions](http://127.0.0.1:8769/separate-subject).
