@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo 🔄 KDT_BE12_Toy_Project4 업데이트 중...
echo ====================================

REM 프로젝트 루트로 이동 (scripts 폴더에서 1단계 위로)
cd /d "%~dp0.."

echo.
echo 업데이트 방식을 선택하세요:
echo 1^) 빠른 재시작 ^(컨테이너만 재시작^)
echo 2^) 이미지 재빌드 ^(코드 변경사항 반영^)
echo 3^) 완전 재설치 ^(모든 데이터 초기화^)
set /p choice=선택 ^(1-3^): 

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo 🔄 빠른 재시작 중...
    echo 💡 컨테이너만 재시작하여 빠르게 적용합니다
    
    docker-compose restart
    
    echo ⏳ 서비스 재시작 대기 중...
    timeout /t 15 /nobreak >nul
    
) else if "%choice%"=="2" (
    echo 🔨 이미지 재빌드 중...
    echo 💡 코드 변경사항을 반영하여 이미지를 다시 빌드합니다
    
    docker-compose down
    docker-compose up --build -d
    
    echo ⏳ 서비스 시작 대기 중...
    timeout /t 30 /nobreak >nul
    
) else if "%choice%"=="3" (
    echo 🗑️  완전 재설치 중...
    echo 💡 모든 데이터를 초기화하고 새로 시작합니다
    
    docker-compose down -v
    docker system prune -f
    docker volume prune -f
    
    if exist ai-service\ai_venv (
        echo Python 가상환경 삭제 중...
        rmdir /s /q ai-service\ai_venv >nul 2>&1
    )
    
    docker-compose up --build -d
    
    echo ⏳ 서비스 시작 대기 중...
    timeout /t 45 /nobreak >nul
    
) else (
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

REM 헬스체크
echo 🔍 서비스 상태 확인 중...

curl -f http://localhost:8001/actuator/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Spring Boot ^(8001^) 응답 없음
) else (
    echo ✅ Spring Boot ^(8001^) 정상
)

curl -f http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FastAPI ^(8003^) 응답 없음
) else (
    echo ✅ FastAPI ^(8003^) 정상
)

curl -f http://localhost:8002/api/v2/heartbeat >nul 2>&1
if errorlevel 1 (
    echo ⚠️  ChromaDB ^(8002^) 응답 없음
) else (
    echo ✅ ChromaDB ^(8002^) 정상
)

echo.
echo ✅ 업데이트 완료!
echo ======================================
echo 📍 접속 URL:
echo    Spring Boot: http://localhost:8001
echo    FastAPI:     http://localhost:8003
echo    ChromaDB:    http://localhost:8002/api/v2/heartbeat
echo    Swagger UI:  http://localhost:8003/docs
echo.
echo 📊 상세 상태: status.bat
echo 🛑 종료:       stop.bat
echo.
pause
