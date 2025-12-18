# ✅ CI/CD 설정 완료!

FastAPI RAG 애플리케이션을 EC2에 자동 배포하는 GitHub Actions CI/CD 파이프라인이 설정되었습니다.

## 📦 생성된 파일

### 1. GitHub Actions 워크플로우
- **`.github/workflows/deploy.yml`** (2.2KB)
  - main 브랜치 푸시 시 자동 배포
  - 수동 실행 가능 (workflow_dispatch)
  - 배포 후 헬스 체크 자동 수행

### 2. 자동화 스크립트
- **`scripts/setup_ec2.sh`** (1.3KB)
  - EC2 초기 설정 자동화
  - 의존성 설치, 환경 변수 템플릿 생성

- **`scripts/setup_systemd.sh`** (1.4KB)
  - Systemd 서비스 자동 설정
  - 서비스 활성화 및 시작

- **`scripts/test_deployment.sh`** (2.5KB)
  - 배포 후 자동 테스트
  - 헬스 체크, API 엔드포인트 검증

### 3. 문서
- **`CICD_SETUP_GUIDE.md`** (4.0KB)
  - 3단계 빠른 시작 가이드
  - GitHub Secrets 설정 방법
  - 문제 해결 가이드

- **`DEPLOYMENT.md`** (5.4KB)
  - 전체 배포 전략 상세 문서
  - 아키텍처 설명
  - 보안 권장사항

- **`QUICKSTART.md`** (2.5KB)
  - 로컬 개발 및 배포 빠른 시작
  - 유용한 명령어 모음

### 4. 설정 파일
- **`env.template`** (350B)
  - 환경 변수 템플릿

## 🚀 다음 단계 (3단계만!)

### 1️⃣ GitHub Secrets 설정
Repository → Settings → Secrets and variables → Actions

필수 Secrets:
- `EC2_HOST` - EC2 IP 주소
- `EC2_USER` - SSH 사용자 (ubuntu)
- `EC2_SSH_KEY` - SSH 프라이빗 키 전체 내용
- `POSTGRES_CONNECTION_STRING` - DB 연결 문자열
- `OPENAI_API_KEY` - OpenAI API 키
- `LLM_PROVIDER` - openai 또는 midm

### 2️⃣ EC2 초기 설정
```bash
# SSH로 EC2 접속
ssh -i your-key.pem ubuntu@<EC2_IP>

# 저장소 클론
git clone <YOUR_REPO_URL> ~/rag-app
cd ~/rag-app

# 자동 설정 실행
bash scripts/setup_ec2.sh

# 환경 변수 설정
cp env.template .env
nano .env

# Systemd 서비스 설정
bash scripts/setup_systemd.sh

# 테스트
bash scripts/test_deployment.sh localhost 8000
```

### 3️⃣ 자동 배포 확인
```bash
# 로컬에서 변경사항 푸시
git add .
git commit -m "Setup CI/CD"
git push origin main
```

GitHub Actions 탭에서 배포 진행 상황 확인!

## 📊 주요 기능

✅ **완전 자동화**
- 코드 푸시 → 자동 배포 → 헬스 체크

✅ **안전한 배포**
- Systemd를 통한 안정적인 서비스 관리
- 배포 실패 시 자동 롤백 (로그 출력)

✅ **쉬운 관리**
- 원클릭 초기 설정 스크립트
- 자동 테스트 스크립트
- 상세한 문서

✅ **프로덕션 준비**
- 환경 변수 보안 관리 (GitHub Secrets)
- 서비스 자동 재시작
- 로그 모니터링

## 🎯 사용 방법

### 일상적인 개발 워크플로우
1. 코드 수정
2. Git 커밋 & 푸시
3. GitHub Actions가 자동 배포 (1-2분)
4. 완료!

### 서비스 관리
```bash
# 상태 확인
sudo systemctl status rag-api

# 재시작
sudo systemctl restart rag-api

# 로그 확인
sudo journalctl -u rag-api -f
```

### 배포 테스트
```bash
# 로컬에서
bash scripts/test_deployment.sh <EC2_IP> 8000

# EC2에서
bash scripts/test_deployment.sh localhost 8000
```

## 📚 문서 가이드

어디서부터 시작할지 모르겠다면:

1. **처음 시작**: `CICD_SETUP_GUIDE.md` 읽기
2. **빠른 실행**: `QUICKSTART.md` 따라하기
3. **상세 정보**: `DEPLOYMENT.md` 참고

## 🎉 완료!

이제 main 브랜치에 푸시할 때마다 자동으로 EC2에 배포됩니다!

배포 프로세스:
```
코드 푸시 → GitHub Actions 트리거 → EC2 SSH 연결
→ Git Pull → 의존성 설치 → 환경 변수 업데이트
→ 서비스 재시작 → 헬스 체크 → 완료! ✨
```

