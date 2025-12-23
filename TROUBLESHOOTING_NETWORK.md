# 네트워크 연결 문제 해결 가이드

## "Failed to fetch" 오류 해결 체크리스트

### 1. EC2 보안 그룹 확인 (가장 중요!)

**EC2 콘솔에서:**
1. 인스턴스 선택 → Security 탭
2. 보안 그룹 클릭
3. 인바운드 규칙 확인
4. 포트 8000이 없으면 추가:
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0
   - Description: FastAPI Server

### 2. EC2 서버 실행 확인

```bash
# SSH로 EC2 접속 후

# systemd 서비스 확인
sudo systemctl status rag-api

# 서비스가 없으면 설정
cd ~/rag-app
bash scripts/setup_systemd.sh

# 로그 확인
sudo journalctl -u rag-api -f

# 헬스 체크
curl http://localhost:8000/health
```

### 3. 외부 접근 테스트

**로컬 컴퓨터에서:**
```bash
# EC2 IP로 직접 테스트
curl http://13.125.247.202:8000/health

# DNS로 테스트
curl http://api.yourdomain.com:8000/health
```

### 4. Vercel 환경 변수 확인

**Vercel 대시보드:**
- Settings → Environment Variables
- `NEXT_PUBLIC_API_URL` 확인:
  - `http://api.yourdomain.com:8000` (DNS 사용)
  - 또는 `http://13.125.247.202:8000` (IP 직접 사용)
- **재배포 필수!**

### 5. DNS 전파 확인

```bash
# DNS 확인
nslookup api.yourdomain.com

# 또는
dig api.yourdomain.com
```

### 6. 브라우저 콘솔 확인

- F12 → Console 탭
- "API 요청 디버깅 정보" 로그 확인
- 실제 요청 URL 확인

## 일반적인 문제와 해결책

### 문제 1: EC2 보안 그룹 포트 미개방
**증상:** 외부에서 curl 테스트 실패
**해결:** 보안 그룹에 포트 8000 추가

### 문제 2: 서버가 실행되지 않음
**증상:** EC2에서 curl localhost:8000 실패
**해결:** systemd 서비스 설정 및 시작

### 문제 3: DNS 전파 미완료
**증상:** DNS 조회 시 다른 IP 반환
**해결:** DNS 전파 대기 (최대 24시간, 보통 수 분)

### 문제 4: Vercel 환경 변수 미설정
**증상:** Vercel 로그에 "localhost:8000" 표시
**해결:** 환경 변수 설정 후 재배포

### 문제 5: Mixed Content 오류
**증상:** 브라우저 콘솔에 Mixed Content 경고
**해결:** Next.js rewrites 사용 (이미 구현됨)

