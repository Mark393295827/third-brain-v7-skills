---
name: harness-engineering
description: Design V6 runtime infrastructure around AI agents — permissions, tools, MCP/Skills/Hooks, feedback loops, observability, scheduled routines, Agentic OS four-C packaging, closed-loop organization trace governance, custom evals, von Neumann-style runtime architecture, and governance. Use when deploying agents to production, designing multi-agent systems, building agent harnesses, or turning Obsidian wiki rules into bounded runtime controls.
version: "6.3"
updated: "2026-07-02"
assumes: "The agent workflow will use tools, permissions, logs, or production-like reliability boundaries."
conflicts_with: "Do not relax approval, sandbox, or observability constraints introduced by agentic-engineering or agent-teams-command."
---

# Harness Engineering

Design the system *around* AI agents for reliable, safe production use.

Harness Engineering protects the quality ceiling of Agentic Engineering. It turns fast agent output into controlled execution through permissions, observability, recovery, and adversarial validation.

## Agent Runtime Model

Treat the agent harness as the kernel around an LLM OS:

| Kernel concern | Agent harness responsibility |
|---|---|
| Memory management | Curate context, summarize bulky outputs, persist state to wiki/logs. |
| Syscall boundary | Expose tools with contracts, allowlists, deny rules, and retries. |
| Process isolation | Separate write scopes, sandboxes, credentials, and state per agent. |
| Scheduling | Decide sequential, parallel, or event-driven execution. |
| Interrupts | Stop, ask approval, rollback, or route to a safer action. |
| Observability | Log tool calls, decisions, outputs, costs, and verification evidence. |
| Garbage collection | Close idle agents, remove stale tasks, compact context, and record risks. |

## Von Neumann Harness Frame

Use this frame to turn an agent workflow into an inspectable runtime. The value is not the metaphor; the value is forcing every delegated action to name its program, memory, control path, tools, disk, verifier, and recovery boundary.

| Runtime part | Harness responsibility |
|---|---|
| Stored program | Skills, prompts, SOPs, routines, and command boards are executable instructions with versions and owners. |
| Processor / control unit | One auditable scheduler decides the next action, interrupt, rollback, or escalation. |
| RAM | Context is hot working memory; load only task-local state and prune stale context. |
| Disk | Wiki, logs, state files, sessions, traces, and receipts hold durable memory outside chat. |
| Bus | Tool calls, event streams, task lists, and handoff schemas move state between components. |
| I/O devices | MCP servers, shell commands, browsers, APIs, filesystems, and external connectors are system calls. |
| Verifier | Tests, lint, evals, receipts, telemetry, reviewers, or red teams check state transitions. |
| Garbage collector | Cleanup idle agents, stale tasks, outdated context, obsolete rules, and unreconciled artifacts. |

Serial-control rule: keep high-risk intent, permission escalation, and final join decisions on one inspectable control path. Parallelize only owned workstreams whose memory, bus, tools, and verifier are already defined.

Automata rule: local rules create global behavior. For each routine, hook, or agent worker, define `state + trigger -> action -> evidence -> next state | stop | escalate`.

Self-reproduction rule: an agent may propose new skills, hooks, schemas, or automations, but installation requires the V6 promotion gate, provenance, human approval when required, and a cheap objective check.

## Productized Agent Harness

Google I/O '26 added a practical pressure test for harness design: the same runtime pattern now appears in developer tools, personal agents, search, commerce, generative media, and smart glasses.

| Product surface | Harness control that must exist |
|---|---|
| Agent-first IDE | task queue, subagent ownership, hooks, sandbox, test proof |
| Personal agent | user mandate, memory scope, tool allowlist, resumable log |
| Agentic search | source provenance, comparison criteria, action preview |
| Agentic commerce | budget, merchant/payment boundary, mandate, receipt trail |
| Generative media | prompt/edit history, watermark/disclosure, content credentials |
| Ambient eyewear/device | sensor consent, privacy mode, physical-world fallback |

If a harness cannot produce an audit trail for what the agent saw, decided, called, changed, and verified, the agent is not ready for delegated action.

## Agentic OS Four-C Runtime Gate

Use this before wrapping a workflow in a dashboard, button, voice command, routine, or headless execution:

