"use client";

// Runtime validation (zod) for every live payload the proof widgets consume:
// SSE chunks from /api/stream + /api/eval/run, the /api/judge verdict, the
// /api/predict response and the /api/inspect record. All schemas are lenient
// about extra backend fields (.passthrough() / .catchall) but strict about
// the fields the UI actually renders, so a malformed chunk is skipped instead
// of crashing the widget.
import { z } from "zod";

export const SseStartSchema = z
  .object({
    event: z.literal("start"),
    request_id: z.string().optional(),
    brand: z.string().optional(),
  })
  .passthrough();

export const SseStagesSchema = z
  .object({
    event: z.literal("stages"),
    intent: z.string().optional(),
    intent_confidence: z.number().optional(),
    classify_ms: z.number().optional(),
    retrieve_ms: z.number().optional(),
    draft_ms: z.number().optional(),
    latency_ms: z.number().optional(),
  })
  .passthrough();

export const SseTokenSchema = z
  .object({
    event: z.literal("token"),
    text: z.string(),
  })
  .passthrough();

export const SseFinalSchema = z
  .object({
    event: z.literal("final"),
    request_id: z.string(),
    brand: z.string().optional(),
    intent: z.string().optional(),
    intent_confidence: z.number().optional(),
    draft_reply: z.string().optional(),
    grounding_passage_ids: z.array(z.string()).optional(),
    decision: z.string().optional(),
    escalate_reason: z.string().optional(),
    signals: z.record(z.unknown()).optional(),
    draft_path: z.string().optional(),
    groq_reason: z.string().optional(),
    latency_ms: z.number().optional(),
    truncated: z.boolean().optional(),
  })
  .passthrough();

export const StreamEventSchema = z.discriminatedUnion("event", [
  SseStartSchema,
  SseStagesSchema,
  SseTokenSchema,
  SseFinalSchema,
]);

export type StreamEvent = z.infer<typeof StreamEventSchema>;
export type SseFinal = z.infer<typeof SseFinalSchema>;

/** Parse one raw SSE `data:` payload; returns null for keep-alives/[DONE]/junk. */
export function parseStreamPayload(payload: string): StreamEvent | null {
  const t = payload.trim();
  if (!t || t === "[DONE]") return null;
  let raw: unknown;
  try {
    raw = JSON.parse(t);
  } catch {
    return null;
  }
  const parsed = StreamEventSchema.safeParse(raw);
  return parsed.success ? parsed.data : null;
}

export const JudgeSchema = z
  .object({
    groundedness: z.number(),
    safety: z.number().optional(),
    verdict: z.string(),
    rubric: z.string().optional(),
  })
  .passthrough();

export type JudgePayload = z.infer<typeof JudgeSchema>;

export const PassageSchema = z
  .object({
    tweet_id: z.string(),
    score: z.number(),
    text: z.string().optional().default(""),
  })
  .passthrough();

export type PassagePayload = z.infer<typeof PassageSchema>;

export function parsePassageList(raw: unknown): { tweet_id: string; score: number; text: string }[] | null {
  const parsed = z.array(PassageSchema).safeParse(raw);
  if (!parsed.success) return null;
  return parsed.data.map((p) => ({ tweet_id: p.tweet_id, score: p.score, text: p.text || "" }));
}

export const PredictResponseSchema = z
  .object({
    request_id: z.string(),
    brand: z.string().optional(),
    intent: z.string().optional(),
    intent_confidence: z.number().optional(),
    draft_reply: z.string().optional(),
    grounding_passage_ids: z.array(z.string()).optional(),
    decision: z.string().optional(),
    escalate_reason: z.string().optional(),
    signals: z.record(z.unknown()).optional(),
    draft_path: z.string().optional(),
    groq_reason: z.string().optional(),
    latency_ms: z.number().optional(),
    truncated: z.boolean().optional(),
    // Workstream A/B contract additions (all optional — absent until live).
    // `offline` echoes PredictIn.offline: template-only draft, no LLM calls.
    // `template_id` identifies the template used for the draft, when known.
    offline: z.boolean().optional(),
    template_id: z.string().optional(),
  })
  .passthrough();

export const InspectLlmSchema = z
  .object({
    model: z.string().optional(),
    system: z.string().optional(),
    user: z.string().optional(),
    completion: z.string().nullable().optional(),
    prompt_tokens: z.number().nullable().optional(),
    completion_tokens: z.number().nullable().optional(),
    draft_path: z.string().optional(),
    groq_reason: z.string().optional(),
  })
  .passthrough();

