#!/bin/bash
# Systemd 서비스 설정 스크립트 (프로덕션: /opt/rag-app)

set -e

echo "🔧 Systemd 서비스 설정 시작 (프로덕션 모드)..."

# 현재 사용자 확인
CURRENT_USER=$(whoami)
APP_DIR="/opt/rag-app"

echo "사용자: $CURRENT_USER"
echo "애플리케이션 경로: $APP_DIR"

# 디렉토리 존재 확인
if [ ! -d "$APP_DIR" ]; then
    echo "❌ 오류: $APP_DIR 디렉토리가 존재하지 않습니다."
    echo "   먼저 scripts/setup_ec2_production.sh를 실행하거나 코드를 클론하세요."
    exit 1
fi

# 소유권 확인 및 설정
echo "🔐 디렉토리 소유권 확인..."
sudo chown -R $CURRENT_USER:$CURRENT_USER $APP_DIR

# 서비스 파일 생성
echo "📝 Systemd 서비스 파일 생성..."
sudo tee /etc/systemd/system/rag-api.service > /dev/null << EOF
[Unit]
Description=RAG FastAPI Service (Production)
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app/main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

# 보안 설정
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Systemd 데몬 리로드
echo "🔄 Systemd 데몬 리로드..."
sudo systemctl daemon-reload

# 서비스 활성화
echo "✅ 서비스 활성화..."
sudo systemctl enable rag-api

# 서비스 시작
echo "🚀 서비스 시작..."
sudo systemctl start rag-api

# 서비스 상태 확인
echo ""
echo "📊 서비스 상태:"
sudo systemctl status rag-api --no-pager || true

echo ""
echo "✅ Systemd 서비스 설정 완료!"
echo ""
echo "📌 애플리케이션 위치: $APP_DIR"
echo ""
echo "유용한 명령어:"
echo "  - 서비스 상태 확인: sudo systemctl status rag-api"
echo "  - 서비스 재시작: sudo systemctl restart rag-api"
echo "  - 로그 확인: sudo journalctl -u rag-api -f"
echo "  - 서비스 중지: sudo systemctl stop rag-api"
echo "  - 최근 로그: sudo journalctl -u rag-api -n 50"

