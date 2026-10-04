# When Jev and ML disagree

The user selected disagreement as an analyst-review trigger. A Jev lead that passes the frozen 0.70 boundary will require review if the unchanged ML model ranks a different service first. ML will not replace Jev's answer. Agreement cannot establish correctness: both models can select the same wrong service.

The paired comparison will measure wrong leads retained, wrong leads sent to review, correct leads lost, review workload and display consistency over three rounds. The input, question, model and probability boundary will stay fixed. No threshold search or refitting is planned. Application results will remain separate; repeats are not independent incidents.

## Checking a fresh collection

The [RCAEval repository](https://github.com/phamquiluan/RCAEval) lists RE1 as a separate metric-only collection with five fault types and five repetitions of each service/fault pair. I inspected only its already downloaded case index. Its telemetry remains unopened except for the ten cases covered by the new schema-audit plan.

The audit opens all five repetitions of Train Ticket auth-service CPU and Sock Shop carts CPU. These two groups become development and cannot enter evaluation. It makes no Jev calls. Before opening the evaluation panel, a separate protocol will fix the cases, input construction, disagreement rule and call budget. The initial target is 50 cases per application, grouped and balanced across faults, with the remaining 70 per application unopened.

New recordings from familiar applications and fault types test collection transfer. They do not establish unseen-family performance, telecom readiness or analyst benefit. Public model pretraining exposure remains unknown. RE1 has fewer metric series and different sampling windows; the schema audit must establish whether the unchanged evidence pipeline can represent them without inventing measurements.
