@echo off
echo ====================================
echo    최종 ChromaDB 설정 적용
echo ====================================

echo 🛑 1. 모든 서비스 중지 및 볼륨 초기화...
docker-compose down --volumes

echo.
echo 🔧 2. docker-compose.yml과 llm.py 수정 완료 확인
echo    - 볼륨 공유: chroma_data:/app/data/chroma_db
echo    - 환경변수: DOCKER_ENV=true
echo    - 예외 처리 추가

echo.
echo 🔨 3. AI Service 재빌드...
docker-compose build --no-cache ai-service

echo.
echo 🚀 4. 단계별 서비스 시작...
echo    ChromaDB 먼저 시작...
docker-compose up -d chroma

echo ⏳ ChromaDB 초기화 대기 (30초)...
timeout /t 30 /nobreak

echo    AI Service 시작...
docker-compose up -d ai-service

echo ⏳ AI Service 안정화 대기 (20초)...
timeout /t 20 /nobreak

echo.
echo 📊 5. 상태 확인:
docker-compose ps

echo.
echo 📋 6. AI Service 로그:
docker-compose logs --tail=15 ai-service

echo.
echo 🧪 7. 최종 테스트:
powershell -Command "
try {
    $response = Invoke-WebRequest 'http://localhost:8003/' -TimeoutSec 10 -UseBasicParsing
    Write-Host '🎉 성공! AI Service가 정상 작동합니다!'
    Write-Host 'Status Code:', $response.StatusCode
} catch {
    Write-Host '📋 로그를 확인해보세요.'
    Write-Host 'Error:', $_.Exception.Message
}
"

pause