"""로컬 개발 환경에서 FastAPI 서버를 실행하는 스크립트."""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가 (상대 import를 위해)
app_dir = Path(__file__).parent
project_root = app_dir.parent
sys.path.insert(0, str(project_root))

# .env 파일 로드 (선택사항)
try:
    from dotenv import load_dotenv

    # 프로젝트 루트의 .env 파일 로드
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env 파일 로드됨: {env_path}")
    else:
        # 현재 디렉토리의 .env 파일도 시도
        load_dotenv()
        print("ℹ️  .env 파일을 찾을 수 없습니다 (환경 변수 직접 사용)")
except ImportError:
    print("ℹ️  python-dotenv가 설치되지 않음 (환경 변수 직접 사용)")

# 필수 환경 변수 확인
required_env_vars = ["POSTGRES_CONNECTION_STRING", "OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
    print("\n.env 파일에 다음을 추가하세요:")
    print("POSTGRES_CONNECTION_STRING=postgresql://...")
    print("OPENAI_API_KEY=your-api-key")
    print("\n또는 환경 변수로 직접 설정하세요.")
    sys.exit(1)

# uvicorn 실행
if __name__ == "__main__":
    import uvicorn

    # 서버 설정
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"\n🚀 FastAPI 서버 시작 중...")
    print(f"   호스트: {host}")
    print(f"   포트: {port}")
    print(f"   자동 리로드: {reload}")
    print(f"   URL: http://localhost:{port}")
    print(f"   API 문서: http://localhost:{port}/docs\n")

    # uvicorn 실행
    # 직접 import하여 app 객체를 가져옴 (상대 import 문제 해결)
    from app.api_server import app

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(app_dir)] if reload else None,
    )

