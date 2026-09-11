# Orchestration Decision for Hiver — No Agent Framework (Deterministic Pipeline + Pydantic)

**Agent:** AGENT 5 — Agent/Orchestration Research
**Date:** 2026-09-10 (UTC)
**Scope:** Hiver pipeline: `validate input → classify intent → retrieve exemplars → draft reply → escalate decision → validate output`
**Decision:** **NO agent framework. Use plain Python + Pydantic (v2) + scikit-learn, with optional single isolated LLM call for reply drafting only.**
**Status:** Final for current scope; revisit only if criteria in §9 are met.

---

## 1. Executive summary

Hiver's 3 well-scoped LLM-adjacent tasks (intent classification, exemplar retrieval, reply drafting) do **not** need autonomous agents or a multi-agent orchestration framework.

- Deterministic pipeline with **typed Pydantic outputs** is more reliable, testable, cheaper, and auditable.
- Agent frameworks (LangChain/LangGraph, LlamaIndex Workflows, PydanticAI, OpenAI Agents SDK, CrewAI, Microsoft Agent Framework, Google ADK, DSPy) add latency, cost, non-determinism, and failure modes (compounding error, runaway loops, tool-selection drift) without benefit when the control flow is known in advance.
- Industry consensus (Anthropic "Building Effective Agents" Dec 2024, still canonical Sep 2026; OpenAI Agents vs Responses guidance; Google ADK 2.0 workflows) converges on the same rule: **start with the simplest deterministic workflow; add agency only when step count/order cannot be predetermined**.
- Hiver's path *is* predetermined: 6 fixed stages, 3 bounded model/ML calls, explicit escalation gate. That is a workflow, not an agent problem.
- MCP (spec `2026-07-28`, stateless core) and provider structured-outputs are useful as *protocols/schemas*, not as reasons to adopt an agent runtime.
- Recommendation is dependency-light: stdlib + `pydantic>=2`, `scikit-learn`, `numpy`; one optional `instructor`-style or `responses.parse`-style LLM call behind a Pydantic contract + retry cap (max 2) + fallback to template/escalation.

---

## 2. Does Hiver need agents? No — with reasons

### 2.1 What "agent" means here

Per Anthropic (still cited verbatim in Jun–Aug 2026 syntheses):

- **Workflow:** LLMs + tools orchestrated through **predefined code paths**. Your code picks the next step.
- **Agent:** LLM **dynamically directs its own process and tool usage**. Model picks next step, length, and tools at runtime.

Hiver is firmly the first: input validation → classifier → retriever → drafter → rules-based escalation → output validator. No step requires the model to invent a new branch, call an open-ended tool loop, or delegate to sub-agents.

### 2.2 The three tasks are closed, not open-ended

| Hiver task | Correct tool (2026 best practice) | Why not an agent |
|---|---|---|
| **Classify intent** | scikit-learn classifier (TF-IDF + LogisticRegression/LinearSVC) or single LLM classification with `Literal[...]` enum output; Pydantic-validated | Fixed label set; needs <50 ms, offline-testable, versioned. Agent loop adds 5–40× latency/cost for identical accuracy. sklearn is deterministic and cheap; see §7. |
| **Retrieve exemplars** | Deterministic retrieval (TF-IDF/BM25 or embeddings + cosine, top-k) over `data/raw/twcs.csv` + curated exemplars; no LLM reasoning needed | Ranking is a function, not a decision. Letting an agent "choose" retrieval steps introduces non-reproducible ranking and cache-busting. |
| **Draft reply** | Single bounded LLM call with JSON-schema structured output → `DraftReply` Pydantic model → validator → retry (≤2) → fallback template | One-shot generation with inspection layer. Multi-turn ReAct/agent loop cannot improve a well-prompted single call enough to justify compounding-error risk (0.95¹⁰ ≈ 0.60 success). |

Escalation (`escalate decision`) must be **rules + classifier confidence**, never model self-delegation — auditability and SLA requirement. Output validation must be **Pydantic contract**, never model self-grading.