| C | Harness check |
|---|---|
| Context | Source-of-truth files, wiki pages, state, logs, and retrieval path are explicit. |
| Connections | Accounts, APIs, MCP servers, repos, vaults, and credentials are scoped by risk. |
| Capabilities | Skills, SOPs, scripts, templates, and evals define the action, not a vague prompt. |
| Cadence | Schedule, event, queue threshold, receipt, anomaly alert, and stop rule are defined. |

Most value should exist before the UI: codified capabilities plus durable state. A headless command or button is not safe automation unless it has the same mandate, context, verifier, receipt, and rollback path as a CLI run.

## Closed-Loop Organization Gate

Use this when a harness reads broad company traces such as code, chats, meetings, tickets, docs, sales calls, or support logs. Closed-loop does not mean full access by default. Define:

```text
Trace sources:
Owner / DRI:
Allowed reads:
Denied reads:
Retention and redaction:
Decision or action the trace may influence:
Custom eval or grader:
Human review boundary:
Feedback-to-skill path:
```

Do not turn workplace surveillance into a harness. Prefer least-privilege trace slices, explicit owners, audit logs, and reviewable recommendations before autonomous action.

## Managed Agent Runtime Model

For production-like agents, separate the runtime into three resources:

| Resource | Defines | Harness questions |
|---|---|---|
| Agent | Model, persona, system prompt, skills, MCP/tools | Is the role narrow enough? Are capabilities necessary? |
| Environment | Execution space, container, network, credentials, filesystem | What can the agent reach? What is allowlisted or denied? |
| Session | Agent instance, mounted context, event stream, durable state | How is state resumed, deleted, audited, and recovered? |

The session event log is the backbone of reliability. It should capture user messages, tool calls, tool results, agent responses, verification evidence, errors, and recovery actions. A response without an inspectable event trail is not enough for delegated production work.

## Permission Bike Method

Escalate autonomy by proven reliability, not by confidence in a prompt:

| Stage | Allowed capability | Required proof |
|---|---|---|
| Observe | Read, search, summarize, recommend | Sources and assumptions are inspectable. |
| Co-drive | Draft, simulate, prepare changes | Human approves every external action. |
| Training wheels | Execute low-risk scoped actions | Logs, rollback, and post-action checks pass. |
| Supervised autonomy | Run reversible routines | Alerts, receipts, and anomaly review exist. |
| Autonomy | Run high-frequency low-risk loops | Periodic permission audit and failure review. |

Do not give a tool key and rely on text instructions to prevent misuse. The real boundary is the key, endpoint, account, filesystem, network, budget, and approval path.

## Usage Template

**Prompt**
```text
Use harness-engineering for this agent workflow. Design permissions, tools, feedback loops, observability, and failure handling.
```

**Use Case**
- Moving an agent workflow from ad hoc prompting toward a reliable runtime architecture.

**Expected Result**
- The agent produces a harness design with permission tiers, tool boundaries, logs, evals, and recovery paths.

**Output Example**
- A runtime spec with permission matrix, tool allowlist, approval gates, logs, evals, and incident response.

**Verification Case**
- The design names what the agent can do automatically, what needs approval, and what is denied.

**Verified Effect**
- An ad hoc agent workflow becomes a controlled runtime with explicit permissions, observability, and failure handling.

## Success Metrics

- Design specifies permissions, tool contracts, observability, failure handling, and recovery path.
- High-risk actions have approval or sandbox boundaries.
- Verification evidence is defined before deployment or automation.
- Harness design separates context-hot-path rules from cold-path reports, dashboards, backlogs, and wiki maps.
- Runtime design maps stored program, control path, memory, disk, bus, I/O tools, verifier, and garbage collection before delegated execution.
- Agentic OS packaging passes the four-C gate before headless, scheduled, or button-driven execution.
- Broad organizational trace access has owner, retention, redaction, audit, custom eval, and human review boundaries.

## When to Use

- Deploying agents to production
- Setting up permissions/guardrails/approval workflows
- Designing multi-agent systems
- Agent behaved unpredictably → needs better constraints
- Configuring auto-mode or permission tiers

---

## Three Domains

| Domain | Object | Maturity |
|--------|--------|----------|
| **Physical** | Wire harnesses (automotive/aerospace) | ⭐ Mature |
| **Software** | CI/CD pipelines (Harness.io) | ⭐ Mature |
| **Cognitive** ⭐ | AI Agents | 🌱 Emerging |

---

## Six Components

### 1. Context & Knowledge Layer
- Curated access to code, docs, schemas, logs
- Use `CLAUDE.md` for project-level context
- Use `context-manager` for token budgeting
- Never inject raw 10K+ token files
- Persist reusable outputs to wiki, docs, logs, or state files; chat history is not durable memory

