/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Get the API URL from environment variable, with a fallback for local development


    return [
      {
        source: "/auth/:path*",
        destination: "http://127.0.0.1:8080/auth/:path*",
      },
      {
        source: "/query",
        destination: "http://127.0.0.1:8080/query",
      },
      {
        source: "/users/:path*",
        destination: "http://127.0.0.1:8080/users/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