### 2.3 Agents add failure modes without benefit

1. **Compounding error:** each autonomous turn multiplies failure probability. Hiver needs ≥95% end-to-end shape-correctness; a 10-step agent at 95%/step ≈ 60% E2E.
2. **Unbounded cost/latency:** agent token use scales with loop length; workflow token use is fixed (1–2 calls max in Hiver).
3. **Non-reproducibility:** identical ticket → different tool traces → unauditable support replies.
4. **Testing burden:** deterministic pipeline = pytest on pure functions + golden files; agent = flaky integration tests + trace inspection + sandbox.
5. **Ops overhead:** every framework below brings its own runtime, checkpoint store, version-churn, and observability lock-in (LangSmith, Logfire, AgentOps, etc.) for zero Hiver gain.

Anthropic, OpenAI, and LangChain docs all give the same ladder: single call → workflow (chain/route/parallelize/orchestrator-workers/evaluator-optimizer) → agent **only if path unknowable in advance**. Hiver never reaches rung 3. Canonical agent-justifying example is multi-file coding agents (SWE-bench) where file set is unknowable until runtime — opposite of Hiver.

---

## 3. Framework comparison (status Sep 2026)

| Framework | Version / status Sep 2026 | Core abstraction | Fit for Hiver | Verdict |
|---|---|---|---|---|
| **LangChain + LangGraph** | Joint v1.0 GA 22 Oct 2025; `langchain-core` ~1.4.x, LangGraph ~1.2.6; `AgentExecutor` deprecated (migrate by Dec 2026); ~145k / ~41k GitHub stars; LangGraph ~34.5M monthly PyPI installs, most-installed agent framework | `create_agent` (high-level) on LangGraph `StateGraph` runtime (nodes/edges, checkpointing, `interrupt()`) | Overkill. Durable graphs, HITL interrupts, multi-agent handoffs solve long-running stateful agents (Klarna, Uber, Replit). Hiver has no cycles, no resume-after-days, no handoffs. | **Reject.** Heaviest abstraction + LangSmith coupling for no needed feature. |
| **LlamaIndex (Workflows)** | Core `v0.14.24` (19 Aug 2026); `llama-index-workflows@2.23.3` standalone (deps: `pydantic` + `typing-extensions` + instrumentation only); `llama-deploy` deprecated → LlamaAgents server | Event-driven `@step` + typed events + `Context`; `FunctionAgent`/`ReActAgent`/`AgentWorkflow` on top | Closest lightweight alternative; typed state + resource injection are genuinely good. But Hiver doesn't need event mesh, streaming workflow server, or RAG coupling. | **Reject.** If orchestration ever grows, reconsider standalone `llama-index-workflows` before LangGraph — still not needed now. |
| **PydanticAI** | V2.0 stable 23 Jun 2026; harness-first `Capability` primitive; `output_type` with Tool/Native/Prompted modes; Anthropic structured-outputs GA (Apr 2026); ~19.5k stars | Typed agent loop + Pydantic validation + capabilities (memory, guardrails, MCP, durable exec via Temporal/DBOS/Prefect) | Best-typed agent option; structured-output handling is exemplary. Still an agent loop + harness + provider matrix Hiver doesn't invoke. | **Reject as runtime; adopt pattern.** Copy its output-mode + validator discipline using plain Pydantic, without importing the loop. |
| **OpenAI Agents SDK** | `v0.22.0` (19 Aug 2026); `0.y.z` semver (still pre-1.0, breaking changes allowed); Apr 2026 harness + sandbox execution + MCP + Manifest; Python-first, TS lags | `Agent` + `Runner` + handoffs + guardrails + sessions/tracing; provider-agnostic (Responses API default) | Built for bounded conversational/transactional multi-agent workflows with approvals. Hiver is not conversational-autonomous and must stay provider-neutral + offline-testable. Pre-1.0 churn risk. | **Reject.** |
| **CrewAI** | `v1.15.x` (Jun–Aug 2026); ~58k stars; standalone (no LangChain dep); Crews (role-playing agents) + Flows (event control) | Role-based `Agent`/`Task`/`Crew`; enterprise AMP runtime (450M+ runs/mo claimed, 65% Fortune 500 claim) | Fastest prototype for role-play demos; weakest production control/observability unless buying AMP. Token chatter ($0.10–0.20 per 3-agent run) dwarfs Hiver per-ticket budget. | **Reject.** Role metaphor actively harms Hiver's fixed pipeline mental model. |
| **Microsoft Agent Framework (MAF)** | **1.0 GA 3 Apr 2026** (.NET + Python); unifies AutoGen + Semantic Kernel (AutoGen now maintenance); BUILD 2026 harness, hosted agents, CodeAct; A2A + MCP interop | `Agent`/`ChatClientAgent` + middleware + workflows + Foundry connectors | Enterprise .NET/Azure/Foundry play. Hiver is Python + sklearn + provider-neutral; no Foundry, no A2A federation needed. Fresh 1.0, preview APIs still churning. | **Reject.** Revisit only if Hiver standardizes on Azure/Foundry. |
| **Google ADK** | **2.0** (Python Mar 2026, Go Jun 2026; py breaking changes from 1.x); ~21k stars; Python/TS/Go/Java/Kotlin; `adk.dev`; graph-based Workflows + HITL + Agent Runtime deploy | Agents + **Workflows** (deterministic steps + LLM nodes separated); deploy-anywhere (Cloud Run/GKE/Agent Engine) | ADK 2.0 *agrees with this report*: blend deterministic code with isolated LLM nodes. But adopting ADK to express "call sklearn, then one LLM call" is pure overhead + GCP coupling. | **Reject runtime; endorse thesis.** Cite ADK 2.0 as vendor validation of workflow-over-agent. |
| **DSPy** | `v3.3.x` (2026); Stanford NLP; Signatures + `GEPA`/`MIPROv2` optimizers; ReActV2 experimental; `dspy.LM`, `ChainOfThought`, `BestOfN` | Declarative programs compiled/optimized against a metric (prompt search, few-shot bootstrapping) | Powerful when prompt quality is the bottleneck and labeled trainset + metric exist (Shopify 75× cheaper anecdote). Hiver has no train/eval harness yet; premature optimization. Adds LM-call-heavy compile loop. | **Reject now; revisit for prompt-tuning phase.** If draft quality lags, use DSPy/GEPA *offline* to optimize the single draft prompt, not as serving runtime. |
| **Plain Python + Pydantic + sklearn (recommended)** | Pydantic v2 (~2.11.x); sklearn 1.x; Python 3.10–3.12 (Hiver `.venv` is 3.12) | Functions + `BaseModel` contracts + `Pipeline(TfidfVectorizer, LogisticRegression)` + one optional LLM call | Zero agent runtime; every stage pure, typed, unit-testable; minimal deps already in/near Hiver venv (numpy, scipy, sklearn-family). | **Adopt.** |

