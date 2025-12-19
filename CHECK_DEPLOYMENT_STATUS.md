# 🔍 EC2 배포 상태 확인 가이드

## 현재 상황 분석

GitHub Actions 페이지에서:
- ✅ `.github/workflows/deploy.yml` 파일 존재
- ✅ `.github/workflows/deploy-production.yml` 파일 존재
- ❓ 최근 "Deploy to EC2" 실행 기록이 보이지 않음

## 확인 방법

### 1. 워크플로우 실행 기록 확인

**GitHub Actions 페이지에서:**

1. 왼쪽 사이드바에서 **"Deploy to EC2"** 클릭
   - 또는 `.github/workflows/deploy.yml` 클릭

2. 최근 실행 기록 확인
   - 실행 기록이 있으면 → 연결 문제
   - 실행 기록이 없으면 → 트리거 문제

### 2. 수동 실행 테스트

**워크플로우 수동 실행:**

1. GitHub → **Actions** 탭
2. 왼쪽에서 **"Deploy to EC2"** 선택
3. 오른쪽 상단 **"Run workflow"** 버튼 클릭
4. 브랜치 선택 (main) → **"Run workflow"** 확인

**결과 확인:**
- ✅ 실행 시작 → 연결 시도 중
- ❌ 실행 안 됨 → 워크플로우 파일 문제
- ⏱️ 타임아웃 → 보안 그룹 문제

### 3. GitHub Secrets 확인

**GitHub 저장소 → Settings → Secrets and variables → Actions**

다음 Secrets 확인:

- [ ] `EC2_HOST` - 설정되어 있음
- [ ] `EC2_USER` - 설정되어 있음
- [ ] `EC2_SSH_KEY` - 설정되어 있음
- [ ] `POSTGRES_CONNECTION_STRING` - 설정되어 있음
- [ ] `OPENAI_API_KEY` - 설정되어 있음
- [ ] `LLM_PROVIDER` - 설정되어 있음 (선택사항)

**Secrets가 없으면:**
- 워크플로우가 실행되지 않을 수 있음
- 또는 실행되지만 환경 변수가 비어있음

### 4. 최근 커밋 확인

**로컬에서:**
```bash
git log --oneline -5
```

**main 브랜치에 최근 푸시가 있었는지 확인:**
- 푸시가 있었는데 워크플로우가 실행 안 됨 → 트리거 문제
- 푸시가 없음 → 정상 (워크플로우는 push 시 자동 실행)

### 5. EC2 직접 연결 테스트

**로컬에서 SSH 테스트:**
```bash
ssh -i your-key.pem ubuntu@13.125.247.202
```

**결과:**
- ✅ 연결 성공 → EC2는 정상, GitHub Actions 설정 문제
- ❌ 연결 실패 → EC2 또는 보안 그룹 문제

---

## 문제 진단 체크리스트

### 시나리오 1: 워크플로우가 실행되지 않음

**증상:**
- GitHub Actions에 실행 기록이 없음
- "Run workflow" 버튼이 작동하지 않음

**가능한 원인:**
1. 워크플로우 파일 문법 오류
2. GitHub Actions 비활성화
3. 브랜치 보호 규칙

**해결:**
1. 워크플로우 파일 문법 확인
2. Settings → Actions → General에서 Actions 활성화 확인
3. 브랜치 보호 규칙 확인

### 시나리오 2: 워크플로우 실행되지만 실패

**증상:**
- 워크플로우가 실행됨
- "Deploy to EC2" 단계에서 실패

**가능한 원인:**
1. SSH 연결 타임아웃 (보안 그룹)
2. GitHub Secrets 누락
3. EC2 인스턴스 문제

**해결:**
1. 보안 그룹 SSH 규칙 확인 (0.0.0.0/0)
2. GitHub Secrets 확인
3. EC2 인스턴스 상태 확인

### 시나리오 3: 워크플로우 실행되지만 환경 변수 비어있음

**증상:**
- 워크플로우 실행됨
- 로그에 `POSTGRES_CONNECTION_STRING=`, `OPENAI_API_KEY=` (비어있음)

**가능한 원인:**
1. GitHub Secrets 미설정
2. Secrets 이름 오타

**해결:**
1. GitHub Secrets 확인 및 재설정
2. Secrets 이름 정확히 확인

---

## 빠른 확인 방법

### 1단계: 워크플로우 수동 실행

```
GitHub → Actions → Deploy to EC2 → Run workflow
```

### 2단계: 실행 로그 확인

실행이 시작되면:
1. 실행 클릭
2. "Deploy to EC2" 단계 클릭
3. 로그 확인

**예상 로그:**
- `dial tcp ...:22: i/o timeout` → 보안 그룹 문제
- `Permission denied` → SSH 키 문제
- `POSTGRES_CONNECTION_STRING=` → Secrets 문제

### 3단계: 문제별 해결

**타임아웃:**
- 보안 그룹 → SSH 규칙 → 소스를 `0.0.0.0/0`으로 변경

**Permission denied:**
- GitHub Secrets의 `EC2_SSH_KEY` 확인 (전체 키, BEGIN/END 포함)

**환경 변수 비어있음:**
- GitHub Secrets 모두 확인 및 재설정

---

## 다음 단계

1. **워크플로우 수동 실행** 시도
2. **실행 로그 확인**
3. **에러 메시지에 따라 해결**

워크플로우가 실행되지 않으면 → 워크플로우 파일 문제
워크플로우가 실행되지만 실패하면 → 연결 또는 Secrets 문제

