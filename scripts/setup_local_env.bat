@echo off
chcp 65001 >nul
echo 🐍 로컬 Python 환경 설정 시작...

REM 프로젝트 루트로 이동 (scripts 폴더에서 1단계 위로)
cd /d "%~dp0.."

REM ai-service 폴더로 이동
cd ai-service

echo 📦 가상환경 생성 중...
python -m venv ai_venv
if errorlevel 1 (
    echo ❌ 가상환경 생성 실패! Python이 설치되어 있는지 확인하세요.
    pause
    exit /b 1
)

echo 🔧 가상환경 활성화 중...
call ai_venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패!
    pause
    exit /b 1
)

echo 📚 패키지 설치 중...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ pip 업그레이드 실패!
    pause
    exit /b 1
)

pip cache purge
pip install --only-binary=all --force-reinstall chromadb==0.4.15
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패! requirements.txt 파일을 확인하세요.
    pause
    exit /b 1
)

echo ✅ 설치 완료! 테스트 실행...
python main.py

echo 🎉 로컬 Python 환경 설정 완료!
echo 💡 다음부터는 다음 명령어로 활성화하세요:
echo    cd ai-service
echo    ai_venv\Scripts\activate
echo.
pause
