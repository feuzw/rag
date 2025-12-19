# 🔒 EC2 보안 그룹 설정 가이드

## 현재 상황

- **현재 설정**: "My IP" (`221.148.97.238/32`)만 허용
- **문제**: GitHub Actions는 다른 IP에서 실행되므로 연결 불가

## 해결 방법

### 옵션 1: GitHub Actions IP 범위 추가 (권장) ⭐

**"My IP"는 유지하고, GitHub Actions IP만 추가 허용**

#### 단계별 설정:

1. **AWS 콘솔** → **EC2** → **보안 그룹**
2. 현재 보안 그룹 선택
3. **인바운드 규칙** → **인바운드 규칙 편집**
4. **규칙 추가** 클릭

**새 규칙 추가:**
- **유형**: SSH
- **프로토콜**: TCP
- **포트**: 22
- **소스**: **사용자 지정**
- **IP 주소**: GitHub Actions IP 범위 입력

#### GitHub Actions IP 범위 확인 방법:

**방법 1: GitHub API 사용**
```bash
curl https://api.github.com/meta | grep actions
```

**방법 2: GitHub Actions IP 범위 (일반적인 범위)**
```
# GitHub Actions는 여러 IP 범위를 사용하므로, 다음 중 하나 선택:

# 옵션 A: GitHub Actions IP 범위만 추가 (보안 강화)
# GitHub API에서 확인한 IP 범위 추가

# 옵션 B: GitHub Actions가 사용하는 주요 IP 범위
# (정확한 범위는 GitHub API로 확인 필요)
```

**방법 3: 간단한 해결 (개발용)**
- 소스: `0.0.0.0/0` (모든 IP 허용)
- ⚠️ 보안상 위험하지만 개발 환경에서는 사용 가능

#### 최종 보안 그룹 규칙:

| 규칙 | 소스 | 설명 |
|------|------|------|
| SSH (My IP) | `221.148.97.238/32` | 본인 IP (기존 유지) |
| SSH (GitHub Actions) | `0.0.0.0/0` 또는 특정 IP 범위 | GitHub Actions용 |

---

### 옵션 2: 수동 배포만 사용 (가장 안전)

**GitHub Actions를 사용하지 않고, 로컬에서 직접 배포**

#### 장점:
- ✅ 보안 그룹 변경 불필요
- ✅ "My IP"만 허용 유지
- ✅ 가장 안전한 방법

#### 단점:
- ❌ 자동 배포 불가
- ❌ 수동으로 배포해야 함

#### 수동 배포 방법:

```bash
# 로컬에서
ssh -i your-key.pem ubuntu@your-ec2-ip

# EC2에서
cd ~/rag-app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rag-api
```

---

### 옵션 3: 조건부 보안 그룹 변경

**배포 시에만 임시로 Anywhere-IPv4 허용, 배포 후 다시 제한**

#### 자동화 스크립트 예시:

```bash
#!/bin/bash
# 배포 전 보안 그룹 변경
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# 배포 실행
# ... (GitHub Actions 또는 수동 배포)

# 배포 후 보안 그룹 제한
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

⚠️ 복잡하고 실수 위험이 있음

---

## 🎯 권장사항

### 개발 환경
👉 **옵션 1 (GitHub Actions IP 추가)** 또는 **임시로 0.0.0.0/0**

이유:
- 자동 배포 편의성
- 개발 환경이므로 보안 요구사항이 낮음

### 프로덕션 환경
👉 **옵션 2 (수동 배포)** 또는 **GitHub Actions IP 범위만 정확히 추가**

이유:
- 보안 강화
- 제어된 배포 프로세스

---

## 📋 빠른 해결 (지금 바로)

### 개발 환경이라면:

1. **보안 그룹** → **인바운드 규칙 편집**
2. **규칙 추가**:
   - 유형: SSH
   - 포트: 22
   - 소스: `0.0.0.0/0` (임시, 개발용)
3. **규칙 저장**

⚠️ **주의**: 프로덕션에서는 사용하지 마세요!

### 프로덕션 환경이라면:

**옵션 2 (수동 배포)**를 사용하거나, GitHub Actions IP 범위만 정확히 추가하세요.

---

## 🔍 GitHub Actions IP 범위 확인

### API로 확인:

```bash
# GitHub Actions IP 범위 확인
curl https://api.github.com/meta | grep -A 10 actions
```

### 웹에서 확인:

1. https://api.github.com/meta 접속
2. `actions` 섹션의 IP 범위 확인
3. 각 IP 범위를 보안 그룹에 추가

---

## ✅ 체크리스트

- [ ] 현재 보안 그룹 설정 확인 ("My IP" 유지)
- [ ] 개발/프로덕션 환경 결정
- [ ] 옵션 선택:
  - [ ] 옵션 1: GitHub Actions IP 추가
  - [ ] 옵션 2: 수동 배포만 사용
  - [ ] 옵션 3: 임시로 0.0.0.0/0 (개발용)
- [ ] 보안 그룹 규칙 적용
- [ ] GitHub Actions 테스트 (옵션 1 선택 시)

---

**결론: "My IP"는 유지하고, GitHub Actions IP만 추가로 허용하는 것이 가장 좋습니다!** 🔒

