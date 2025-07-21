@echo off
chcp 65001 >nul 2>&1

echo 🛑 KDT_BE12_Toy_Project4 종료 중...
echo =================================

REM 프로젝트 루트로 이동
cd /d "%~dp0.."

echo 종료 방식을 선택하세요:
echo 1^) 일반 종료 ^(컨테이너만 중지^)
echo 2^) 완전 종료 ^(볼륨 데이터 포함 삭제^)
echo 3^) 개발 환경 정리 ^(이미지도 삭제^)
set /p choice=선택 ^(1-3^):

if "%choice%"=="1" (
    echo 🔄 컨테이너 중지 중...
    docker-compose stop
    echo ✅ 컨테이너가 중지되었습니다.
    echo 💡 재시작: scripts\start.bat
) else if "%choice%"=="2" (
    echo 🗑️  완전 종료 중... ^(볼륨 데이터 삭제^)
    docker-compose down -v
    echo ✅ 모든 컨테이너와 볼륨이 삭제되었습니다.
    echo 💡 재시작: scripts\start.bat
) else if "%choice%"=="3" (
    echo 🧹 개발 환경 완전 정리 중...

    docker-compose down -v
    docker system prune -f
    docker volume prune -f

    if exist ai-service\ai_venv (
        echo Python 가상환경 삭제 중...
        rmdir /s /q ai-service\ai_venv
    )

    echo ✅ 개발 환경이 완전히 정리되었습니다.
    echo 💡 재시작: scripts\start.bat
) else (
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

echo.
echo 🏁 종료 완료!
pause