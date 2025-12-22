"""로컬 개발 환경에서 FastAPI 서버를 실행하는 스크립트."""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가 (상대 import를 위해)
# 로컬: app/main.py -> project_root는 rag/
# 우분투: app/main.py가 없고 루트에 main.py가 있거나, app/ 폴더가 없을 수 있음
current_file = Path(__file__).resolve()
current_dir = current_file.parent

# app/main.py에서 실행되는 경우 (로컬)
if current_dir.name == "app" and (current_dir.parent / "app").exists():
    app_dir = current_dir
    project_root = app_dir.parent.resolve()
# 프로젝트 루트에서 실행되는 경우 (우분투: app/ 폴더 없음)
else:
    project_root = current_dir.resolve()
    app_dir = project_root  # 우분투에서는 app 폴더가 없으므로 루트가 app_dir

# 현재 작업 디렉토리를 프로젝트 루트로 변경 (app 패키지 인식 문제 해결)
os.chdir(project_root)

# 프로젝트 루트를 Python path에 추가
if str(project_root) not in sys.path:
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
    # 우분투: app/ 폴더가 없고 루트에 파일들이 직접 있음
    # 로컬: app/ 폴더가 있음

    # app 폴더가 있는지 확인
    app_folder = project_root / "app"
    if app_folder.exists() and (app_folder / "api_server.py").exists():
        # 로컬 환경: app/ 폴더가 있음
        app_module_path = "app.api_server:app"
        reload_dir = str(app_folder)
    elif (project_root / "api_server.py").exists():
        # 우분투 환경: app/ 폴더가 없고 루트에 파일들이 직접 있음
        # api_server를 직접 import
        app_module_path = "api_server:app"
        reload_dir = str(project_root)
    else:
        print(f"❌ 오류: api_server.py를 찾을 수 없습니다.")
        print(f"   프로젝트 루트: {project_root}")
        print(f"   app 폴더 존재: {app_folder.exists()}")
        sys.exit(1)

    uvicorn.run(
        app_module_path,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[reload_dir] if reload else None,
    )

