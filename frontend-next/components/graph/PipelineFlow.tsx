"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Background,
  Controls,
  Edge,
  Handle,
  Node,
  NodeProps,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";

export type PipelineStepState = "done" | "active" | "idle";

export type PipelineFlowProps = {
  classifyMs?: number;
  retrieveMs?: number;
  draftMs?: number;
  latencyMs?: number;
  intent?: string;
  intentConfidence?: number;
  draftPath?: string;
  decision?: string;
  requestId?: string | null;
  /** True while /predict or /predict/stream is in flight. */
  running?: boolean;
  /** True once a /predict (or stream final) response has arrived. */
  hasResult?: boolean;
};

type StepNodeData = {
  title: string;
  ms?: number;
  note?: string;
  state: PipelineStepState;
};

function formatStepMs(v: unknown): string {
  return typeof v === "number" && Number.isFinite(v) ? `${Math.round(v)} ms` : "—";
}

function StepNode(props: NodeProps) {
  const data = props.data as unknown as StepNodeData;
  const ring =
    data.state === "done"
      ? "border-teal-600/50"
      : data.state === "active"
        ? "border-amber-500/60 animate-pulse"
        : "border-hairline-soft opacity-70";
  return (
    <div
      className={`w-48 rounded-2xl border-2 bg-card px-3 py-2 shadow-sm ${ring}`}
    >
      <Handle type="target" position={Position.Left} className="!bg-teal-700" />
      <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-teal">
        {data.title}
      </p>
      <p className="mt-0.5 font-mono text-sm font-semibold tabular-nums text-ink">
        {formatStepMs(data.ms)}
      </p>
      {data.note ? (
        <p className="mt-0.5 truncate text-[11px] text-muted" title={data.note}>
          {data.note}
        </p>
      ) : null}
      <Handle type="source" position={Position.Right} className="!bg-teal-700" />
    </div>
  );
}

const nodeTypes = { step: StepNode };

const NODE_W = 192;
const NODE_H = 92;

type StepDef = {
  id: string;
  title: string;
  ms?: number;
  note?: string;
  state: PipelineStepState;
};

function buildSteps(p: PipelineFlowProps): StepDef[] {
  // Every value below comes from live /predict signals passed in as props.
  // Missing timings render as "—", never as invented numbers.
  const live = p.hasResult === true;
  const perStep: PipelineStepState = p.running ? "active" : live ? "done" : "idle";
  return [
    {
      id: "classify",
      title: "Classify",
      ms: p.classifyMs,
      note:
        p.intent !== undefined
          ? `${p.intent} @ ${Number(p.intentConfidence ?? 0).toFixed(3)}`
          : undefined,
      state: perStep,
    },
    {
      id: "retrieve",
      title: "Retrieve",
      ms: p.retrieveMs,
      note: undefined,
      state: perStep,
    },
    {
      id: "draft",
      title: `Draft (${p.draftPath || "template"})`,
      ms: p.draftMs,
      note: p.draftPath,
      state: perStep,
    },
    {
      id: "escalate",
      title: "Escalate",
      ms: p.latencyMs,
      note: p.decision,
      state: perStep,
    },
  ];
}

function layoutGraph(steps: StepDef[], animated: boolean): { nodes: Node[]; edges: Edge[] } {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 24, ranksep: 56 });
  g.setDefaultEdgeLabel(() => ({}));
  for (const s of steps) g.setNode(s.id, { width: NODE_W, height: NODE_H });
  const pairs: Array<[string, string]> = [
    ["classify", "retrieve"],
    ["retrieve", "draft"],
    ["draft", "escalate"],
  ];
  for (const [a, b] of pairs) g.setEdge(a, b);
  dagre.layout(g);
  const nodes: Node[] = steps.map((s) => {
    const pos = g.node(s.id);
    return {
      id: s.id,
      type: "step",
      position: { x: pos.x - NODE_W / 2, y: pos.y - NODE_H / 2 },
      data: { title: s.title, ms: s.ms, note: s.note, state: s.state },
    };
  });
  const edges: Edge[] = pairs.map(([a, b]) => ({
    id: `${a}-${b}`,
    source: a,
    target: b,
    animated,
    style: { strokeWidth: 2 },
  }));
  return { nodes, edges };
}

export default function PipelineFlow(props: PipelineFlowProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const steps = useMemo(() => buildSteps(props), [props]);
  const animated = props.running === true || props.hasResult === true;
  const initial = useMemo(() => layoutGraph(steps, animated), [steps, animated]);
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);

  useEffect(() => {
    const laid = layoutGraph(steps, animated);
    setNodes(laid.nodes);
    setEdges(laid.edges);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [steps, animated]);

  if (!mounted) {
    return (
      <div className="flex h-72 items-center justify-center rounded-2xl border border-hairline-soft bg-paper text-sm text-muted">
        Loading pipeline graph…
      </div>
    );
  }

  return (
    <div className="h-72 overflow-hidden rounded-2xl border border-hairline-soft bg-paper">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.4}
        maxZoom={1.5}
        nodesConnectable={false}
        proOptions={{ hideAttribution: false }}
        aria-label="Live pipeline DAG: classify, retrieve, draft, escalate with per-step milliseconds from the predict response"
      >
        <Background gap={18} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
