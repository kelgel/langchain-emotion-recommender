#!/bin/bash

# UTF-8 인코딩 설정
export LC_ALL=ko_KR.UTF-8 2>/dev/null || export LC_ALL=C.UTF-8 2>/dev/null || export LC_ALL=en_US.UTF-8 2>/dev/null || true
export LANG=ko_KR.UTF-8 2>/dev/null || export LANG=C.UTF-8 2>/dev/null || export LANG=en_US.UTF-8 2>/dev/null || true

echo "🛑 KDT_BE12_Toy_Project4 종료 중..."
echo "================================="

# 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "종료 방식을 선택하세요:"
echo "1) 일반 종료 (컨테이너만 중지)"
echo "2) 완전 종료 (볼륨 데이터 포함 삭제)"
echo "3) 개발 환경 정리 (이미지도 삭제)"
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "🔄 컨테이너 중지 중..."
        docker-compose stop
        echo "✅ 컨테이너가 중지되었습니다."
        echo "💡 재시작: scripts/start.sh"
        ;;

    2)
        echo "🗑️  완전 종료 중... (볼륨 데이터 삭제)"
        docker-compose down -v
        echo "✅ 모든 컨테이너와 볼륨이 삭제되었습니다."
        echo "💡 재시작: scripts/start.sh"
        ;;

    3)
        echo "🧹 개발 환경 완전 정리 중..."

        docker-compose down -v
        docker system prune -f
        docker volume prune -f

        if [ -d "ai-service/ai_venv" ]; then
            echo "Python 가상환경 삭제 중..."
            rm -rf ai-service/ai_venv
        fi

        echo "✅ 개발 환경이 완전히 정리되었습니다."
        echo "💡 재시작: scripts/start.sh"
        ;;

    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "🏁 종료 완료!"