### 2. Tooling & API Surface
**Three-Tier Permission Model:**

| Tier | Scope | Mechanism | Examples |
|:----:|-------|-----------|----------|
| **1** | Safe tools | Always allowed | Read, search, grep, glob |
| **2** | In-project | Auto-approve (git reviewable) | Write/edit in project dir |
| **3** | High-risk | Classifier/human approval | Shell, API calls, deletes |

**Tier 3 heuristic:**
```
1. Can destroy data irreversibly? → BLOCK
2. Accesses credentials? → BLOCK
3. Affects shared infrastructure? → BLOCK
4. Target inferred (not explicit)? → BLOCK
```

**Delegated action gate:**

Before any tool call that buys, publishes, schedules, messages, edits shared state, or acts through a user's account, require:

```text
Mandate: what the user explicitly authorized
Scope: allowed accounts, surfaces, vendors, files, or domains
Limit: budget, time, rate, data, or blast radius cap
Preview: what the user can inspect before execution
Receipt: durable audit record after execution
Rollback: how to undo or compensate if wrong
```

### 3. Architectural Constraints
- Linters, structural tests
- File/directory access boundaries
- Token budget: never exceed 80% context window

### 4. Feedback & Validation Loops
- Write-Test-Fix cycle
- **Generator + Evaluator pattern** (GAN-inspired)
- Deny-and-continue: try safer alternative on block
- Escalate to human after 3 consecutive blocks
- For high-risk work: Builder -> Evaluator -> Red Team -> Fixer -> final proof

### 5. Observability & Governance
- Log every tool call + result
- Metrics: success rate, revert rate, token usage
- Cost tracking per session
- Evidence ledger: verification command, source link, screenshot, test result, or diff for each completion claim
- Provenance ledger for generated media, search summaries, and commerce decisions: source, prompt/edit trail, model/tool used, and user confirmation point

### 6. Maintenance
- Periodic agents: dead code, outdated docs, architectural drift
- Wiki lint for broken links/missing frontmatter
- Context garbage collection: summarize completed work, close idle processes, and record residual risk

---

## GAN-Inspired Multi-Agent Pattern

> "Tuning a standalone evaluator to be skeptical is far more tractable than making a generator critical of its own work."

```
Generator ←──sprint contract──→ Evaluator
    │                              │
    ▼                              ▼
 Produces output              Playwright/Test
```

**Implementation:**
1. **Planner** → 1-sentence prompt → full spec
2. **Generator** → builds in sprints
3. **Evaluator** → tests, files bugs
4. Feedback loop → 5-15 iterations

---

## Physical → Cognitive Analogies

| Physical | AI Agent | Implementation |
|----------|----------|----------------|
| Zonal Architecture | Permission scopes | `AGENTS.md` domain restrictions |
| IP68 Protection | Security isolation | Sandbox, token in vault |
| HiPot Test | Stress testing | Edge-case test suite |
| Continuity Test | Tool verification | `describe-tools` pre-flight |
| EMC/Interference | Multi-agent isolation | Separate sandbox per agent |

---

## Multi-Agent Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Supervisor** | Orchestrator delegates to sub-agents | Complex tasks with sub-steps |
| **Peer Review** | Agents review each other | High-risk changes |
| **Competitive** | Multiple agents try same task | Creative work, optimization |
| **Pipeline** | Sequential chain | Document processing |
| **Zonal** | Domain-based routing | Enterprise systems |
| **Closed-Loop** | Output feedback shapes input | Continuous improvement |

---

## Permissioned Tool Design

Define every tool like a system call:

| Field | Required question |
|---|---|
| Purpose | What state can this tool read or change? |
| Inputs | Which arguments must be explicit, not inferred? |
| Bounds | Which paths, domains, records, or resources are allowed? |
| Failure mode | What is the safe fallback when it fails or is denied? |
| Evidence | What output proves it succeeded? |
| Audit | Where is the call logged? |

Prefer narrow tools with explicit inputs over broad shell/API access. If broad access is unavoidable, wrap it with approval gates and post-action verification.

## V6 Extension Primitive Selector

Choose the lowest-context primitive that can do the job:

