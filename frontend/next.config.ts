import type { NextConfig } from "next";
import withPWA from "next-pwa";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {},
  /* config options here */
  async rewrites() {
    // EC2 또는 백엔드 서버 URL 설정
    // 프로덕션: EC2의 공개 IP 또는 도메인
    // 개발: localhost:8000
    // rewrites는 서버 사이드에서만 작동하므로 HTTPS → HTTP 문제 없음
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'http://api.yourdomain.com:8000' // 실제 API 서브도메인으로 변경 필요
        : 'http://localhost:8000');

    console.log('API URL for rewrites:', apiUrl);

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
