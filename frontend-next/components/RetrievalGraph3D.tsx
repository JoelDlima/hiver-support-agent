"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { Passage } from "../lib";

// 3D retrieval graph: query = center node, top-k passages = satellites.
// Sized/colored by live score. 2 draw calls total (Points + LineSegments).
function Graph({ passages }: { passages: Passage[] }) {
  const pointsRef = useRef<THREE.Points>(null);
  const groupRef = useRef<THREE.Group>(null);

  const { positions, colors, linePositions } = useMemo(() => {
    const n = Math.max(passages.length, 1);
    const positions = new Float32Array((n + 1) * 3);
    const colors = new Float32Array((n + 1) * 3);
    // center (query) node
    positions[0] = 0; positions[1] = 0; positions[2] = 0;
    colors[0] = 0.2; colors[1] = 0.9; colors[2] = 1.0;
    const linePositions = new Float32Array(n * 6);
    passages.forEach((p, i) => {
      const a = (i / Math.max(n, 1)) * Math.PI * 2;
      const r = 2.2 - Math.min(Math.max(p.score, 0), 1) * 0.9; // higher score = closer
      const x = Math.cos(a) * r;
      const y = Math.sin(a * 1.7) * 1.1;
      const z = Math.sin(a) * r;
      positions[(i + 1) * 3] = x;
      positions[(i + 1) * 3 + 1] = y;
      positions[(i + 1) * 3 + 2] = z;
      const heat = Math.min(Math.max(p.score, 0), 1);
      colors[(i + 1) * 3] = 0.4 + heat * 0.6;
      colors[(i + 1) * 3 + 1] = 0.9 - heat * 0.4;
      colors[(i + 1) * 3 + 2] = 0.4;
      linePositions[i * 6] = 0; linePositions[i * 6 + 1] = 0; linePositions[i * 6 + 2] = 0;
      linePositions[i * 6 + 3] = x; linePositions[i * 6 + 4] = y; linePositions[i * 6 + 5] = z;
    });
    return { positions, colors, linePositions };
  }, [passages]);

  useFrame((_, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.25;
  });

  return (
    <group ref={groupRef}>
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
          <bufferAttribute attach="attributes-color" args={[colors, 3]} />
        </bufferGeometry>
        <pointsMaterial size={0.22} vertexColors sizeAttenuation />
      </points>
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[linePositions, 3]} />
        </bufferGeometry>
        <lineBasicMaterial color="#334155" transparent opacity={0.7} />
      </lineSegments>
    </group>
  );
}

export default function RetrievalGraph3D({ passages }: { passages: Passage[] }) {
  if (!passages.length) {
    return (
      <div className="flex h-56 items-center justify-center rounded-lg border border-slate-800 text-sm text-slate-500">
        No passages — run a prediction to see live retrieval.
      </div>
    );
  }
  return (
    <div className="h-56 overflow-hidden rounded-lg border border-slate-800 bg-black/40">
      <Canvas camera={{ position: [0, 0, 6] }} frameloop="always" dpr={1}>
        <ambientLight intensity={0.6} />
        <Graph passages={passages} />
      </Canvas>
    </div>
  );
}
