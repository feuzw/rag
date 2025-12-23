import type { NextConfig } from "next";
import withPWA from "next-pwa";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {},
  /* config options here */
  async rewrites() {
    // EC2 또는 백엔드 서버 URL 설정
    // 프로덕션: EC2의 공개 IP 또는 도메인 (예: http://ec2-13-125-247-202.ap-northeast-2.compute.amazonaws.com:8000)
    // 개발: localhost:8000
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // rewrites는 서버 사이드에서만 작동하므로,
    // 프로덕션에서는 실제 백엔드 서버 URL을 사용해야 함
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
