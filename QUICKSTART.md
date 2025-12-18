# FastAPI RAG 시스템 빠른 시작 가이드

## 로컬 개발

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r app/requirements.txt

# 환경 변수 설정
cp env.template .env
# .env 파일을 편집하여 실제 값 입력
nano .env
```

### 2. 서버 실행

```bash
python app/main.py
```

API 문서: http://localhost:8000/docs

## EC2 배포

### 1. EC2 초기 설정

SSH로 EC2에 접속한 후:

```bash
# 저장소 클론
git clone <YOUR_REPO_URL> ~/rag-app
cd ~/rag-app

# 초기 설정 스크립트 실행
bash scripts/setup_ec2.sh

# .env 파일 생성 및 편집
nano .env
```

### 2. Systemd 서비스 설정

```bash
cd ~/rag-app
bash scripts/setup_systemd.sh
```

### 3. GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions:

- `EC2_HOST`: EC2 퍼블릭 IP
- `EC2_USER`: `ubuntu`
- `EC2_SSH_KEY`: SSH 프라이빗 키 (PEM 파일 내용)
- `POSTGRES_CONNECTION_STRING`: PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키
- `LLM_PROVIDER`: `openai` 또는 `midm`

### 4. 배포 테스트

```bash
# 로컬에서
bash scripts/test_deployment.sh <EC2_IP> 8000

# 또는 EC2에서
bash scripts/test_deployment.sh localhost 8000
```

### 5. 자동 배포

이제 `main` 브랜치에 푸시하면 자동으로 EC2에 배포됩니다:

```bash
git add .
git commit -m "Update application"
git push origin main
```

## 유용한 명령어

### 서비스 관리

```bash
# 상태 확인
sudo systemctl status rag-api

# 재시작
sudo systemctl restart rag-api

# 로그 확인
sudo journalctl -u rag-api -f

# 서비스 중지
sudo systemctl stop rag-api
```

### API 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 검색 테스트
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test query","k":5}'
```

## 문제 해결

### 서비스가 시작되지 않는 경우

```bash
# 로그 확인
sudo journalctl -u rag-api -n 50

# 환경 변수 확인
cat ~/rag-app/.env

# 수동 실행으로 에러 확인
cd ~/rag-app
source venv/bin/activate
python app/main.py
```

### 포트 충돌

```bash
# 8000번 포트 사용 중인 프로세스 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

## 더 자세한 정보

- 전체 배포 전략: [DEPLOYMENT.md](DEPLOYMENT.md)
- API 문서: http://your-ec2-ip:8000/docs

