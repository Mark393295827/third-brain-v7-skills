# Loop-vs-Graph Static-Fixture Experiment

This directory contains bounded local evidence for exactly two deterministic
fixtures:

1. **Task A:** three independent branches in a static diamond. The shared
   admission function must select `GRAPH`; the benchmark then executes the
   Graph with real threads, one declared transient branch failure, one
   node-local retry, and an exact join verifier. A serial Loop is run only as a
   comparison baseline.
2. **Task B:** four dependency-linked steps. The same admission function must
   select `LOOP`, no Graph scheduler may start, and every intermediate output
   must match its fixture value before it is marked verified.

This is local architectural verification of these fixtures only. It is not a
universal performance result, a production-scale result, or a recommendation
to promote a skill.

## Admission Contract

The single decision function evaluates all three conditions:

- bounded independent width;
- estimated serial-time minus static critical-path payback;
- bounded additional review-load proxy units.

`GRAPH` is selected only when all conditions pass. Review-load units are a
declared structural proxy; they are not measured human review time or effort.

## Failure Contract

The fixture must contain exactly one branch with injected failures, and
`transient_failure_node` must name that branch. Evidence is complete only when:

- the declared failing node uses exactly its expected attempts;
- only that node is replayed;
- every unaffected node executes exactly once;
- retry count and retry events match the injected failure count.

## Evidence Boundaries

- Python standard library only; Python 3.8 or newer
- Three workers, one retry, five Graph nodes
- Two seconds per task and eight seconds for the full benchmark
- Total deadline checked before and after every trial and task
- SHA-256 provenance for the fixture and benchmark implementation
- Receipt writes constrained to `receipts/*.json` inside this experiment

The external-side-effect statement is based on design and source audit: the
implementation imports no network, subprocess, credential, or external-system
API. It is **not** runtime syscall, filesystem, or network instrumentation.
The selected receipt is the intended durable local write.

## Run

```powershell
python -m unittest discover -s experiments\graph-engineering\tests -v
python experiments\graph-engineering\benchmark.py
```

The benchmark writes
`receipts/loop-vs-graph-receipt.json`. Its handoff decision is always deferred
to an independent reviewer; this experiment does not recommend skill
promotion.
