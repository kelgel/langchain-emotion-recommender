@echo off
chcp 65001 >nul 2>&1

echo 📊 KDT_BE12_Toy_Project4 상태 확인
echo =================================

REM 프로젝트 루트로 이동
cd /d "%~dp0.."

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 설치되지 않았습니다!
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 실행되지 않고 있습니다!
    pause
    exit /b 1
)

echo ✅ Docker 상태: 정상
echo 📁 현재 위치: %CD%
echo.

echo 🐳 컨테이너 상태:
echo ----------------------
docker-compose ps 2>nul || echo ❌ docker-compose.yml 파일을 찾을 수 없습니다.
echo.

echo 🔌 포트 사용 상황:
echo ----------------------
netstat -an | findstr ":8001 " >nul && echo ✅ 포트 8001: 사용 중 || echo ❌ 포트 8001: 사용 안함
netstat -an | findstr ":8003 " >nul && echo ✅ 포트 8003: 사용 중 || echo ❌ 포트 8003: 사용 안함
netstat -an | findstr ":8002 " >nul && echo ✅ 포트 8002: 사용 중 || echo ❌ 포트 8002: 사용 안함
echo.

echo 🏥 서비스 헬스체크:
echo ----------------------

curl -f -s http://localhost:8001/main >nul 2>&1
if errorlevel 1 (
    echo ❌ Spring Boot ^(8001^): 응답 없음
) else (
    echo ✅ Spring Boot ^(8001^): 정상
)

curl -f -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo ❌ FastAPI ^(8003^): 응답 없음
) else (
    echo ✅ FastAPI ^(8003^): 정상
)

curl -f -s http://localhost:8002/api/v2/heartbeat >nul 2>&1
if errorlevel 1 (
    echo ❌ ChromaDB ^(8002^): 응답 없음
) else (
    echo ✅ ChromaDB ^(8002^): 정상
)

echo.

echo 🔑 환경변수 상태:
echo ----------------------
if exist .env (
    echo ✅ .env 파일: 존재
    findstr /c:"OPENAI_API_KEY" .env >nul && echo ✅ OpenAI API Key: 설정됨 || echo ❌ OpenAI API Key: 미설정
    findstr /c:"AWS_MYSQL" .env >nul && echo ✅ AWS MySQL: 설정됨 || echo ❌ AWS MySQL: 미설정
) else (
    echo ❌ .env 파일: 없음
)

echo.
echo 🔧 유용한 명령어:
echo - 로그 확인:    docker-compose logs
echo - 프로젝트 종료: scripts\stop.bat
pause