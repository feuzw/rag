#!/bin/bash
# EC2 초기 설정 스크립트

set -e

echo "🚀 EC2 인스턴스 초기 설정 시작..."

# 패키지 업데이트
echo "📦 시스템 패키지 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
echo "📦 필수 패키지 설치 중..."
sudo apt install -y python3-pip python3-venv git curl

# 애플리케이션 디렉토리 생성
echo "📁 애플리케이션 디렉토리 생성..."
mkdir -p ~/rag-app
cd ~/rag-app

# .env 파일 생성 안내
echo "📝 환경 변수 설정..."
if [ ! -f ".env" ]; then
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ .env 파일이 생성되었습니다 (env.template 복사)"
    else
        cat > .env << 'EOF'
POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
HOST=0.0.0.0
PORT=8000
EOF
        echo "✅ .env 파일이 생성되었습니다"
    fi
    echo "⚠️  .env 파일을 편집하여 실제 값을 입력해주세요:"
    echo "   nano .env"
else
    echo "ℹ️  .env 파일이 이미 존재합니다"
fi

# Git 저장소 클론 안내
echo ""
echo "📥 다음 명령어로 저장소를 클론하세요:"
echo "   git clone <YOUR_GITHUB_REPO_URL> ~/rag-app"
echo ""

echo "✅ EC2 초기 설정 완료!"

