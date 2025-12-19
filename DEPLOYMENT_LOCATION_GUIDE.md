# 📁 EC2 배포 위치 가이드

FastAPI RAG 애플리케이션을 EC2에 배포할 때 최적의 디렉토리 위치를 선택하는 가이드입니다.

## 🎯 배포 위치 옵션

### 1. `/opt/rag-app` ⭐ **프로덕션 권장**

**장점:**
- ✅ Linux Filesystem Hierarchy Standard (FHS) 준수
- ✅ 서드파티 소프트웨어 표준 위치
- ✅ 시스템 업데이트와 분리
- ✅ 프로덕션 환경에 적합
- ✅ 명확한 애플리케이션 관리

**단점:**
- ⚠️ sudo 권한 필요
- ⚠️ 소유권 설정 필요

**사용 시나리오:**
- 프로덕션 배포
- 장기 운영
- 여러 사용자 환경

### 2. `/home/ubuntu/rag-app` (현재 기본값)

**장점:**
- ✅ 설정 간단 (권한 문제 적음)
- ✅ 개발/테스트에 적합
- ✅ 기존 스크립트와 호환

**단점:**
- ⚠️ 프로덕션에는 부적합
- ⚠️ 사용자 홈 디렉토리라 관리가 불명확
- ⚠️ 시스템 재설치 시 삭제 가능

**사용 시나리오:**
- 개발/테스트 환경
- 빠른 프로토타이핑
- 개인 프로젝트

### 3. `/srv/rag-app` (대안)

**장점:**
- ✅ 서비스 데이터용 표준 위치
- ✅ 웹 서비스에 적합
- ✅ 시스템 구조상 명확

**단점:**
- ⚠️ `/opt`보다 덜 일반적

**사용 시나리오:**
- 웹 서비스 중심 배포
- 서비스 데이터 관리

## 🚀 권장 전략

### 프로덕션 배포: `/opt/rag-app` 사용

프로덕션 환경에서는 `/opt/rag-app`을 강력히 권장합니다.

## 📋 배포 방법

### 방법 1: 프로덕션 배포 (`/opt/rag-app`)

#### 1단계: EC2 초기 설정

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 프로덕션 초기 설정 스크립트 실행
git clone <YOUR_REPO_URL> /tmp/rag-temp
cd /tmp/rag-temp
chmod +x scripts/setup_ec2_production.sh
bash scripts/setup_ec2_production.sh

# 저장소 클론
sudo git clone <YOUR_REPO_URL> /opt/rag-app
sudo chown -R $USER:$USER /opt/rag-app
cd /opt/rag-app

# 환경 변수 설정
nano .env  # 실제 값 입력
```

#### 2단계: Systemd 서비스 설정

```bash
cd /opt/rag-app
chmod +x scripts/setup_systemd_production.sh
bash scripts/setup_systemd_production.sh
```

#### 3단계: GitHub Actions 워크플로우 설정

`.github/workflows/deploy.yml`을 `.github/workflows/deploy-production.yml`로 교체하거나, 기존 파일을 수정:

```yaml
# deploy.yml에서
cd ~/rag-app  # 이 부분을
cd /opt/rag-app  # 이렇게 변경
```

#### 4단계: 배포 테스트

```bash
# 서비스 상태 확인
sudo systemctl status rag-api

# 헬스 체크
curl http://localhost:8000/health

# 로그 확인
sudo journalctl -u rag-api -f
```

### 방법 2: 개발/테스트 배포 (`~/rag-app`)

기존 스크립트를 그대로 사용:

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 기존 초기 설정 스크립트 실행
git clone <YOUR_REPO_URL> ~/rag-app
cd ~/rag-app
bash scripts/setup_ec2.sh
bash scripts/setup_systemd.sh
```

## 🔄 기존 배포에서 마이그레이션

`~/rag-app`에서 `/opt/rag-app`으로 마이그레이션하는 방법:

```bash
# 1. 기존 서비스 중지
sudo systemctl stop rag-api
sudo systemctl disable rag-api

# 2. 데이터 백업
sudo cp -r ~/rag-app /tmp/rag-app-backup

# 3. /opt로 이동
sudo mkdir -p /opt/rag-app
sudo cp -r ~/rag-app/* /opt/rag-app/
sudo chown -R $USER:$USER /opt/rag-app

# 4. Systemd 서비스 재설정
cd /opt/rag-app
bash scripts/setup_systemd_production.sh

# 5. 서비스 시작 및 확인
sudo systemctl start rag-api
sudo systemctl status rag-api

# 6. (선택) 기존 디렉토리 삭제
# rm -rf ~/rag-app
```

## 📊 디렉토리 구조 비교

### `/opt/rag-app` 구조

```
/opt/
└── rag-app/
    ├── app/
    │   ├── api_server.py
    │   ├── main.py
    │   └── ...
    ├── venv/
    ├── .env
    ├── .git/
    └── requirements.txt
```

### `~/rag-app` 구조

```
/home/ubuntu/
└── rag-app/
    ├── app/
    ├── venv/
    ├── .env
    └── ...
```

## 🔒 보안 고려사항

### `/opt/rag-app` 사용 시

```bash
# 디렉토리 권한 설정
sudo chown -R ubuntu:ubuntu /opt/rag-app
sudo chmod 755 /opt/rag-app

# .env 파일 보안
chmod 600 /opt/rag-app/.env

# 가상환경 권한
chmod -R 755 /opt/rag-app/venv
```

### Systemd 서비스 보안

```ini
[Service]
User=ubuntu
Group=ubuntu
NoNewPrivileges=true
PrivateTmp=true
```

## 📝 체크리스트

### 프로덕션 배포 (`/opt/rag-app`)

- [ ] `/opt/rag-app` 디렉토리 생성
- [ ] 소유권 설정 (`chown -R ubuntu:ubuntu /opt/rag-app`)
- [ ] 코드 클론 또는 이동
- [ ] 환경 변수 설정 (`.env` 파일)
- [ ] Systemd 서비스 설정
- [ ] GitHub Actions 워크플로우 경로 업데이트
- [ ] 서비스 시작 및 테스트
- [ ] 헬스 체크 확인

### 개발/테스트 배포 (`~/rag-app`)

- [ ] `~/rag-app` 디렉토리 생성
- [ ] 코드 클론
- [ ] 환경 변수 설정
- [ ] Systemd 서비스 설정
- [ ] 서비스 시작 및 테스트

## 🎯 최종 권장사항

### 프로덕션 환경
👉 **`/opt/rag-app` 사용**

이유:
- 표준 Linux 배포 관행 준수
- 시스템 업데이트와 분리
- 명확한 애플리케이션 관리
- 장기 운영에 적합

### 개발/테스트 환경
👉 **`~/rag-app` 사용**

이유:
- 빠른 설정
- 권한 문제 적음
- 개발 편의성

## 📚 참고 자료

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.html)
- [Systemd Service 파일 작성 가이드](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**프로덕션 배포를 권장합니다! `/opt/rag-app`을 사용하세요.** 🚀

