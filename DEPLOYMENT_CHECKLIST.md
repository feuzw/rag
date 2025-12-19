# ✅ EC2 배포 체크리스트 (`/home/ubuntu/rag-app`)

FastAPI RAG 애플리케이션을 `/home/ubuntu/rag-app`에 배포하는 단계별 체크리스트입니다.

## 📍 배포 위치
**`/home/ubuntu/rag-app`** (또는 `~/rag-app`)

---

## 🔧 1단계: EC2 초기 설정

### EC2 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

- [ ] EC2 인스턴스 접속 성공

### 저장소 클론
```bash
cd ~
git clone <YOUR_GITHUB_REPO_URL> rag-app
cd rag-app
```

- [ ] 저장소 클론 완료
- [ ] `~/rag-app` 디렉토리 확인

### 초기 설정 스크립트 실행
```bash
chmod +x scripts/setup_ec2.sh
bash scripts/setup_ec2.sh
```

- [ ] 초기 설정 스크립트 실행 완료
- [ ] 시스템 패키지 업데이트 완료
- [ ] 필수 패키지 설치 완료 (python3-pip, python3-venv, git, curl)

---

## 🔐 2단계: 환경 변수 설정

### .env 파일 편집
```bash
cd ~/rag-app
nano .env
```

다음 값들을 실제 값으로 변경:

- [ ] `POSTGRES_CONNECTION_STRING` 설정
- [ ] `OPENAI_API_KEY` 설정
- [ ] `LLM_PROVIDER` 설정 (openai 또는 midm)
- [ ] `HOST=0.0.0.0` 확인
- [ ] `PORT=8000` 확인

저장: `Ctrl + O` → `Enter` → `Ctrl + X`

---

## 🐍 3단계: Python 환경 설정

### 가상환경 생성 및 의존성 설치
```bash
cd ~/rag-app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
```

- [ ] 가상환경 생성 완료 (`~/rag-app/venv`)
- [ ] 의존성 설치 완료 (에러 없음)
- [ ] 가상환경 활성화 확인

---

## 🧪 4단계: 수동 테스트

### 서버 수동 실행
```bash
cd ~/rag-app
source venv/bin/activate
python app/main.py
```

다른 터미널에서 테스트:
```bash
curl http://localhost:8000/health
```

- [ ] 서버 수동 실행 성공
- [ ] 헬스 체크 응답 확인 (`{"status":"healthy"}`)
- [ ] `Ctrl + C`로 서버 종료

---

## ⚙️ 5단계: Systemd 서비스 설정

### 서비스 설정 스크립트 실행
```bash
cd ~/rag-app
chmod +x scripts/setup_systemd.sh
bash scripts/setup_systemd.sh
```

- [ ] Systemd 서비스 파일 생성 완료
- [ ] 서비스 활성화 완료 (`enable`)
- [ ] 서비스 시작 완료 (`start`)
- [ ] 서비스 상태 확인 (`active (running)`)

### 서비스 상태 확인
```bash
sudo systemctl status rag-api
```

- [ ] 서비스가 `active (running)` 상태
- [ ] 에러 메시지 없음

---

## 🔑 6단계: GitHub Secrets 설정

GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**

다음 6개 Secret 추가:

- [ ] `EC2_HOST` - EC2 Public IP 또는 도메인
- [ ] `EC2_USER` - `ubuntu`
- [ ] `EC2_SSH_KEY` - SSH 프라이빗 키 전체 내용 (BEGIN/END 포함)
- [ ] `POSTGRES_CONNECTION_STRING` - PostgreSQL 연결 문자열
- [ ] `OPENAI_API_KEY` - OpenAI API 키
- [ ] `LLM_PROVIDER` - `openai` 또는 `midm`

---

## 🚀 7단계: 첫 배포 테스트

### 방법 1: GitHub Actions 수동 실행

1. GitHub 저장소 → **Actions** 탭
2. **"Deploy to EC2"** 워크플로우 선택
3. **"Run workflow"** 버튼 클릭
4. 브랜치 선택 (main) → **"Run workflow"** 확인

- [ ] 워크플로우 실행 시작
- [ ] 모든 단계 성공 (녹색 체크마크)
- [ ] "✅ 배포 성공!" 메시지 확인

