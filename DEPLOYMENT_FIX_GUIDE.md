# 🔧 배포 오류 해결 가이드

## 현재 발생한 문제

### 1. SSH 연결 타임아웃
```
dial tcp 13.125.247.202:22: i/o timeout
```

### 2. 환경 변수 비어있음
```
POSTGRES_CONNECTION_STRING=
OPENAI_API_KEY=
```

---

## ✅ 해결 방법 (단계별)

### 🔴 1단계: EC2 보안 그룹 설정 (가장 중요!)

**AWS 콘솔에서:**

1. **EC2 대시보드** → 인스턴스 선택
2. **보안** 탭 → **보안 그룹** 클릭
3. **인바운드 규칙** → **인바운드 규칙 편집**

**SSH 규칙 추가:**
- **유형**: SSH
- **프로토콜**: TCP
- **포트**: 22
- **소스**: `0.0.0.0/0` (모든 IP 허용 - 개발용)
  - ⚠️ 프로덕션에서는 특정 IP만 허용 권장

**규칙 저장** 클릭

### 🔴 2단계: GitHub Secrets 확인

**GitHub 저장소 → Settings → Secrets and variables → Actions**

다음 6개 Secret이 모두 설정되어 있는지 확인:

#### 필수 Secrets 체크리스트:

- [ ] **`EC2_HOST`**
  - 값: `13.125.247.202` (또는 도메인)
  - 형식: IP 주소 또는 도메인 (포트 없음)

- [ ] **`EC2_USER`**
  - 값: `ubuntu`
  - 형식: 사용자 이름만

- [ ] **`EC2_SSH_KEY`** ⚠️ 가장 중요!
  - 값: SSH 프라이빗 키 **전체 내용**
  - 형식:
    ```
    -----BEGIN RSA PRIVATE KEY-----
    (키 내용 여러 줄)
    -----END RSA PRIVATE KEY-----
    ```
  - 복사 방법:
    ```bash
    # Windows PowerShell
    Get-Content ~\.ssh\your-key.pem | Set-Clipboard

    # macOS
    cat ~/.ssh/your-key.pem | pbcopy
    ```

- [ ] **`POSTGRES_CONNECTION_STRING`**
  - 값: `postgresql://user:password@host:port/dbname`
  - 예시: `postgresql://user:pass@db.example.com:5432/mydb`

- [ ] **`OPENAI_API_KEY`**
  - 값: `sk-...` (실제 API 키)
  - 예시: `sk-proj-abc123...`

- [ ] **`LLM_PROVIDER`** (선택사항, 기본값: openai)
  - 값: `openai` 또는 `midm`

### 🔴 3단계: SSH 연결 테스트 (로컬에서)

로컬 컴퓨터에서 직접 SSH 연결 테스트:

```bash
# SSH 키로 직접 연결 시도
ssh -i your-key.pem ubuntu@13.125.247.202

# 연결이 성공하면:
# - 보안 그룹은 정상
# - SSH 키는 정상
# - 문제는 GitHub Actions 설정

# 연결이 실패하면:
# - 보안 그룹 확인 필요
# - SSH 키 확인 필요
# - EC2 인스턴스 상태 확인
```

### 🔴 4단계: 워크플로우 파일 업데이트

이미 업데이트된 워크플로우 파일이 있습니다:
- 타임아웃 증가 (60초 → 더 긴 시간)
- 환경 변수 처리 개선
- .env 파일 권한 설정 추가

**변경사항 커밋 및 푸시:**
```bash
git add .github/workflows/deploy.yml
git commit -m "fix: increase SSH timeout and improve env var handling"
git push origin main
```

### 🔴 5단계: GitHub Actions 재실행

1. **GitHub 저장소** → **Actions** 탭
2. 실패한 워크플로우 클릭
3. **"Re-run all jobs"** 또는 **"Re-run failed jobs"** 클릭

또는 수동 실행:
1. **Actions** → **Deploy to EC2**
2. **"Run workflow"** 클릭
3. 브랜치 선택 → **"Run workflow"**

---

## 🔍 문제 진단 체크리스트

