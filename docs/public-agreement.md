# When Jev and ML disagree

The user selected disagreement as an analyst-review trigger. A Jev lead that passes the frozen 0.70 boundary will require review if the unchanged ML model ranks a different service first. ML will not replace Jev's answer. Agreement cannot establish correctness: both models can select the same wrong service.

The paired comparison will measure wrong leads retained, wrong leads sent to review, correct leads lost, review workload and display consistency over three rounds. The input, question, model and probability boundary will stay fixed. No threshold search or refitting is planned. Application results will remain separate; repeats are not independent incidents.

## Checking a fresh collection

The [RCAEval repository](https://github.com/phamquiluan/RCAEval) lists RE1 as a separate metric-only collection with five fault types and five repetitions of each service/fault pair. I inspected only its already downloaded case index. Its telemetry remains unopened except for the ten cases covered by the new schema-audit plan.

The audit opens all five repetitions of Train Ticket auth-service CPU and Sock Shop carts CPU. These two groups become development and cannot enter evaluation. It makes no Jev calls. Before opening the evaluation panel, a separate protocol will fix the cases, input construction, disagreement rule and call budget. The initial target is 50 cases per application, grouped and balanced across faults, with the remaining 70 per application unopened.

New recordings from familiar applications and fault types test collection transfer. They do not establish unseen-family performance, telecom readiness or analyst benefit. Public model pretraining exposure remains unknown. RE1 has fewer metric series and different sampling windows; the schema audit must establish whether the unchanged evidence pipeline can represent them without inventing measurements.

## Frozen comparison

The ten schema-audit cases use the existing CPU, memory, workload, error and latency-50/90 labels. Their timestamps and windows match the public index. No schema conversion is required.

The committed evaluation plan selects 50 Train Ticket and 50 Sock Shop recordings. Each application has ten service/fault groups, with all five repetitions intact and ten cases per fault type. Selection uses sorted service index minus fault index modulo five, keeping offsets one and two. The two audited groups are development only; 70 cases per application stay unopened. This allocation precedes telemetry inspection. Duplicate downloaded metric bytes, unsupported metric names, missing published candidates or timeline inconsistencies stop preparation rather than trigger case replacement.

The largest prepared request is 50,440 bytes, below the unchanged empirical request cap. Jev receives named summaries of all observed services. CPU, memory, workload, error and latency retain their source labels and units. Disk I/O and socket series absent from this collection remain unavailable; the frozen ML records feature availability instead of treating an absent series as an observed zero.

Three serial rounds permit 300 calls, with rotated case order and no retries or warmup. Exact request fingerprints must be committed before execution. HTTP, network, checkpoint or context failures stop the run; failed or missing calls keep their denominator.

The descriptive research gate requires each round to begin with an erroneous eligible Jev lead, route at least one such error to review, retain correct guidance and lower the wrong fraction among retained leads. An application with no eligible Jev errors provides no opportunity to test error reduction. The gate is a reporting criterion, not an operational error budget. A passed gate can still retain wrong leads.