### 방법 2: 코드 푸시로 자동 배포

```bash
# 로컬에서
git add .
git commit -m "Initial deployment setup"
git push origin main
```

- [ ] 코드 푸시 완료
- [ ] GitHub Actions 자동 실행 확인
- [ ] 배포 성공 확인

---

## ✅ 8단계: 배포 확인

### API 엔드포인트 테스트

```bash
# 헬스 체크
curl http://your-ec2-ip:8000/health

# 루트 엔드포인트
curl http://your-ec2-ip:8000/

# API 문서 (브라우저)
http://your-ec2-ip:8000/docs
```

- [ ] 헬스 체크 성공 (`{"status":"healthy"}`)
- [ ] 루트 엔드포인트 응답 확인
- [ ] API 문서 접근 가능

### EC2 서버에서 확인

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 서비스 상태
sudo systemctl status rag-api

# 실시간 로그
sudo journalctl -u rag-api -f

# 최근 50줄 로그
sudo journalctl -u rag-api -n 50
```

- [ ] 서비스가 정상 실행 중
- [ ] 로그에 에러 없음
- [ ] "FastAPI 서버 준비 완료!" 메시지 확인

---

## 📊 9단계: 디렉토리 구조 확인

```bash
cd ~/rag-app
ls -la
```

예상 구조:
```
~/rag-app/
├── app/
│   ├── api_server.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── venv/
├── .env
├── .git/
└── scripts/
```

- [ ] 디렉토리 구조 확인
- [ ] 모든 필수 파일 존재
- [ ] `.env` 파일 권한 확인 (`chmod 600 .env` 권장)

---

## 🔄 10단계: 자동 배포 검증

### 코드 변경 테스트

```bash
# 로컬에서 간단한 변경
echo "# Test" >> README.md

# 커밋 및 푸시
git add README.md
git commit -m "test: verify auto deployment"
git push origin main
```

- [ ] 코드 변경 후 푸시
- [ ] GitHub Actions 자동 실행 확인
- [ ] EC2에서 변경사항 반영 확인
- [ ] 서비스 재시작 확인
- [ ] 헬스 체크 통과

---

## 🎉 배포 완료!

모든 체크리스트 항목이 완료되었다면 배포가 성공적으로 완료된 것입니다!

### 배포 정보 요약

- **배포 위치**: `/home/ubuntu/rag-app`
- **서비스 이름**: `rag-api`
- **포트**: `8000`
- **API URL**: `http://your-ec2-ip:8000`
- **API 문서**: `http://your-ec2-ip:8000/docs`

### 유용한 명령어

```bash
# 서비스 관리
sudo systemctl status rag-api    # 상태 확인
sudo systemctl restart rag-api   # 재시작
sudo systemctl stop rag-api      # 중지
sudo systemctl start rag-api     # 시작

# 로그 확인
sudo journalctl -u rag-api -f         # 실시간 로그
sudo journalctl -u rag-api -n 100     # 최근 100줄
sudo journalctl -u rag-api --since today  # 오늘 로그

# 디렉토리 확인
cd ~/rag-app
ls -la
```

---

## 🆘 문제 해결

### 배포 실패 시

1. **GitHub Actions 로그 확인**
   - GitHub → Actions → 실패한 워크플로우 클릭

2. **EC2 서비스 로그 확인**
   ```bash
   sudo journalctl -u rag-api -n 100
   ```

3. **환경 변수 확인**
   ```bash
   cat ~/rag-app/.env
   ```

4. **수동 실행으로 디버깅**
   ```bash
   cd ~/rag-app
   source venv/bin/activate
   python app/main.py
   ```

### 일반적인 문제

| 문제 | 해결 방법 |
|------|----------|
| SSH 연결 실패 | `EC2_SSH_KEY` Secret 확인 (BEGIN/END 포함) |
| 서비스 시작 실패 | `.env` 파일 및 환경 변수 확인 |
| 포트 충돌 | `sudo lsof -i :8000` 확인 |
| PostgreSQL 연결 실패 | 연결 문자열 및 IP 화이트리스트 확인 |

---

**배포를 축하합니다! 🎊**

이제 `main` 브랜치에 푸시할 때마다 자동으로 EC2에 배포됩니다! 🚀

