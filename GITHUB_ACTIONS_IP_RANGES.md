# GitHub Actions IP 범위 설정 가이드

## GitHub Actions IP 범위

GitHub Actions는 동적 IP를 사용하므로, 특정 IP만 허용하면 연결이 실패할 수 있습니다.

### 옵션 1: 모든 IP 허용 (개발용)

**보안 그룹 설정:**
- 소스: `0.0.0.0/0` (모든 IPv4 주소)

⚠️ **주의**: 보안상 위험하므로 개발 환경에서만 사용

### 옵션 2: GitHub Actions IP 범위 추가 (권장)

GitHub Actions IP 범위는 다음 API로 확인 가능:
```
https://api.github.com/meta
```

**주요 IP 범위:**
- GitHub Actions는 여러 IP 범위를 사용
- 정확한 범위는 GitHub API에서 확인 필요

**보안 그룹 설정:**
1. 기존 SSH 규칙 유지 (My IP)
2. 새로운 SSH 규칙 추가:
   - 소스: `0.0.0.0/0` (임시, 개발용)
   - 또는 GitHub Actions IP 범위 추가

### 옵션 3: Elastic IP 사용 (프로덕션)

프로덕션 환경에서는:
1. EC2에 Elastic IP 할당
2. 보안 그룹에서 특정 IP만 허용
3. GitHub Actions IP 범위만 추가

## 빠른 해결 (개발용)

**지금 바로 해결하려면:**

1. AWS 콘솔 → EC2 → 보안 그룹
2. SSH 규칙 편집
3. 소스를 "My IP"에서 **"Anywhere-IPv4"** (`0.0.0.0/0`)로 변경
4. 저장

이렇게 하면 GitHub Actions에서 연결 가능합니다.

⚠️ **보안 주의**: 프로덕션 환경에서는 특정 IP만 허용하는 것이 좋습니다.

