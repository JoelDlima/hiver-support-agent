// dagre ships no TypeScript declarations and this project may only add
// @xyflow/react, dagre and zod as dependencies (no @types/dagre).
// This minimal ambient module keeps `npx tsc --noEmit` clean; all dagre
// handles below are intentionally typed via local interfaces.
declare module "dagre" {
  const dagre: {
    graphlib: {
      Graph: new () => {
        setGraph(opts: Record<string, unknown>): void;
        setDefaultEdgeLabel(fn: () => Record<string, unknown>): void;
        setNode(id: string, dims: { width: number; height: number }): void;
        setEdge(from: string, to: string): void;
        node(id: string): { x: number; y: number };
      };
    };
    layout(g: unknown): void;
  };
  export default dagre;
}