export const InspectRecordSchema = z
  .object({
    request_id: z.string(),
    timestamp: z.string().optional(),
    brand: z.string().optional(),
    text: z.string().optional(),
    intent: z.string().optional(),
    intent_confidence: z.number().optional(),
    decision: z.string().optional(),
    escalate_reason: z.string().optional(),
    timings: z.record(z.unknown()).optional(),
    passages: z.array(PassageSchema).optional(),
    llm: InspectLlmSchema.optional(),
  })
  .passthrough();

export type InspectRecordPayload = z.infer<typeof InspectRecordSchema>;

// ---- POST /judge/groundedness (workstream A contract; may be pending) ----
// Request: {brand, text, reply, passage_ids?}
// Response: {claims: [{text, supported, passage_id}], score, model}

export const GroundednessClaimSchema = z
  .object({
    text: z.string(),
    supported: z.boolean(),
    passage_id: z.string().nullable().optional(),
  })
  .passthrough();

export const GroundednessSchema = z
  .object({
    claims: z.array(GroundednessClaimSchema),
    score: z.number().optional(),
    model: z.string().optional(),
  })
  .passthrough();

export type GroundednessPayload = z.infer<typeof GroundednessSchema>;

// ---- GET /eval/compare?brands=virgin,apple (workstream A contract; pending) ----
// Response: {results: {virgin: {...}, apple: {...}}}
// Per-brand: {intent_acc, macro_f1, esc_f1, ground_mean, n}

export const CompareBrandSchema = z
  .object({
    intent_acc: z.number().optional(),
    macro_f1: z.number().optional(),
    esc_f1: z.number().optional(),
    esc_p: z.number().optional(),
    esc_r: z.number().optional(),
    ground_mean: z.number().optional(),
    n: z.number().optional(),
  })
  .passthrough();

export const CompareSchema = z
  .object({
    results: z.record(CompareBrandSchema),
  })
  .passthrough();

export type ComparePayload = z.infer<typeof CompareSchema>;

// ---- POST /eval/retrieval-ablation (workstream A contract; pending) ----
// Response: {arms: [{name, k, groundedness_mean, ge4_rate, p50_ms}]}

export const AblationArmSchema = z
  .object({
    name: z.string().optional(),
    k: z.number().optional(),
    groundedness_mean: z.number().optional(),
    ge4_rate: z.number().optional(),
    p50_ms: z.number().optional(),
    p95_ms: z.number().optional(),
    recall_proxy: z.number().optional(),
  })
  .passthrough();

export const AblationSchema = z
  .object({
    arms: z.array(AblationArmSchema),
  })
  .passthrough();

export type AblationPayload = z.infer<typeof AblationSchema>;

// ---- /api/eval/run SSE events ----

export const EvalItemSchema = z
  .object({
    event: z.literal("item").optional(),
    i: z.number().optional(),
    id: z.union([z.string(), z.number()]).optional(),
    text: z.string().optional(),
    human_intent: z.string().optional(),
    pred_intent: z.string().optional(),
    ok: z.boolean().optional(),
    esc_ok: z.boolean().optional(),
    intent: z.string().optional(),
    note: z.string().optional(),
  })
  .passthrough();

export const EvalDoneSchema = z
  .object({
    event: z.literal("done"),
    n: z.number().optional(),
    total: z.number().optional(),
    intent_acc: z.number().optional(),
    esc_acc: z.number().optional(),
    passed: z.number().optional(),
  })
  .passthrough();

export const EvalErrorSchema = z
  .object({
    event: z.literal("error"),
    detail: z.string().optional(),
  })
  .passthrough();

/** Parse one raw eval SSE `data:` payload into item/done/error/unknown. */
export function parseEvalPayload(payload: string):
  | { kind: "item"; value: z.infer<typeof EvalItemSchema> }
  | { kind: "done"; value: z.infer<typeof EvalDoneSchema> }
  | { kind: "error"; value: z.infer<typeof EvalErrorSchema> }
  | { kind: "unknown" } {
  const t = payload.trim();
  if (!t || t === "[DONE]") return { kind: "unknown" };
  let raw: unknown;
  try {
    raw = JSON.parse(t);
  } catch {
    return { kind: "unknown" };
  }
  if (typeof raw !== "object" || raw === null) return { kind: "unknown" };
  const rec = raw as Record<string, unknown>;
  if (rec.event === "done") {
    const p = EvalDoneSchema.safeParse(raw);
    return p.success ? { kind: "done", value: p.data } : { kind: "unknown" };
  }
  if (rec.event === "error") {
    const p = EvalErrorSchema.safeParse(raw);
    return p.success ? { kind: "error", value: p.data } : { kind: "unknown" };
  }
  if (rec.event === "item" || typeof rec.i === "number") {
    const p = EvalItemSchema.safeParse(raw);
    return p.success ? { kind: "item", value: p.data } : { kind: "unknown" };
  }
  return { kind: "unknown" };
}
