import type { NextConfig } from "next";
import withPWA from "next-pwa";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {},
  /* config options here */
  async rewrites() {
    // Vercel 환경 변수에서 API_URL 가져오기
    // NEXT_PUBLIC_ 접두사를 사용하면 클라이언트와 서버 모두에서 접근 가능
    // Vercel 프로젝트 → Settings → Environment Variables에서 NEXT_PUBLIC_API_URL 설정 필요
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;

    if (!apiUrl) {
      throw new Error('NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다. Vercel 환경 변수를 설정하세요.');
    }

    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

const pwaConfig = withPWA({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development", // 개발 모드에서는 비활성화 (경고 방지)
  buildExcludes: [/app-build-manifest\.json$/],
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: "NetworkFirst",
      options: {
        cacheName: "offlineCache",
        expiration: {
          maxEntries: 200,
        },
      },
    },
  ],
});

export default pwaConfig(nextConfig);
