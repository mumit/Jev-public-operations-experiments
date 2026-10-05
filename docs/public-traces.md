# Does trace evidence help Jev?

Adding trace summaries did not improve Jev's recommendations consistently. All 78 development calls succeeded, but neither application met the frozen promotion criterion. The 22 evaluation cases and 25 reserve cases remain unopened.

## Purpose and data

I compared the existing named metric input with the same input plus recorded span timing and service dependencies. Both versions use identical cases, metrics, candidate services and questions. The comparison tests an input addition, not a new display policy.

[RCAEval RE3](https://github.com/phamquiluan/RCAEval) supplies metrics and traces for Train Ticket and Online Boutique code faults. RE1 supplies metrics only, so it cannot support this addition. RE3 also changes the fault collection: its scores cannot establish an improvement over earlier RE1 or RE2 results. Within RE3, the paired metric-only control isolates the effect of adding trace context.

The schema audit opened four Train Ticket auth/F1 recordings and three Online Boutique ad/F3 recordings. Development adds three route/F2 and three email/F2 recordings, making 13 cases in four intact service/fault groups. Evaluation has 22 cases in seven different groups; reserve has 25 in seven more. A group keeps correlated repetitions of the same application's injected service and fault together. These splits separate groups, not applications or entirely new fault types. All 140 RE1 reserves and RE3 Sock Shop telemetry remain unopened.

The published injected service supplies the reference. The incident boundary is given, not detected. Public pretraining exposure is unknown. These controlled application faults do not represent a telecom network or measure investigation benefit.

## What the audit found

The seven audited recordings contain both before/after spans, unique trace/span identities and consistent time units. Jaeger uses microseconds for `startTime` and `duration`; the pipeline checks `startTime // 1000 == startTimeMillis`. See the [Jaeger data model](https://raw.githubusercontent.com/jaegertracing/jaeger/main/internal/uimodel/model.go).

Coverage limits affect the usable evidence:

- Online Boutique records seven trace services but has no `adservice` span, including in recordings where the publisher names adservice as the injected cause. Missing instrumentation cannot establish service health.
- Every audited Train Ticket status code is missing. Online Boutique mixes numeric codes whose meaning is not uniform. The input preserves source code counts without classifying them as success or error.
- Two audited recordings have unresolved parent links: 13 in one Train Ticket recording and eight in one Online Boutique recording. Unknown links remain unknown.
- Metric candidates can include services absent from traces, including unrelated application names. The pipeline preserves all candidates; reference answers never repair the candidate set or map service aliases.

Trace IDs, operation text, source paths, fault labels and published answers stay outside requests. Preparation verifies publisher checksums and reconstructs every summary from source telemetry.

## Exactly what changed in Jev's input

The trace arm adds one `trace_context` field to the original state. For each exact-matched observed service, it contains before/after span and distinct-trace counts, median and p90 inclusive duration, median and p90 uncovered duration, uninterpreted status counts and the missing-status fraction. Resolved cross-service parent/child counts form a separate dependency table. Coverage records missing parents, window-crossing spans, uninstrumented candidates and unmapped service names.

An inclusive duration includes recorded downstream work. Uncovered duration subtracts the union of immediate child intervals, clipped to the parent. Overlapping children count once. The remainder can contain unrecorded children or other work; it is not CPU time or proof of a local cause. Spans enter a window by their start time. Their complete duration stays visible, with a separate count for spans crossing the window end.

The first representation repeated field names for every service/window and reached 83,517 wire bytes, above the existing conservative 79,840-byte cap. It made no model calls. A separate frozen version declares columns once and encodes each window as an ordered row, preserving every value and definition. Its largest request is 73,628 bytes. The actual run reports 4,910–26,228 input tokens, within the unchanged 32,768-token context. The byte cap is a sizing guard, not an exact token limit.

For example, TRC-62dc836e52ba adds this auth-service observation; durations are microseconds:

```json
{
  "service_columns": [
    "spans",
    "distinct_traces",
    "duration_median_us",
    "duration_p90_us",
    "uncovered_duration_median_us",
    "uncovered_duration_p90_us",
    "status_code_counts",
    "status_missing_fraction"
  ],
  "services": {
    "ts-auth-service": {
      "after": [
        2646,
        660,
        41758.5,
        231508.5,
        1788.0,
        200578.0,
        {},
        1.0
      ],
      "before": [
        1800,
        360,
        2990.0,
        199311.6,
        1837.5,
        190007.2,
        {},
        1.0
      ]
    }
  }
}
```

This excerpt shows one service; the [trace inspector](http://127.0.0.1:8769/traces?case=TRC-62dc836e52ba&arm=traces&service=ts-auth-service#input) shows the complete original request, compact trace rows and expanded observations. Inclusive median duration rises from 2.99 to 41.76 ms while uncovered median duration stays near 1.8 ms. That distinction directs attention to recorded child work; it does not establish the fault origin.

## Comparison setup

Jev 1.13.0 receives both versions in three serial rounds with balanced arm order, no retries and no warmup. The source plan and all 78 exact requests were committed before execution. The existing 0.70 probability boundary and zero margin allow at most one analyst-facing lead, otherwise withholding. No threshold search or ML refitting occurred.

The fitted Online Boutique ML and change/resource rankings remain metric-only controls. A separate transparent trace ranking uses positive relative growth in median uncovered duration, requiring at least five spans in each window. Missing observations cannot rank as healthy services. This ranking is not fitted ML and receives different information from the metric controls.

Promotion requires a repeated fix in each application, no repeated lost success, no round-level loss of first-choice accuracy or displayed correct coverage, no extra displayed errors, and some correct displayed guidance. These are descriptive research criteria, not an operational error budget.

## Results

| Application and input | First-choice matches, rounds 1 / 2 / 3 | Shown correct | Shown wrong | Withheld |
| --- | --- | --- | --- | --- |
| Train Ticket, metrics | 1 / 0 / 1 of 7 | 0 / 0 / 0 | 0 / 0 / 0 | 7 / 7 / 7 |
| Train Ticket, metrics + traces | 1 / 1 / 1 of 7 | 0 / 0 / 0 | 0 / 0 / 0 | 7 / 7 / 7 |
| Online Boutique, metrics | 3 / 3 / 4 of 6 | 3 / 3 / 3 | 0 / 0 / 0 | 3 / 3 / 3 |
| Online Boutique, metrics + traces | 3 / 3 / 4 of 6 | 3 / 3 / 3 | 0 / 0 / 0 | 3 / 3 / 3 |

Rounds repeat the same cases; they are not 39 independent incidents. Withholding every Train Ticket lead prevents displayed errors here but supplies no investigation guidance.

| Local control | Train Ticket, 7 cases | Online Boutique, 6 cases |
| --- | --- | --- |
| Frozen metric ML | 6 | 3 |
| Change ranking | 0 | 6 |
| Resource ranking | 0 | 6 |
| Uncovered-duration ranking | 2 | 0 |

These small development panels do not establish that ML is generally better. They do show that additional telemetry alone did not make this Jev setup competitive on Train Ticket code faults. The trace-only ranking also fails to identify most injected causes.

## What the failures show

TRC-62dc836e52ba is the only first-choice fix, in round two. Metrics choose admin-travel; traces choose auth. Both versions choose auth in rounds one and three, so this is not a repeated fix. Its trace-arm choice probability stays around 0.26, well below 0.70.

In TRC-88e79b2affcd, traces replace insufficient evidence with travel-service in all three rounds, while the published cause is auth-service. The choices remain below 0.70. In Online Boutique TRC-ca36c873ae96, traces shift every choice to frontend at about 0.58–0.61 despite no recorded adservice span. Neither change is useful guidance, and increased certainty about a symptom would become risky if the boundary were lowered.

The three email/F2 cases match with or without traces and provide all Online Boutique displayed guidance. Their after-window email spans number only one to four, too few for the trace ranking's minimum. Useful metric evidence can coexist with poor trace coverage; missing traces must not suppress it automatically.

The unchanged question asks Jev to compare local resource changes with latency/error symptoms. Its insufficient-evidence option still refers specifically to “metric summaries.” That wording may limit how Jev uses the added traces, but the saved choice probabilities contain no explanation that proves it did. The experiment establishes that this input addition under the existing question did not help consistently; it does not establish that all trace-aware Jev designs fail.

## Next decision

The evaluation gate failed, so the planned 132 evaluation calls did not run. All 22 evaluation cases and 25 reserve cases remain sealed. The existing display boundary stays unchanged.

I recommend a focused trace-aware question and explicit before/after trace deltas before another full-candidate comparison. The question should address all supplied telemetry and allow code faults without a large resource change. A new protocol would use untouched groups for development and preserve a separate evaluation panel. Replaying the inspected 13 cases could diagnose wording effects, but could not validate a gain.

An alternative is to strengthen the ML comparator and test Jev as an evidence check on a short candidate list. That changes Jev's task from finding a cause among every service to assessing a supplied lead, so it needs a separate comparison that measures shared errors and lost correct leads. The human decision is whether to continue Jev's full-candidate diagnosis or move to that narrower supporting role.
