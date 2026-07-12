# Property Control Model

Load this reference when producing ontology, dashboards, agent roles, or state transitions.

## Default MVP

1. Work-order classification.
2. Worker dispatch recommendation.
3. Quote draft.
4. Evidence upload and audit.
5. Quality dashboard.

## Quality Domains

| Domain | Core controls | Example CTQs |
|---|---|---|
| Customer | response, experience, acceptance | first response, satisfaction, complaint rate |
| Work order | classification, dispatch, completion | first-time fix, rework, timeout |
| Worker | skill, location, reliability, capacity | on-time, completion, score |
| Quote | accuracy, margin, approval | error rate, gross margin, close rate |
| Process | end-to-end flow | cycle, wait, bottleneck time |
| Data | completeness, accuracy, traceability | missing fields/photos/location |
| Knowledge | SOP, rules, lessons | SOP hit, rule updates, reviews |

Thresholds require a baseline: green acceptable, yellow watch, red root-cause review.

## Minimum Ontology

| Object | Required fields |
|---|---|
| Customer | id, contact, address, priority, consent flags |
| Property | id, address, unit, access rules, manager |
| Asset | id, property, type, model, location, history |
| WorkOrder | id, customer, property, type, priority, SLA, status, description, evidence_required |
| Worker | id, skills, service area, location, availability, rating, capacity |
| Quote | id, work_order, labor, materials, travel, margin, approval_status |
| Evidence | id, work_order, media, signature, location, timestamps, checklist |
| Rule | id, trigger, condition, action, owner, version |
| Review | id, work_order, issue, root_cause, countermeasure, owner, due_date |

Environmental testing may add TestResult (pollutant, device, value, unit, threshold, calibration) and Device (model, calibration date, operator, status).

## Work-Order State Machine

```text
submitted -> classified -> data_needed | dispatch_recommended
dispatch_recommended -> quote_drafted -> quote_approved
quote_approved -> assigned -> in_progress -> evidence_uploaded
evidence_uploaded -> quality_review -> customer_acceptance -> closed
```

Exception states: `waiting_customer`, `waiting_material`, `worker_rejected`, `quote_rejected`, `rework_required`, `cancelled`, `escalated`.

No agent may skip a required transition or close a case without acceptance evidence.

## Agent Boundaries

| Role | Output | Human gate |
|---|---|---|
| Define | SLA, CTQ, work type | New service standard |
| Measure | Metric and missing-data report | Metric definition change |
| Analyze | Root-cause candidate | Cause acceptance |
| Improve | Rule/SOP experiment | Policy/pricing change |
| Control | Alerts and exception report | Exception closure |
| Dispatch | Ranked worker recommendation | Risk/low confidence |
| Quote | Draft and margin calculation | Customer-facing quote |
| Review | Evidence and abnormality decision | Closure/discipline |

## Dashboards

- Business: orders, completions, revenue, margin, satisfaction, alerts.
- Process: response, dispatch, completion, overdue, rework, waiting.
- Quality: classification, dispatch, quote, evidence, SOP, complaints.
- Worker: location, active/completed, on-time, score, empty-run.

Every widget must trace to an ontology field and metric definition.
