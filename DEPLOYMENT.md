# EC2 배포 전략 (GitHub Actions CI/CD)

## 개요

FastAPI RAG 애플리케이션을 AWS EC2에 GitHub Actions를 통해 자동 배포합니다.

## 배포 아키텍처

```
GitHub Push → GitHub Actions → EC2 (SSH) → 서비스 재시작 → 헬스 체크
```

## 프로젝트 구조

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 워크플로우
├── scripts/
│   ├── setup_ec2.sh           # EC2 초기 설정 스크립트
│   ├── setup_systemd.sh       # Systemd 서비스 설정
│   └── test_deployment.sh     # 배포 테스트 스크립트
├── app/                        # FastAPI 애플리케이션
├── env.template               # 환경 변수 템플릿
├── DEPLOYMENT.md              # 이 파일
└── QUICKSTART.md              # 빠른 시작 가이드
```

## 사전 준비

### 1. EC2 인스턴스 설정

- **OS**: Ubuntu 24.04 LTS
- **보안 그룹**: 8000번 포트 오픈 (FastAPI)
- **Python**: 3.10+
- **필수 패키지**: `python3-pip`, `python3-venv`, `git`

### 2. GitHub Secrets 등록

Repository Settings → Secrets and variables → Actions에 추가:

- `EC2_HOST`: EC2 퍼블릭 IP 또는 도메인
- `EC2_USER`: SSH 사용자 (기본: `ubuntu`)
- `EC2_SSH_KEY`: EC2 SSH 프라이빗 키 (PEM 파일 내용)
- `POSTGRES_CONNECTION_STRING`: PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키
- `LLM_PROVIDER`: LLM 제공자 (기본: `openai`)

### 3. EC2 초기 설정

#### 자동 설정 (권장)

```bash
# 저장소 클론
git clone <YOUR_REPO_URL> ~/rag-app
cd ~/rag-app

# 초기 설정 스크립트 실행
bash scripts/setup_ec2.sh

# 환경 변수 설정
cp env.template .env
nano .env  # 실제 값 입력
```

#### 수동 설정

```bash
# 의존성 설치
sudo apt update && sudo apt install -y python3-pip python3-venv git

# 애플리케이션 디렉토리 생성
mkdir -p ~/rag-app
cd ~/rag-app

# 환경 변수 파일 생성
cat > .env << EOF
POSTGRES_CONNECTION_STRING=your_connection_string
OPENAI_API_KEY=your_api_key
HOST=0.0.0.0
PORT=8000
EOF
```

## GitHub Actions 워크플로우

`.github/workflows/deploy.yml` 파일이 이미 생성되어 있습니다.

### 워크플로우 주요 기능

- ✅ `main` 브랜치 푸시 시 자동 배포
- ✅ 수동 실행 가능 (`workflow_dispatch`)
- ✅ 코드 자동 업데이트 (git pull)
- ✅ 의존성 자동 설치
- ✅ 환경 변수 자동 업데이트
- ✅ Systemd 서비스 자동 재시작
- ✅ 배포 후 헬스 체크
- ✅ 실패 시 로그 출력

### 수동 배포 트리거

GitHub 저장소 → Actions → Deploy to EC2 → Run workflow

## Systemd 서비스 (권장)

안정적인 운영을 위해 systemd 서비스를 등록하세요.

### 자동 설정 (권장)

```bash
cd ~/rag-app
bash scripts/setup_systemd.sh
```

이 스크립트는 자동으로:
- Systemd 서비스 파일 생성
- 서비스 활성화 및 시작
- 상태 확인

### 수동 설정

```bash
# 서비스 파일 생성
sudo tee /etc/systemd/system/rag-api.service > /dev/null << EOF
[Unit]
Description=RAG FastAPI Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$HOME/rag-app
Environment="PATH=$HOME/rag-app/venv/bin"
EnvironmentFile=$HOME/rag-app/.env
ExecStart=$HOME/rag-app/venv/bin/python $HOME/rag-app/app/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable rag-api
sudo systemctl start rag-api
```

## 배포 확인

### 자동 테스트 (권장)

```bash
# 로컬에서 EC2 테스트
bash scripts/test_deployment.sh <EC2_IP> 8000

# EC2에서 로컬 테스트
bash scripts/test_deployment.sh localhost 8000
```

이 스크립트는 자동으로:
- 헬스 체크
- 루트 엔드포인트 테스트
- API 문서 접근 확인
- 검색 엔드포인트 테스트

### 수동 확인

```bash
# 서비스 상태 확인
sudo systemctl status rag-api

# 로그 확인
sudo journalctl -u rag-api -f

# API 테스트
curl http://localhost:8000/health
curl http://localhost:8000/
```

## 롤백 전략

문제 발생 시 이전 버전으로 복구:

```bash
cd ~/rag-app
git log --oneline -5  # 커밋 해시 확인
git checkout <이전_커밋_해시>
sudo systemctl restart rag-api
```

## 모니터링

- **헬스 체크**: `/health` 엔드포인트 주기적 확인
- **로그**: `journalctl` 또는 `app.log` 파일 모니터링
- **리소스**: `htop` 또는 CloudWatch로 CPU/메모리 모니터링

## 보안 권장사항

1. **SSH 키 관리**: EC2 SSH 키는 안전하게 보관
2. **환경 변수**: 민감 정보는 GitHub Secrets에만 저장
3. **보안 그룹**: 필요한 포트만 오픈 (8000번 또는 80/443)
4. **HTTPS**: 프로덕션에서는 Nginx + Let's Encrypt 사용 권장
5. **방화벽**: UFW로 추가 보안 설정

## 트러블슈팅

- **포트 충돌**: `lsof -i :8000`으로 확인 후 프로세스 종료
- **권한 문제**: 파일/디렉토리 소유자 확인
- **의존성 오류**: 가상환경 재생성 (`rm -rf venv && python3 -m venv venv`)

