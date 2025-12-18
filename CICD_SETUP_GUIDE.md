# CI/CD 설정 완료 가이드

## ✅ 생성된 파일 목록

### GitHub Actions
- `.github/workflows/deploy.yml` - 자동 배포 워크플로우

### 스크립트
- `scripts/setup_ec2.sh` - EC2 초기 설정 자동화
- `scripts/setup_systemd.sh` - Systemd 서비스 자동 설정
- `scripts/test_deployment.sh` - 배포 테스트 자동화

### 문서
- `DEPLOYMENT.md` - 전체 배포 전략 문서
- `QUICKSTART.md` - 빠른 시작 가이드
- `env.template` - 환경 변수 템플릿

## 🚀 배포 시작하기 (3단계)

### 1단계: GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions에서 추가:

| Secret 이름 | 설명 | 예시 |
|------------|------|------|
| `EC2_HOST` | EC2 퍼블릭 IP 또는 도메인 | `54.123.45.67` |
| `EC2_USER` | SSH 사용자명 | `ubuntu` |
| `EC2_SSH_KEY` | SSH 프라이빗 키 (PEM 파일 전체 내용) | `-----BEGIN RSA PRIVATE KEY-----...` |
| `POSTGRES_CONNECTION_STRING` | PostgreSQL 연결 문자열 | `postgresql://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | OpenAI API 키 | `sk-proj-...` |
| `LLM_PROVIDER` | LLM 제공자 | `openai` 또는 `midm` |

### 2단계: EC2 초기 설정

SSH로 EC2 접속 후:

```bash
# 1. 저장소 클론
git clone <YOUR_GITHUB_REPO_URL> ~/rag-app
cd ~/rag-app

# 2. 자동 설정 실행
bash scripts/setup_ec2.sh

# 3. 환경 변수 설정
cp env.template .env
nano .env  # 실제 값 입력

# 4. Systemd 서비스 설정
bash scripts/setup_systemd.sh

# 5. 배포 테스트
bash scripts/test_deployment.sh localhost 8000
```

### 3단계: 자동 배포 확인

```bash
# 로컬에서 변경사항 푸시
git add .
git commit -m "Initial deployment setup"
git push origin main
```

GitHub Actions 탭에서 배포 진행 상황을 확인하세요!

## 📊 배포 확인 방법

### 로컬에서 EC2 테스트
```bash
bash scripts/test_deployment.sh <EC2_IP> 8000
```

### EC2 서비스 상태 확인
```bash
sudo systemctl status rag-api
sudo journalctl -u rag-api -f
```

### API 직접 테스트
```bash
curl http://<EC2_IP>:8000/health
curl http://<EC2_IP>:8000/docs
```

## 🔄 일상적인 배포 프로세스

1. 코드 변경
2. Git 커밋 및 푸시
   ```bash
   git add .
   git commit -m "Feature: Add new functionality"
   git push origin main
   ```
3. GitHub Actions가 자동으로 배포 실행
4. 배포 완료 확인 (약 1-2분 소요)

## 🛠️ 유용한 명령어

### 서비스 관리
```bash
sudo systemctl status rag-api    # 상태 확인
sudo systemctl restart rag-api   # 재시작
sudo systemctl stop rag-api      # 중지
sudo systemctl start rag-api     # 시작
```

### 로그 확인
```bash
sudo journalctl -u rag-api -f         # 실시간 로그
sudo journalctl -u rag-api -n 100     # 최근 100줄
sudo journalctl -u rag-api --since today  # 오늘 로그
```

### 수동 배포
GitHub → Actions → Deploy to EC2 → Run workflow

## ⚠️ 문제 해결

### 배포 실패 시

1. **GitHub Actions 로그 확인**
   - Repository → Actions → 실패한 워크플로우 클릭

2. **EC2 서비스 로그 확인**
   ```bash
   sudo journalctl -u rag-api -n 50
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

### SSH 연결 실패
- EC2 보안 그룹에서 22번 포트 오픈 확인
- SSH 키가 올바른지 확인
- EC2 인스턴스가 실행 중인지 확인

### 서비스 시작 실패
- PostgreSQL 연결 문자열 확인
- API 키 유효성 확인
- 포트 충돌 확인: `sudo lsof -i :8000`

## 📚 추가 문서

- [DEPLOYMENT.md](DEPLOYMENT.md) - 상세한 배포 전략
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드

## 🎉 완료!

이제 `main` 브랜치에 푸시할 때마다 자동으로 EC2에 배포됩니다!

