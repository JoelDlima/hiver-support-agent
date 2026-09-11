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

export const FASTAPI_URL =
  process.env.FASTAPI_URL || "http://127.0.0.1:8000";
