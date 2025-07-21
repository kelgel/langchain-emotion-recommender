echo "🧹 KDT_BE12_Toy_Project4 정리 중..."
echo "================================="

echo "⚠️  이 작업은 다음을 정리합니다:"
echo "- 모든 Docker 컨테이너"
echo "- 모든 Docker 볼륨 (데이터베이스 데이터 포함)"
echo "- 사용하지 않는 Docker 이미지"
echo "- Python 가상환경"
echo ""
read -p "계속하시겠습니까? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    # Docker 정리
    echo "🐳 Docker 리소스 정리 중..."
    docker-compose down -v 2>/dev/null || true
    docker system prune -f
    docker volume prune -f

    # Python 환경 정리
    if [ -d "ai-service/ai_venv" ]; then
        echo "🐍 Python 가상환경 삭제 중..."
        rm -rf ai-service/ai_venv
    fi

    # 빌드 파일 정리
    if [ -d "target" ]; then
        echo "🗑️  Maven 빌드 파일 정리 중..."
        rm -rf target
    fi

    if [ -d "build" ]; then
        echo "🗑️  Gradle 빌드 파일 정리 중..."
        rm -rf build
    fi

    echo ""
    echo "✅ 정리 완료!"
    echo "💡 새로 시작하려면: ./start.sh"
else
    echo "❌ 정리 작업을 취소했습니다."
fi