/** @type {import('next').NextConfig} */
const nextConfig = {
  // BFF proxy pattern: browser -> /api/* -> FastAPI (key stays server-side)
  output: "standalone",
  transpilePackages: ["three", "@react-three/fiber"],
};

export default nextConfig;
