/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Get the API URL from environment variable, with a fallback for local development


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

module.exports = nextConfig;
