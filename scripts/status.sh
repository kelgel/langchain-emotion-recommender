#!/bin/bash

# UTF-8 인코딩 설정
export LC_ALL=ko_KR.UTF-8 2>/dev/null || export LC_ALL=C.UTF-8 2>/dev/null || export LC_ALL=en_US.UTF-8 2>/dev/null || true
export LANG=ko_KR.UTF-8 2>/dev/null || export LANG=C.UTF-8 2>/dev/null || export LANG=en_US.UTF-8 2>/dev/null || true

echo "📊 KDT_BE12_Toy_Project4 상태 확인"
echo "================================="

# 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 현재 위치: $(pwd)"

# Docker 상태 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다!"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker가 실행되지 않고 있습니다!"
    exit 1
fi

echo "✅ Docker 상태: 정상"
echo ""

# 컨테이너 상태 확인
echo "🐳 컨테이너 상태:"
echo "----------------------"
docker-compose ps 2>/dev/null || echo "❌ docker-compose.yml 파일을 찾을 수 없습니다."
echo ""

# 포트 사용 상황
echo "🔌 포트 사용 상황:"
echo "----------------------"
ports=("8001" "8003" "8002")
for port in "${ports[@]}"; do
    if lsof -i :$port &>/dev/null || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ 포트 $port: 사용 중"
    else
        echo "❌ 포트 $port: 사용 안함"
    fi
done
echo ""

# 서비스별 헬스체크
echo "🏥 서비스 헬스체크:"
echo "----------------------"

if curl -f -s http://localhost:8001 > /dev/null 2>&1; then
    echo "✅ Spring Boot (8001): 정상"
else
    echo "❌ Spring Boot (8001): 응답 없음"
fi

if curl -f -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ FastAPI (8003): 정상"
else
    echo "❌ FastAPI (8003): 응답 없음"
fi

if curl -f -s http://localhost:8002/api/v2/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB (8002): 정상"
else
    echo "❌ ChromaDB (8002): 응답 없음"
fi

echo ""

# 환경변수 확인
echo "🔑 환경변수 상태:"
echo "----------------------"
if [ -f .env ]; then
    echo "✅ .env 파일: 존재"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ OpenAI API Key: 설정됨"
    else
        echo "❌ OpenAI API Key: 미설정"
    fi
    if grep -q "AWS_MYSQL" .env; then
        echo "✅ AWS MySQL: 설정됨"
    else
        echo "❌ AWS MySQL: 미설정"
    fi
else
    echo "❌ .env 파일: 없음"
fi

echo ""
echo "🔧 유용한 명령어:"
echo "- 로그 확인:    docker-compose logs"
echo "- 프로젝트 종료: scripts/stop.sh"