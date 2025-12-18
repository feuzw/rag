#!/bin/bash
# 배포 테스트 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 배포 테스트 시작..."

# 서버 주소 설정 (환경 변수 또는 기본값)
SERVER_HOST=${1:-"localhost"}
SERVER_PORT=${2:-"8000"}
BASE_URL="http://${SERVER_HOST}:${SERVER_PORT}"

echo "서버: $BASE_URL"
echo ""

# 1. 헬스 체크
echo "1️⃣  헬스 체크 테스트..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 헬스 체크 성공${NC}"
    echo "응답: $RESPONSE_BODY"
else
    echo -e "${RED}❌ 헬스 체크 실패 (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# 2. 루트 엔드포인트
echo "2️⃣  루트 엔드포인트 테스트..."
ROOT_RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/")
HTTP_CODE=$(echo "$ROOT_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$ROOT_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 루트 엔드포인트 성공${NC}"
    echo "응답: $RESPONSE_BODY"
else
    echo -e "${RED}❌ 루트 엔드포인트 실패 (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
echo ""

# 3. API 문서 확인
echo "3️⃣  API 문서 접근 테스트..."
DOCS_RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/docs")
HTTP_CODE=$(echo "$DOCS_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ API 문서 접근 성공${NC}"
    echo "URL: ${BASE_URL}/docs"
else
    echo -e "${YELLOW}⚠️  API 문서 접근 실패 (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# 4. 검색 엔드포인트 테스트 (선택적)
echo "4️⃣  검색 엔드포인트 테스트..."
SEARCH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","k":1}')
HTTP_CODE=$(echo "$SEARCH_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 검색 엔드포인트 성공${NC}"
elif [ "$HTTP_CODE" = "500" ]; then
    echo -e "${YELLOW}⚠️  검색 엔드포인트 응답 있음 (데이터베이스 미설정 가능)${NC}"
else
    echo -e "${YELLOW}⚠️  검색 엔드포인트 테스트 스킵 (HTTP $HTTP_CODE)${NC}"
fi
echo ""

echo -e "${GREEN}✅ 배포 테스트 완료!${NC}"
echo ""
echo "추가 테스트:"
echo "  - API 문서: ${BASE_URL}/docs"
echo "  - OpenAPI 스펙: ${BASE_URL}/openapi.json"

