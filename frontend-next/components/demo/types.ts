"use client";

// Shared view-model for the demo tab shell (page.tsx owns the state; TryIt and
// ProofTab render from it). Keeps every existing widget mounted and reachable
// without prop-drilling each field individually.

import type { EmbedPoint, Passage, PredictResponse } from "../../lib";

/** Predict response plus workstream A/B contract additions (offline flag, template id). */
export type PredictResult = PredictResponse & {
  offline?: boolean;
  template_id?: string;
};

export type JudgeState = { groundedness: number; verdict: string } | null;

export type RunLogEntry = {
  t: number;
  brand: string;
  intent: string;
  decision: string;
  ms?: number;
};

export type RetrievalView = "flow" | "3d";

export type DemoVM = {
  brand: string;
  text: string;
  loading: boolean;
  streaming: string;
  result: PredictResult | null;
  resultAt: number | null;
  now: number;
  runLog: RunLogEntry[];
  judge: JudgeState;
  passages: Passage[];
  embed: EmbedPoint[] | null;
  embedLoading: boolean;
  inspectId: string | null;
  error: string | null;
  apiOk: boolean | null;
  retrievalView: RetrievalView;
  passagesLoading: boolean;
  passagesError: string | null;
  judgeLoading: boolean;
  judgeError: string | null;
  streamChunks: number;
  streamToks: number | null;
  metricsNonce: number;
  setBrand: (b: string) => void;
  setText: (t: string) => void;
  setRetrievalView: (v: RetrievalView) => void;
  runPredict: (nextBrand?: string) => void;
  runStream: () => void;
  loadPassages: (j: PredictResult) => void;
  loadJudge: (j: PredictResult) => void;
  loadEmbed: (b: string, q: string) => void;
  bumpMetrics: () => void;
  /** Switch the shell to the Proof tab (used by receipt → Inspector links). */
  goProof: () => void;
};