Sources: LangChain/LangGraph v1.0 blog + release-policy docs + Aug 2026 comparisons; PydanticAI v2.0 release + changelog + structured-output docs; OpenAI Agents SDK repo/releases + Apr 2026 harness announcement; CrewAI README/PyPI + Jun 2026 review; MAF 1.0 + BUILD 2026 + harness blogs; ADK site + ADK 2.0 blogs + `adk-python` releases; DSPy site + `stanfordnlp/dspy` releases; Anthropic "Building Effective Agents" + Jun 2026 agents-vs-workflows syntheses; MCP spec `2026-07-28` + roadmap blogs; structured-outputs validation guides (2026).

---

## 4. Deterministic workflow vs agents — debate summary (2026)

- **Anthropic (canonical):** "Most successful implementations use simple, composable patterns rather than complex frameworks." Find simplest solution; workflows for predictable tasks; agents only for open-ended, unpredictable-step problems with verifiable feedback. Frameworks help start fast — "don't hesitate to reduce abstraction layers and build with basic components as you move to production."
- **OpenAI (Agents SDK vs Responses API):** Use Responses API (own the loop) unless SDK-managed turns/handoffs/guardrails/sessions are needed. "Otherwise, a deterministic solution may suffice."
- **Google (ADK 2.0):** "Separate execution routing from language processing." Deterministic workflow engine orchestrates; LLMs confined to cognitive nodes. This is exactly Hiver §7, without needing ADK itself.
- **Production reality 2025–2026:** Workflows won production; fully autonomous multi-agent remains exploratory outside coding/deep-research niches. Hybrid pattern emerging: agent sets goals, deterministic modules do validated work — Hiver inverts this correctly (deterministic sets goals, one bounded LLM call does drafting).
- **Hiver implication:** every Hiver stage has knowable inputs/outputs and a fixed successor. Routing (intent → template/exemplar bucket) is an LLM-or-sklearn classifier picking off a human-written menu — still a workflow per Google/Anthropic taxonomy, not an agent.

