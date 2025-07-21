#!/bin/bash
@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo 🚀 KDT_BE12_Toy_Project4 시작 중...
echo ====================================

REM 프로젝트 루트로 이동 (scripts 폴더에서 1단계 위로)
cd /d "%~dp0.."

REM 환경변수 확인
if not exist .env (
    echo ❌ .env 파일이 없습니다!
    echo 현재 위치: %CD%
    echo 다음 내용으로 .env 파일을 생성해주세요:
    echo.
    echo OPENAI_API_KEY=sk-proj-your-key-here
    echo AWS_MYSQL_URL=your-aws-rds-endpoint
    echo AWS_MYSQL_USERNAME=your-username
    echo AWS_MYSQL_PASSWORD=your-password
    echo.
    pause
    exit /b 1
)

echo ✅ 환경변수 파일 확인됨 (%CD%\.env)

REM Docker 상태 확인
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 설치되지 않았습니다!
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 실행되지 않고 있습니다!
    echo Docker Desktop을 시작해주세요.
    pause
    exit /b 1
)

echo ✅ Docker 상태 정상

REM 기존 컨테이너 정리
echo 🧹 기존 컨테이너 정리 중...
docker-compose down >nul 2>&1

REM AI 서비스 Python 환경 준비
echo 🐍 Python AI 환경 준비 중...
if exist ai-service (
    cd ai-service
    if not exist ai_venv (
        python -m venv ai_venv
        echo ✅ Python 가상환경 생성됨
    )
    call ai_venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    echo ✅ Python 패키지 설치 완료
    cd ..
)

REM Docker Compose 시작
echo 🐳 Docker 컨테이너 시작 중...
echo 💡 Docker 내부에서 Java 빌드를 수행합니다...
docker-compose up --build -d

REM 서비스 시작 대기
echo ⏳ 서비스 시작 대기 중...
timeout /t 45 /nobreak >nul

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
echo 🎉 프로젝트 시작 완료!
echo ======================================
echo 📍 접속 URL:
echo    Spring Boot: http://localhost:8001
echo    FastAPI:     http://localhost:8003
echo    ChromaDB:    http://localhost:8002
echo    Swagger UI:  http://localhost:8003/docs
echo.
echo 📊 상태 확인: status.bat
echo 🛑 종료:       stop.bat
echo.
pause