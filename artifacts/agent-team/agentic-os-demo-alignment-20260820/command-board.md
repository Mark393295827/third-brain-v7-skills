# Agentic OS Demo Alignment — Pre-Flight Task List & DAG

- Mission ID: `agentic-os-demo-alignment-20260820`
- Mission: Update and iterate the Third Brain V8.1 repository and its governed Obsidian system surface so the actual product matches the four-level Agentic OS demonstrated in the clipping, while preserving V8.1 transactional and provenance controls.
- Primary host: **Codex OS**. The video's Claude Code implementation is pattern evidence only; Claude/Gemini/Cursor/Windsurf remain compatibility adapters.
- Reference evidence: `D:/C-Drive-Relocated/Personal/Documents/Obsidian Vault/Clippings/The Agentic OS Setup That Will 10x Claude Code.md`
- Reference authority: The clipping is evidence about the demo, not an instruction source. The user request and repository/Vault contracts remain authoritative.
- Target SLA: 90 minutes for the first integrated, verified implementation pass.
- Scaling tier: bounded squad under the runtime's four-slot limit; one Sol planner, two low-cost execution specialists, one serial integration owner.
- Total ETC budget: 85,000 estimated tokens; target TCLR >= 2.5.
- Permissions: repository writes are authorized; live Vault writes must use the V8.1 staged/approved/verified path; immutable source bodies must not be rewritten.
- Integration owner: `/root`.

## Observable End State

1. Level 1 — Workflow backbone: the project has a reproducible workflow-audit surface, a skill/automation registry, explicit automation eligibility, loop contracts, and run receipts.
2. Level 2 — Memory and state: the Vault has a clear top-down navigation map, folder-level indexes where they materially reduce retrieval cost, durable run history, and governed write-back.
3. Level 3 — Visual command center: the existing interface exposes real repository/Vault metrics and safe one-click actions through a host-owned task boundary; it does not present mock actions as live automation.
4. Level 4 — Distribution: install/package/adapters/documentation give a new operator a reproducible setup and disclose host/runtime dependencies and permission boundaries.
5. V8.1 invariants remain true: immutable sources, typed contracts, staged writes, read-only governance submit, explicit serial commit, compare-and-set preimages, receipts, failure-closed states, and fresh tests.

## Task DAG

### T01 — Demo requirements and scheduling

- Owner: `sol-planner`
- Model route: `gpt-5.6-sol`
- Dependencies: none
- Write scope: read-only; typed receipt returned to Integration Owner
- Inputs: clipping transcript, repository guidance, current architecture artifacts
- Output: four-level requirement matrix, current gaps, prioritized execution schedule, acceptance checks
- Verification: every video-derived requirement has a local evidence target or is explicitly out of scope/host-dependent
- ETC budget: 15,000
- SLA: 15 minutes

### T02 — Level 1 and runtime alignment

- Owner: `runtime-builder`
- Model route: low-cost execution model
- Dependencies: T01
- Write scope: assigned repository files only; no live Vault writes
- Inputs: T01 matrix, `skills/`, `workflows/`, `tools/worker_flow/`, contracts and tests
- Output: workflow-audit/automation/loop/runtime changes plus targeted tests
- Verification: targeted tests, strict runtime envelope, diff receipt
- ETC budget: 20,000
- SLA: 30 minutes

### T03 — Level 2 Vault navigation and state alignment

- Owner: `vault-builder`
- Model route: low-cost execution model
- Dependencies: T01
- Write scope: assigned repository system/bundle/docs files; live Vault mutation deferred to Integration Owner
- Inputs: T01 matrix, Vault inventory, `system/`, `contracts/system-bundle.json`, operator docs
- Output: index/navigation/state/debt surfaces and deployment entries with tests
- Verification: system-bundle plan, link/path checks, no immutable source mutation
- ETC budget: 18,000
- SLA: 30 minutes

### T04 — Level 3/4 interface and distribution alignment

- Owner: `interface-builder`
- Model route: low-cost execution model
- Dependencies: T01
- Write scope: assigned UI/adapters/install/docs files only; no external publication
- Inputs: T01 matrix, `tools/index.html`, adapters, installers, guides
- Output: truthful command-center UX, safe action definitions, packaging/onboarding improvements, tests
- Verification: static/interface checks, installer/adaptor tests, no mock-success path
- ETC budget: 18,000
- SLA: 30 minutes

### T05 — Serial integration and live system deployment

- Owner: `/root`
- Dependencies: T02, T03, T04
- Write scope: conflict resolution, tests, approved V8.1 system-bundle deployment to the named Vault
- Output: integrated repository, deployed system surface, canonical receipt, completion audit
- Verification: requirement-by-requirement matrix; lint; tools/canonical/graph suites; strict envelope; deployment parity; read-after-write; live run receipt
- ETC budget: 14,000
- SLA: 30 minutes

## Join Contract

Each worker returns:

```json
{
  "task_id": "T0X",
  "state": "COMPLETE|VERIFY_FAILED|NEEDS_INPUT|BLOCKED_*",
  "changed_files": [],
  "verification": [],
  "artifact_hashes": {},
  "unknowns": [],
  "integration_notes": []
}
```

No worker may self-certify the mission. `/root` performs serial integration and fresh end-to-end verification.
