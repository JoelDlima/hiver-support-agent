# 004 — Agent Framework Decision (Hiver AppleSupport)

Date: 2026-09-10 | Owner: Swarm B | Status: FINAL v1
Base: `research/agents/orchestration.md` (10 topics, Sep 2026) + `research/competitors/analysis.md`

## Context
Pipeline is 6 fixed stages: validate → classify → retrieve → draft → escalate → validate.
No planning, no tool-choice, no multi-turn delegation. Requirements: reliable, testable,
cheap, auditable support replies with SLA-bounded latency.

## Candidates
Plain Python + Pydantic v2 + sklearn (deterministic workflow) | LangChain/LangGraph 1.x |
LlamaIndex Workflows | PydanticAI v2 | OpenAI Agents SDK | CrewAI | Microsoft Agent
Framework 1.0 | Google ADK 2.0 | DSPy (serving) | MCP agent runtime

## Evidence (VERIFIED vs ESTIMATE)
- VERIFIED (Sep 2026 versions): LangChain/LangGraph joint v1.0 GA Oct 2025
  (core ~1.4.x / graph ~1.2.6, AgentExecutor EOL Dec 2026); LlamaIndex core v0.14.24 +
  workflows v2.23.3 standalone; PydanticAI v2.0 Jun 2026; OpenAI Agents SDK v0.22.0
  (pre-1.0, breaking changes allowed); CrewAI v1.15.x; MAF 1.0 GA Apr 2026;
  ADK 2.0 (breaking from 1.x); DSPy v3.3.x; MCP spec 2026-07-28 (stateless core).
  Source: orchestration.md §3 (release blogs + repos, Aug 2026 comparisons).
- VERIFIED (vendor consensus, still canonical Sep 2026): Anthropic "Building Effective
  Agents" (Dec 2024) + OpenAI Agents-vs-Responses guidance + Google ADK 2.0 ("separate
  execution routing from language processing") converge: start with simplest
  deterministic workflow; add agency only when step count/order cannot be predetermined.
  Hiver's path IS predetermined — a workflow, not an agent problem.
- ESTIMATE (failure math): 10-step agent at 95%/step ≈ 60% E2E (0.95¹⁰); cheapest
  3-agent CrewAI-style run ≈ $0.10–0.20 vs deterministic ≈ $0 marginal + 1 bounded LLM
  call — 10–50× costlier with worse variance.
- VERIFIED (competitor pattern): `adityanaranje/Langgraph-Customer-Support-Multi-Agent`
  guardrail graph (grounding + confidence + escalation) is the right *pattern* — we
  instantiate it as pure functions (~200 lines) without the LangGraph runtime.

## Decision
**NO agent framework. Plain Python + Pydantic v2 contracts + sklearn, one optional
isolated LLM call for drafting behind `DraftReply` schema + ≤2 retries + fallback.
Copy PydanticAI's validation-sandwich discipline (30-line reimplementation), cite
ADK 2.0 as vendor validation of workflow-over-agent — without importing any runtime.**

## Rejected — why
- LangGraph: durable graphs/HITL/multi-agent handoffs solve long-running stateful agents
  (Klarna/Uber/Replit) — Hiver has no cycles, no resume-after-days, no handoffs.
  Heaviest abstraction + LangSmith coupling for zero needed feature.
- LlamaIndex Workflows: closest lightweight alt (typed events, tiny deps) — still an
  event mesh + server Hiver doesn't invoke. First reconsideration candidate IF routing
  ever grows (routing subgraph only).
- PydanticAI: best-typed agent option — still a loop + harness + provider matrix unused.
  Adopt pattern, not runtime.
- OpenAI Agents SDK: pre-1.0 churn + provider-centering conflicts with offline-testable
  neutrality. Reject.
- CrewAI: role metaphor harms fixed-pipeline mental model; token chatter dwarfs budget.
- MAF: .NET/Azure/Foundry play; fresh 1.0 with preview churn. Revisit iff Hiver
  standardizes on Azure/Foundry.
- ADK: adopting it to express "call sklearn, then one LLM call" is pure overhead + GCP
  coupling. Endorse thesis, reject runtime.
- DSPy as serving runtime: premature (no train/eval harness yet) + LM-call-heavy compile
  loop. Revisit OFFLINE for prompt-tuning (GEPA/MIPROv2) if draft quality lags.
- MCP runtime: no external tool federation (2–4 tools max future) — use as protocol later,
  not a runtime now.

## Cost / complexity / failure / scale
- Cost: $0 marginal (sklearn + retrieval) + ≤1 LLM call/ticket vs N×LLM + tool
  round-trips unbounded without caps.
- Complexity: every stage pure + typed + pytest-testable; no trace replay, sandbox, or
  checkpoint store. Deps: pydantic>=2, sklearn, numpy (+ httpx/openai only in draft fn).
- Failure: compounding-error eliminated by construction; escalation is rules+confidence
  (never model self-delegation); output validation is Pydantic (never self-grading).
- Scale: add branches as `if` statements, not agents. Revisit ALL-of: (a) unpredictable
  step order at runtime, (b) single-call+workflow provably fails evals, (c) per-step
  ground truth exists, (d) team accepts sandboxing + caps + budgets.
