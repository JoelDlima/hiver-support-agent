"use client";

import { useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { EmbedPoint } from "../../lib";
import { Card } from "../sg/card";

const QUERY_COLOR = "#0891b2"; // --color-aqua
const PASSAGE_HIGH = "#14b8a6"; // SmartGrey chart line teal
const PASSAGE_LOW = "#5b6e71"; // --color-muted
const LINK_COLOR = "#3a4444"; // dark hairline-strong

function isFiniteNum(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

// Positions come from the embed prop (z optional, defaults to 0);
// fall back to a circle when coordinates are missing or carry no variance.
function usePositions(points: EmbedPoint[]): [number, number, number][] {
  return useMemo(() => {
    const ok =
      points.length > 0 &&
      points.every((p) => isFiniteNum(p.x) && isFiniteNum(p.y) && (p.z === undefined || isFiniteNum(p.z)));
    if (ok) {
      const xs = points.map((p) => p.x);
      const ys = points.map((p) => p.y);
      const spread =
        Math.max(...xs) - Math.min(...xs) + (Math.max(...ys) - Math.min(...ys));
      if (spread > 1e-9) {
        const s =
          2.4 /
          Math.max(
            1e-6,
            Math.max(...points.map((p) => Math.abs(p.x) + Math.abs(p.y) + Math.abs(p.z ?? 0)))
          );
        return points.map(
          (p) => [p.x * s * 3, p.y * s * 3, (p.z ?? 0) * s * 3] as [number, number, number]
        );
      }
    }
    return points.map((_, i) => {
      const a = (i / Math.max(points.length, 1)) * Math.PI * 2;
      return [Math.cos(a) * 2, Math.sin(a * 1.7) * 1.1, Math.sin(a) * 2];
    });
  }, [points]);
}

function passageColor(score: number): string {
  const t = Math.min(Math.max(score ?? 0, 0), 1);
  const c = new THREE.Color(PASSAGE_LOW).lerp(new THREE.Color(PASSAGE_HIGH), t);
  return `#${c.getHexString()}`;
}

function Scene({
  points,
  positions,
  queryIdx,
  onHover,
}: {
  points: EmbedPoint[];
  positions: [number, number, number][];
  queryIdx: number;
  onHover: (p: EmbedPoint | null) => void;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const scaleRef = useRef(0.2);

  const linePositions = useMemo(() => {
    const q = positions[queryIdx] || [0, 0, 0];
    const arr = new Float32Array(Math.max(points.length - 1, 0) * 6);
    let k = 0;
    positions.forEach((pos, i) => {
      if (i === queryIdx) return;
      arr[k++] = q[0];
      arr[k++] = q[1];
      arr[k++] = q[2];
      arr[k++] = pos[0];
      arr[k++] = pos[1];
      arr[k++] = pos[2];
    });
    return arr;
  }, [positions, points.length, queryIdx]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2;
      const s = Math.min(1, scaleRef.current + delta * 1.5);
      scaleRef.current = s;
      groupRef.current.scale.setScalar(s);
    }
  });

  return (
    <group ref={groupRef}>
      {points.map((p, i) => {
        const isQuery = i === queryIdx;
        const heat = Math.min(Math.max(p.score ?? 0, 0), 1);
        const radius = isQuery ? 0.17 : 0.06 + heat * 0.08;
        return (
          <mesh
            key={p.tweet_id || i}
            position={positions[i]}
            onPointerOver={(e) => {
              e.stopPropagation();
              onHover(p);
            }}
            onPointerOut={() => onHover(null)}
          >
            <sphereGeometry args={[radius, 16, 16]} />
            {isQuery ? (
              <meshStandardMaterial
                color={QUERY_COLOR}
                emissive={QUERY_COLOR}
                emissiveIntensity={0.9}
                roughness={0.3}
              />
            ) : (
              <meshStandardMaterial color={passageColor(p.score ?? 0)} roughness={0.5} />
            )}
          </mesh>
        );
      })}
      {points.length > 1 ? (
        <lineSegments>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" args={[linePositions, 3]} />
          </bufferGeometry>
          <lineBasicMaterial color={LINK_COLOR} transparent opacity={0.8} />
        </lineSegments>
      ) : null}
    </group>
  );
}

export default function EmbedScene({
  embed,
  loading,
}: {
  embed: EmbedPoint[] | null;
  loading: boolean;
}) {
  const [hovered, setHovered] = useState<EmbedPoint | null>(null);
  const points = embed || [];
  const positions = usePositions(points);
  const queryIdx = useMemo(() => {
    const q = points.findIndex((p) => p.is_query);
    return q >= 0 ? q : 0;
  }, [points]);
  const hash = useMemo(
    () => JSON.stringify(points.map((p) => [p.tweet_id, p.x, p.y, p.z, p.score, p.is_query])),
    [points]
  );

  return (
    <Card className="rounded-[24px] p-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Projection
          </p>
          <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
            Embedding
          </h3>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted">
          <span className="inline-flex items-center gap-1.5">
            <span
              className="inline-block size-2 rounded-full"
              style={{ backgroundColor: QUERY_COLOR }}
            />
            Query
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span
              className="inline-block size-2 rounded-full"
              style={{ backgroundColor: PASSAGE_HIGH }}
            />
            Passages
          </span>
        </div>
      </div>
      {loading ? (
        <div className="flex h-56 items-center justify-center rounded-2xl border border-hairline-soft bg-[#050505] text-sm text-muted">
          Loading projection…
        </div>
      ) : points.length === 0 ? (
        <div className="flex h-56 items-center justify-center rounded-2xl border border-hairline-soft bg-[#050505] text-sm text-muted">
          No embedding yet
        </div>
      ) : (
        <div className="relative h-56 overflow-hidden rounded-2xl border border-hairline-soft bg-[#050505]">
          <Canvas
            camera={{ position: [3.5, 2.5, 5] }}
            frameloop="always"
            dpr={1}
            style={{ background: "transparent" }}
          >
            <ambientLight intensity={0.7} />
            <directionalLight position={[4, 6, 5]} intensity={0.8} />
            <Scene
              key={hash}
              points={points}
              positions={positions}
              queryIdx={queryIdx}
              onHover={setHovered}
            />
          </Canvas>
          {hovered ? (
            <div className="absolute left-2 top-2 flex items-center gap-2 rounded-full border border-hairline bg-card px-2.5 py-1">
              <span className="font-mono text-[11px]">{hovered.tweet_id}</span>
              <span className="font-mono text-[11px] tabular-nums text-muted">
                {Number(hovered.score ?? 0).toFixed(3)}
              </span>
            </div>
          ) : null}
        </div>
      )}
    </Card>
  );
}