| Primitive | Use for | Avoid when |
|---|---|---|
| Skill | Reusable procedure, local convention, task policy, source-to-output workflow | Deterministic check can run outside context |
| Hook | LSP/lint/test/secret scan, tool-call guard, CI or PR signal, post-action receipt | The result needs human judgment or broad context |
| MCP / Connector | Public or cross-product integration, external API, authenticated system access | A local file/script or narrow hook is enough |
| Dynamic workflow | Many independent shards with script review, cost cap, and observable workers | Roles need frequent IPC or shared judgment |
| Agent team | Distinct roles, ownership, critique, integration, or debate | One thin loop plus test can solve it |

Default to zero-overhead context: do not inject a tool, rule, report, or map into the prompt unless the current task uses it.

## V6 Trigger-Context-Steering Harness

For scheduled routines and proactive agents, define:

```text
Trigger: schedule, event, webhook, human request, or queue threshold
Context: exact files, tools, credentials, memory, and wiki pages visible to the agent
Steering: live observation, approval gate, verifier, rollback, anomaly alert
Receipt: durable log, diff, dashboard, daily note, or external system status
```

No routine should run indefinitely. Every routine needs a hard budget, stop condition, stale-context half-life review, and recovery path.

---

## Security-Aware Integration

Before shipping high-risk agent output, run an adversarial review:

| Risk area | Minimum adversarial check |
|---|---|
| Auth, permissions, secrets | Attempt privilege escalation and secret exposure paths. |
| Data mutation or deletion | Verify backups, rollback, idempotency, and explicit target bounds. |
| Public claims or launch copy | Check evidence, source quality, and unsupported promises. |
| External API actions | Confirm rate limits, credentials, audit logs, and retry safety. |
| Commerce or delegated account actions | Verify mandate, budget, merchant/payment boundary, receipt trail, and rollback path. |
| Generated media or public content | Verify provenance, disclosure/watermark path, and unsupported claim risk. |
| Multi-agent integration | Check ownership conflicts, stale assumptions, and unverified joins. |

Use simulated hostile agents, security tests, or a skeptical evaluator before release. Do not let the same builder be the only judge of safety.

---

## Closed-Loop System (Aladdin)

```
Data Lake → Risk Engine → Optimizer → Stress Test → OMS → Compliance → Feedback Loop
     ↑                                                              ↓
     └──────────────────── 反馈闭环 ────────────────────────────────┘
```

| Aladdin Module | Agent Harness |
|----------------|---------------|
| Data Lake | Session log, knowledge base |
| Risk Engine | Risk assessment, threat detection |
| Optimizer | Task decomposition, resource allocation |
| Stress Test | Edge-case testing, failure simulation |
| OMS | Order execution, tool calls |
| Compliance | Guardrails, policy enforcement |
| Feedback Loop | Results → learning → improvement |

**Key:** Closed loop is the moat — not any single component. MECE principle applies.

---

## Quality Gates

- [ ] Each agent has defined permission scope
- [ ] Agent, Environment, and Session responsibilities are separated
- [ ] Three-tier permission model documented
- [ ] Permission escalation follows observe -> co-drive -> scoped action -> monitored autonomy
- [ ] Write-Test-Fix feedback loop in place
- [ ] Tool calls logged and observable
- [ ] Token costs tracked per session
- [ ] Delegated actions have mandate, scope, limit, preview, receipt, and rollback
- [ ] Generated media and public claims have provenance or disclosure path
- [ ] High-risk actions require approval
- [ ] Multi-agent isolation prevents interference
- [ ] Generator and Evaluator separate for complex tasks
- [ ] High-risk outputs receive adversarial or red-team review
- [ ] Reusable outputs have durable write-back outside chat history
- [ ] Tool contracts include bounds, failure path, evidence, and audit trail
- [ ] V6 extension primitive selected with MCP/Skills/Hooks/workflow/team tradeoff and zero-overhead context checked
- [ ] Scheduled or proactive harness has Trigger, Context, Steering, Receipt, budget, stop condition, and recovery path
- [ ] Agentic OS four-C gate defines Context, Connections, Capabilities, and Cadence before UI or headless packaging
- [ ] Closed-loop organization trace access is least-privilege, owned, auditable, redacted, and tied to a specific eval or decision
- [ ] Von Neumann runtime frame names stored program, control path, RAM, disk, bus, I/O tools, verifier, and garbage collector
- [ ] High-risk decisions stay on an auditable serial control path; only owned/verifiable workstreams run in parallel
- [ ] Self-improving skills, hooks, schemas, and automations pass the V6 promotion gate before installation
