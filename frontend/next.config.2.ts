import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/auth/:path*",
        destination: "http://127.0.0.1:5000/auth/:path*",
      },
      {
        source: "/query",
        destination: "http://127.0.0.1:5000/query",
      },
      {
        source: "/users/:path*",
        destination: "http://127.0.0.1:5000/users/:path*",
      },
    ];
  },
};

export default nextConfig;
