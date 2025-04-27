import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/auth/:path*",
        destination: "https://sqlmate-18170637984.us-central1.run.app/auth/:path*",
      },
      {
        source: "/query",
        destination: "https://sqlmate-18170637984.us-central1.run.app/query",
      },
      {
        source: "/users/:path*",
        destination: "https://sqlmate-18170637984.us-central1.run.app/users/:path*",
      },
    ];
  },
};

export default nextConfig;
