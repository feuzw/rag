import type { NextConfig } from "next";
import withPWA from "next-pwa";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {},
  /* config options here */
  async rewrites() {
    // EC2 또는 백엔드 서버 URL 설정
    // rewrites는 서버 사이드에서만 작동하므로 HTTPS → HTTP 문제 없음
    // NEXT_PUBLIC_API_URL 환경 변수에 포트 번호 포함 필요 (예: http://api.leeyujin.kr:8000)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // 포트 번호가 없으면 기본 포트 8000 추가
    let finalApiUrl = apiUrl;
    if (!apiUrl.includes(':') || (!apiUrl.match(/:\d+/) && !apiUrl.endsWith('/'))) {
      // URL에 포트가 없으면 추가
      const urlObj = new URL(apiUrl.startsWith('http') ? apiUrl : `http://${apiUrl}`);
      if (!urlObj.port || urlObj.port === '80' || urlObj.port === '443') {
        urlObj.port = '8000';
      }
      finalApiUrl = urlObj.toString().replace(/\/$/, ''); // 마지막 슬래시 제거
    }

    console.log('✅ API URL for rewrites:', finalApiUrl);

    return [
      {
        source: '/api/:path*',
        destination: `${finalApiUrl}/:path*`,
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
