# 🔧 배포 문제 해결 가이드

## 문제: SSH 연결 타임아웃

### 증상
```
dial tcp 13.125.247.202:22: i/o timeout
```

### 해결 방법

#### 1. EC2 보안 그룹 설정 확인

**AWS 콘솔에서:**

1. **EC2 대시보드** → **인스턴스** 선택
2. 인스턴스 클릭 → **보안** 탭 → **보안 그룹** 클릭
3. **인바운드 규칙** 확인

**필수 규칙:**
- **SSH (포트 22)**:
  - 소스: `0.0.0.0/0` (모든 IP 허용) 또는
  - 소스: GitHub Actions IP 범위 (권장)

**GitHub Actions IP 범위:**
```
# GitHub Actions IP는 동적이므로, 다음 중 하나 선택:

# 옵션 1: 모든 IP 허용 (개발용, 보안 위험)
소스: 0.0.0.0/0

# 옵션 2: 특정 IP만 허용 (권장)
# GitHub Actions IP 확인: https://api.github.com/meta
# 또는 GitHub Actions 로그에서 확인 가능
```

**인바운드 규칙 추가:**
1. **인바운드 규칙 편집** 클릭
2. **규칙 추가** 클릭
3. 설정:
   - **유형**: SSH
   - **프로토콜**: TCP
   - **포트**: 22
   - **소스**: `0.0.0.0/0` (임시) 또는 특정 IP
4. **규칙 저장** 클릭

#### 2. EC2 인스턴스 상태 확인

```bash
# AWS 콘솔에서 확인
- 인스턴스 상태: running
- 상태 확인: 2/2 checks passed
```

#### 3. SSH 키 확인

**로컬에서 SSH 테스트:**
```bash
# SSH 키로 직접 연결 테스트
ssh -i your-key.pem ubuntu@13.125.247.202

# 연결이 안 되면:
# 1. SSH 키 파일 권한 확인: chmod 400 your-key.pem
# 2. EC2 인스턴스가 실행 중인지 확인
# 3. 보안 그룹 규칙 확인
```

#### 4. GitHub Secrets 확인

**GitHub 저장소 → Settings → Secrets and variables → Actions**

다음 Secrets가 올바르게 설정되어 있는지 확인:

- [ ] `EC2_HOST`: `13.125.247.202` (또는 도메인)
- [ ] `EC2_USER`: `ubuntu`
- [ ] `EC2_SSH_KEY`: SSH 프라이빗 키 전체 내용 (BEGIN/END 포함)
- [ ] `POSTGRES_CONNECTION_STRING`: 실제 연결 문자열
- [ ] `OPENAI_API_KEY`: 실제 API 키
- [ ] `LLM_PROVIDER`: `openai` 또는 `midm`

**SSH 키 복사 방법:**
```bash
# Windows PowerShell
Get-Content ~\.ssh\your-key.pem | Set-Clipboard

# macOS/Linux
cat ~/.ssh/your-key.pem | pbcopy  # macOS
cat ~/.ssh/your-key.pem           # Linux (수동 복사)
```

**중요:** SSH 키는 다음 형식이어야 합니다:
```
-----BEGIN RSA PRIVATE KEY-----
(키 내용)
-----END RSA PRIVATE KEY-----
```

#### 5. 워크플로우 타임아웃 설정 증가

워크플로우 파일에 타임아웃 설정 추가:

