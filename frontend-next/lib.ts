export type PredictResponse = {
  request_id: string;
  brand: string;
  intent: string;
  intent_confidence: number;
  draft_reply: string;
  grounding_passage_ids: string[];
  decision: string;
  escalate_reason: string;
  signals: Record<string, unknown> & {
    classify_ms?: number;
    retrieve_ms?: number;
    draft_ms?: number;
    draft_path?: string;
    groq_reason?: string;
  };
  draft_path: string;
  groq_reason?: string;
  latency_ms: number;
  truncated?: boolean;
};

export type Passage = {
  tweet_id: string;
  score: number;
  text: string;
};

export type EmbedPoint = {
  tweet_id: string;
  x: number;
  y: number;
  z?: number;
  score: number;
  is_query?: boolean;
};

export type InspectRecord = {
  request_id: string;
  timestamp: string;
  brand: string;
  text: string;
  intent: string;
  intent_confidence: number;
  decision: string;
  escalate_reason: string;
  timings: {
    classify_ms?: number;
    retrieve_ms?: number;
    draft_ms?: number;
    latency_ms?: number;
  } & Record<string, number | undefined>;
  passages: Passage[];
  llm: {
    model: string;
    system: string;
    user: string;
    completion: string;
    prompt_tokens: number;
    completion_tokens: number;
    draft_path: string;
    groq_reason: string;
  };
};

export type EvalItem = {
  event: "item";
  id: string;
  text: string;
  brand: string;
  intent?: string;
  ok?: boolean;
  note?: string;
};

export type EvalDone = {
  event: "done";
  total: number;
  passed: number;
  failed: number;
};

export const FASTAPI_URL =
  process.env.FASTAPI_URL || "http://127.0.0.1:8000";

// NOTE: server-only BFF helpers live in ./lib/proxy.ts (imports next/server).
// They are intentionally NOT re-exported here: lib.ts is also imported by
// client components (type-only today), and a next/server import would break
// the client bundle the day someone value-imports from here.

// Shared SmartGrey-ported classnames helper (see ./lib/cn.ts).
export { cn } from "./lib/cn";
