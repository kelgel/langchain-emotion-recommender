#!/bin/bash

echo "🔄 KDT_BE12_Toy_Project4 업데이트 중..."
echo "===================================="

# Git 업데이트
echo "📥 Git 최신 변경사항 가져오기..."
git pull origin main

# 종료 옵션 제공
echo "업데이트 방식을 선택하세요:"
echo "1) 빠른 업데이트 (코드만)"
echo "2) 전체 재빌드 (Docker 이미지 포함)"
echo "3) 완전 재설치 (모든 데이터 초기화)"
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "🔄 빠른 업데이트 시작..."

        # Java 빌드
        if [ -f "pom.xml" ]; then
            ./mvnw clean package -DskipTests
        elif [ -f "build.gradle" ]; then
            ./gradlew clean build -x test
        fi

        # Python 패키지 업데이트
        if [ -d "ai-service" ]; then
            cd ai-service
            if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
                source ai_venv/Scripts/activate
            else
                source ai_venv/bin/activate
            fi
            pip install -r requirements.txt --upgrade
            cd ..
        fi

        # 컨테이너 재시작
        docker-compose restart
        ;;

    2)
        echo "🔨 전체 재빌드 시작..."

        # 기존 컨테이너 및 이미지 정리
        docker-compose down
        docker-compose build --no-cache

        # 재시작
        ./start.sh
        ;;

    3)
        echo "🗑️  완전 재설치 시작..."

        # 모든 Docker 데이터 정리
        docker-compose down -v
        docker system prune -f
        docker volume prune -f

        # Python 환경 재생성
        if [ -d "ai-service/ai_venv" ]; then
            rm -rf ai-service/ai_venv
        fi

        # 완전 재시작
        ./start.sh
        ;;

    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "✅ 업데이트 완료!"
echo "📊 상태 확인: ./status.sh"
EOF