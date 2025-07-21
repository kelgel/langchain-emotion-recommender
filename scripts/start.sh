#!/bin/bash

# UTF-8 인코딩 설정
export LC_ALL=ko_KR.UTF-8 2>/dev/null || export LC_ALL=C.UTF-8 2>/dev/null || export LC_ALL=en_US.UTF-8 2>/dev/null || true
export LANG=ko_KR.UTF-8 2>/dev/null || export LANG=C.UTF-8 2>/dev/null || export LANG=en_US.UTF-8 2>/dev/null || true

echo "🚀 KDT_BE12_Toy_Project4 시작 중..."
echo "===================================="

# 프로젝트 루트로 이동 (scripts 폴더에서 1단계 위로)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "프로젝트 루트: $PROJECT_ROOT"

# 환경변수 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "현재 위치: $(pwd)"
    echo "다음 내용으로 .env 파일을 생성해주세요:"
    echo ""
    echo "OPENAI_API_KEY=sk-proj-your-key-here"
    echo "AWS_MYSQL_URL=your-aws-rds-endpoint"
    echo "AWS_MYSQL_USERNAME=your-username"
    echo "AWS_MYSQL_PASSWORD=your-password"
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo "✅ 환경변수 파일 확인됨 ($(pwd)/.env)"

# Docker 상태 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다!"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker가 실행되지 않고 있습니다!"
    echo "Docker Desktop을 시작해주세요."
    exit 1
fi

echo "✅ Docker 상태 정상"

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down 2>/dev/null || true

# AI 서비스 Python 환경 준비
echo "🐍 Python AI 환경 준비 중..."
if [ -d "ai-service" ]; then
    cd ai-service

    if [ ! -d "ai_venv" ]; then
        python3 -m venv ai_venv || python -m venv ai_venv
        echo "✅ Python 가상환경 생성됨"
    fi

    source ai_venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "✅ Python 패키지 설치 완료"

    cd ..
fi

# Docker Compose 시작
echo "🐳 Docker 컨테이너 시작 중..."
echo "💡 Docker 내부에서 Java 빌드를 수행합니다..."
docker-compose up --build -d

# 서비스 시작 대기
echo "⏳ 서비스 시작 대기 중..."
sleep 45

# 헬스체크
echo "🔍 서비스 상태 확인 중..."

if curl -f http://localhost:8001/actuator/health &>/dev/null; then
    echo "✅ Spring Boot (8001) 정상"
else
    echo "⚠️  Spring Boot (8001) 응답 없음"
fi

if curl -f http://localhost:8003/health &>/dev/null; then
    echo "✅ FastAPI (8003) 정상"
else
    echo "⚠️  FastAPI (8003) 응답 없음"
fi

if curl -f http://localhost:8002/api/v2/heartbeat &>/dev/null; then
    echo "✅ ChromaDB (8002) 정상"
else
    echo "⚠️  ChromaDB (8002) 응답 없음"
fi

echo ""
echo "🎉 프로젝트 시작 완료!"
echo "======================================"
echo "📍 접속 URL:"
echo "   Spring Boot: http://localhost:8001"
echo "   FastAPI:     http://localhost:8003"
echo "   ChromaDB:    http://localhost:8002"
echo "   Swagger UI:  http://localhost:8003/docs"
echo ""
echo "📊 상태 확인: ./status.sh"
echo "🛑 종료:       ./stop.sh"