---

## 5. MCP status Sep 2026 — use as protocol, not runtime

- **Spec `2026-07-28` (final Jul 2026):** stateless core (no `initialize` handshake, no `Mcp-Session-Id`); self-describing `_meta` per request; `Mcp-Method`/`Mcp-Name` headers for gateway routing; `ttlMs`/`cacheScope` list caching; full JSON Schema 2020-12 for tool I/O (`oneOf`/`anyOf`/`$ref`); Tasks moved to `io.modelcontextprotocol/tasks` extension (`tasks/get`/`update`/`cancel`); Roots/Sampling/Logging deprecated (12-mo window); formal extensions framework; Tier-1 SDKs (TS/Python/Go/C#).
- **Roadmap:** server-initiated events, progressive tool discovery (don't pay for 100-tool catalogs up front), result-type unification, agent identity.
- **Hiver stance:** no MCP server/client needed now (no external tool federation). If a future exemplar store or ticket-system connector needs standard tooling, expose/consume it via MCP *without* adopting an agent loop. Keep tool surface tiny (2–4 tools max) to avoid selection degradation.

---

## 6. Structured outputs (Pydantic) — the reliability mechanism

Provider enforcement (OpenAI `responses.parse`/`text_format`, Anthropic `output_config.format` / strict tools, Gemini `response_json_schema`, local vLLM+XGrammar constrained decoding) guarantees **shape, not semantics**. Production rule for 2026:

1. Define `BaseModel` once; derive provider JSON Schema via `model_json_schema()`.
2. Enforce shape provider-side (`strict:true` where supported; enums, `Literal`, nested models, reasoning-field-first ordering).
3. **Always re-validate client-side** with `model_validate` + `field_validator`/`model_validator` (ranges, cross-field invariants like `escalate ⇔ confidence < τ`, non-empty reply, allowed intents).
4. Bounded retry: feed `ValidationError.errors()` (loc/msg/type) back to model, cap ≤2 retries, then fallback (template reply + escalate flag).
5. Log every failure with raw output + model version + prompt hash → `llm_validation_failures` table; alert on spike.
6. Version schemas (`v1`, `v2` with optional-field expansion) alongside prompts.

PydanticAI's Tool/Native/Prompted modes and `instructor`'s retry wrapper are reference implementations of this sandwich — reimplement the 30-line version in plain Python (§7) rather than importing their runtimes.

---

## 7. Recommended Hiver architecture (no framework)

```
validate_input (pydantic) → classify_intent (sklearn, p<50ms)
  → retrieve_exemplars (deterministic top-k)
  → draft_reply (ONE isolated LLM call, optional; Pydantic-validated)
  → escalate_decision (rules + confidence threshold)
  → validate_output (pydantic contract) → return / fallback
```

```python
from enum import Enum
from pydantic import BaseModel, Field, model_validator

class Intent(str, Enum):
    BILLING = "billing"; TECH = "technical"; ACCOUNT = "account"; OTHER = "other"

class TicketInput(BaseModel):
    subject: str = Field(min_length=1); body: str = Field(min_length=1)
    customer_tier: str = "standard"

class ClassifiedTicket(TicketInput):
    intent: Intent; confidence: float = Field(ge=0.0, le=1.0)

class DraftReply(BaseModel):
    intent: Intent
    reply_text: str = Field(min_length=20)
    needs_escalation: bool
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def escalation_consistent(self):
        if self.confidence < 0.55 and not self.needs_escalation:
            raise ValueError("low confidence must escalate")
        if not self.reply_text.strip():
            raise ValueError("reply_text must be non-empty")
        return self
```

- **Classify:** `sklearn.pipeline.Pipeline([TfidfVectorizer(), LogisticRegression()])` trained on `data/raw/twcs.csv`; persist to `models/`; emit `confidence` via `predict_proba`. Optional LLM classifier only as A/B, same `ClassifiedTicket` contract.
- **Retrieve:** pure function `retrieve_exemplars(intent, text, k=3)` — no LLM.
- **Draft:** single function `draft_reply(...)` with structured output + ≤2 retries + template fallback. Only network-touching stage; mockable in tests.
- **Escalate/validate:** pure rules + Pydantic; 100% unit-testable, auditable, SLA-bounded.

Deps: `pydantic>=2`, `scikit-learn`, `numpy` (+ `httpx`/`openai`/`anthropic` only inside `draft_reply` if enabled). No `langchain`, `langgraph`, `llama-index`, `crewai`, `pydantic-ai`, `openai-agents`, `agent-framework`, `adk`, or `dspy` in serving path.

---

## 8. Cost / reliability / testability note

- **Cost:** sklearn + retrieval ≈ $0 marginal; single LLM draft ≈ 1 call/ticket. Cheapest agent alternative (3-agent CrewAI-style on GPT-4o ≈ $0.10–0.20/run) is 10–50× costlier with worse variance.
- **Latency:** pipeline p95 = classifier ms + retrieval ms + 1 LLM call s. Agent p95 = N×LLM calls + tool round-trips, unbounded without caps.
- **Tests:** `pytest` on pure functions + Pydantic negative cases + golden reply files + sklearn cross-val + contract regression on model upgrade. No trace replay, no sandbox, no flaky loop assertions.

---

## 9. Revisit criteria (when to reopen this decision)

Adopt an orchestration/agent layer only if **all** apply: (a) step count/order becomes genuinely unpredictable at runtime (not just a new fixed branch); (b) bounded single-call + workflow patterns provably fail on evals; (c) verifiable ground truth per step exists (tests, env state); (d) team accepts sandboxing, iteration caps, and cost budgets. First escalation path if complexity grows: standalone `llama-index-workflows` or LangGraph `StateGraph` for the *routing subgraph only*, keeping classification/retrieval/validation deterministic; use DSPy/GEPA *offline* for prompt optimization.

---

## 10. Queries run (10 topics, Sep 2026)

1. LangChain/LangGraph status Sep 2026 — joint v1.0 Oct 2025, core 1.4.x / graph 1.2.6, AgentExecutor EOL Dec 2026.
2. LlamaIndex status 2026 — core v0.14.24, standalone workflows v2.23.3, llama-deploy deprecated.
3. PydanticAI status 2026 — V2.0 Jun 2026, capability/harness model, structured-output modes.
4. OpenAI Agents SDK status 2026 — v0.22.0, pre-1.0, Apr 2026 harness+sandbox+MCP.
5. CrewAI status 2026 — v1.15.x, ~58k stars, Crews+Flows, AMP platform.
6. Microsoft Agent Framework status 2026 — 1.0 GA Apr 2026, AutoGen+SK converged, A2A+MCP.
7. Google ADK status 2026 — 2.0 (breaking), 5 languages, Workflows+HITL thesis.
8. DSPy status 2026 — v3.3.x, Signatures+GEPA, ReActV2 experimental.
9. Deterministic workflow vs agents debate — Anthropic/OpenAI/Google converge on workflow-first.
10. MCP (`2026-07-28` stateless) + Pydantic structured-outputs validation sandwich — shape≠semantics, always re-validate, bounded retry.
