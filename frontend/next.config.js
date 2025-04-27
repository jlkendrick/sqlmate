/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/auth/:path*',
        destination: 'http://127.0.0.1:5000/auth/:path*',
      },
      {
        source: '/query',
        destination: 'http://127.0.0.1:5000/query',
      },
      {
        source: "/users/:path*",
        destination: "http://127.0.0.1:5000/users/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