### SSH 연결 문제

- [ ] EC2 보안 그룹에서 포트 22 인바운드 규칙 확인
- [ ] EC2 인스턴스가 `running` 상태인지 확인
- [ ] 로컬에서 SSH 연결 테스트 성공
- [ ] GitHub Secrets의 `EC2_SSH_KEY`가 올바른지 확인 (BEGIN/END 포함)
- [ ] GitHub Secrets의 `EC2_HOST`가 올바른 IP인지 확인
- [ ] GitHub Secrets의 `EC2_USER`가 `ubuntu`인지 확인

### 환경 변수 문제

- [ ] GitHub Secrets에 `POSTGRES_CONNECTION_STRING` 설정됨
- [ ] GitHub Secrets에 `OPENAI_API_KEY` 설정됨
- [ ] GitHub Secrets에 `LLM_PROVIDER` 설정됨 (또는 기본값 사용)
- [ ] Secrets 값에 공백이나 특수문자 오류 없음

---

## 🛠️ 추가 디버깅 방법

### 1. SSH 연결 상세 로그 확인

워크플로우에 디버그 모드 추가 (임시):

```yaml
- name: Deploy to EC2
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ${{ secrets.EC2_USER }}
    key: ${{ secrets.EC2_SSH_KEY }}
    port: 22
    timeout: 60s
    command_timeout: 15m
    debug: true  # 디버그 모드 추가
```

### 2. EC2에서 직접 확인

EC2에 직접 접속하여 확인:

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@13.125.247.202

# 디렉토리 확인
ls -la ~/rag-app

# 서비스 상태 확인
sudo systemctl status rag-api

# 로그 확인
sudo journalctl -u rag-api -n 50
```

### 3. GitHub Actions 로그 확인

GitHub Actions 로그에서:
- SSH 연결 시도 시간 확인
- 타임아웃 발생 시점 확인
- 에러 메시지 상세 내용 확인

---

## 📋 빠른 해결 체크리스트

가장 빠른 해결을 위한 우선순위:

1. ✅ **EC2 보안 그룹 확인** (가장 중요!)
   - SSH (포트 22) 인바운드 규칙 추가
   - 소스: `0.0.0.0/0` (개발용)

2. ✅ **GitHub Secrets 확인**
   - `EC2_SSH_KEY`가 올바른지 확인 (전체 키, BEGIN/END 포함)
   - 모든 필수 Secrets 설정 확인

3. ✅ **로컬 SSH 테스트**
   - 로컬에서 직접 SSH 연결 테스트
   - 연결 성공 시 → GitHub Actions 설정 문제
   - 연결 실패 시 → EC2/보안 그룹 문제

4. ✅ **워크플로우 재실행**
   - 수정된 워크플로우 푸시
   - GitHub Actions 재실행

---

## 🎯 예상 해결 시간

- **보안 그룹 설정**: 2분
- **GitHub Secrets 확인**: 5분
- **SSH 테스트**: 1분
- **워크플로우 재실행**: 2-3분

**총 예상 시간**: 약 10-15분

---

## 💡 예방 방법

### 1. 보안 그룹 템플릿 사용

EC2 시작 시 보안 그룹에 SSH 규칙 자동 추가

### 2. GitHub Secrets 검증

배포 전에 Secrets 값 확인:
- SSH 키 형식 확인
- 연결 문자열 형식 확인
- API 키 유효성 확인

### 3. 테스트 워크플로우

간단한 연결 테스트 워크플로우 생성:

```yaml
- name: Test SSH Connection
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.EC2_HOST }}
    username: ${{ secrets.EC2_USER }}
    key: ${{ secrets.EC2_SSH_KEY }}
    script: echo "SSH connection successful!"
```

---

## 📞 추가 도움

문제가 계속되면:

1. **GitHub Actions 로그** 전체 확인
2. **EC2 CloudWatch 로그** 확인
3. **SSH 연결 상세 로그** 확인 (`ssh -v` 옵션 사용)

---

**가장 먼저 확인할 것: EC2 보안 그룹 SSH 규칙!** 🔴

