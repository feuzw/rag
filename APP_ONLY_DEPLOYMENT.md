# 📦 app 폴더만 EC2 배포 가이드

이 가이드는 `app` 폴더만 EC2에 배포하는 방법을 설명합니다.

## 📁 배포 구조

### GitHub 저장소 구조
```
rag/
├── app/              ← 이 폴더만 배포
│   ├── api_server.py
│   ├── main.py
│   ├── requirements.txt (없으면 루트의 requirements.txt 사용)
│   └── ...
├── requirements.txt
└── ...
```

### EC2 배포 구조
```
~/rag-app/            ← app 폴더의 내용이 여기에 직접 배포됨
├── api_server.py
├── main.py
├── requirements.txt
├── venv/
├── .env
└── ...
```

## 🔧 주요 변경사항

### 1. GitHub Actions 워크플로우

`.github/workflows/deploy.yml`이 수정되었습니다:

- ✅ `app` 폴더의 내용만 `~/rag-app`에 배포
- ✅ `requirements.txt`도 함께 복사
- ✅ `main.py`의 모듈 경로 자동 수정 (`app.api_server` → `api_server`)

### 2. Systemd 서비스

`scripts/setup_systemd.sh`가 수정되었습니다:

- ✅ `ExecStart` 경로: `$APP_DIR/main.py` (app 폴더 없이)

### 3. 모듈 경로

EC2에서:
- `app.api_server:app` → `api_server:app`
- 상대 import는 그대로 작동 (같은 디렉토리 구조)

## 🚀 배포 프로세스

### 자동 배포 (GitHub Actions)

1. **코드 푸시**
   ```bash
   git add .
   git commit -m "Update app"
   git push origin main
   ```

2. **GitHub Actions 실행**
   - `app` 폴더 내용만 EC2에 배포
   - 자동으로 의존성 설치 및 서비스 재시작

### 수동 배포

EC2에서 직접 배포하려면:

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 임시 디렉토리에서 클론
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR
git clone --depth 1 https://github.com/your-username/rag.git temp-repo

# app 폴더 내용만 복사
cp -r temp-repo/app/* ~/rag-app/
cp temp-repo/requirements.txt ~/rag-app/

# 정리
cd ~
rm -rf $TEMP_DIR

# 의존성 설치 및 서비스 재시작
cd ~/rag-app
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rag-api
```

## 📝 주의사항

### 1. 상대 Import

`app` 폴더 내부의 상대 import는 그대로 작동합니다:
- `from .app import ...` ✅
- `from .models import ...` ✅
- `from .router import ...` ✅

### 2. main.py 수정

`main.py`의 uvicorn 실행 부분이 자동으로 수정됩니다:
- 원본: `"app.api_server:app"`
- 배포 후: `"api_server:app"`

### 3. requirements.txt 위치

- `app/requirements.txt`가 있으면 사용
- 없으면 루트의 `requirements.txt` 사용

## 🔍 확인 방법

### 배포 후 확인

```bash
# EC2 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 디렉토리 구조 확인
ls -la ~/rag-app

# 예상 출력:
# api_server.py
# main.py
# requirements.txt
# venv/
# .env
# ...

# 서비스 상태 확인
sudo systemctl status rag-api

# 헬스 체크
curl http://localhost:8000/health
```

## 🛠️ 문제 해결

### 문제 1: 모듈을 찾을 수 없음

**증상:**
```
ModuleNotFoundError: No module named 'api_server'
```

**해결:**
```bash
# main.py 확인
cat ~/rag-app/main.py | grep api_server

# 수동 수정
cd ~/rag-app
sed -i 's/"app\.api_server:app"/"api_server:app"/g' main.py
sudo systemctl restart rag-api
```

### 문제 2: 상대 import 오류

**증상:**
```
ImportError: attempted relative import with no known parent package
```

**해결:**
- `api_server.py`의 상대 import 확인
- 같은 디렉토리 구조인지 확인

### 문제 3: requirements.txt 없음

**해결:**
```bash
# 루트의 requirements.txt 복사
cd ~/rag-app
# 또는 GitHub에서 다시 다운로드
```

## ✅ 체크리스트

배포 전 확인:

- [ ] `app` 폴더에 필요한 모든 파일이 있음
- [ ] `requirements.txt`가 `app/` 또는 루트에 있음
- [ ] GitHub Secrets 설정 완료
- [ ] EC2 보안 그룹 SSH 규칙 설정 완료
- [ ] Systemd 서비스 설정 완료

배포 후 확인:

- [ ] `~/rag-app`에 `app` 폴더의 내용이 있음
- [ ] `main.py`가 `api_server:app`을 참조함
- [ ] 서비스가 정상 실행됨
- [ ] 헬스 체크 통과

---

**이제 `app` 폴더만 깔끔하게 배포됩니다!** 🚀

