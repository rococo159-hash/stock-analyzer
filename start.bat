@echo off
REM ============================================
REM 주식분석도구 - Windows 자동 실행 스크립트
REM ============================================

chcp 65001 > nul
cls

echo.
echo ============================================
echo   📊 주식분석도구 - Windows 실행 스크립트
echo ============================================
echo.

REM Python 버전 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo    https://www.python.org/downloads/ 에서 설치하세요.
    echo    (반드시 "Add Python to PATH" 선택)
    pause
    exit /b 1
)

echo ✅ Python 설치 확인됨
echo.

REM 가상환경 확인/생성
if not exist venv (
    echo 📦 가상환경 생성 중...
    python -m venv venv
    echo ✅ 가상환경 생성 완료
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 패키지 설치
echo 📥 필요한 패키지 설치 중...
python -m pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt

REM ngrok 설치 확인
echo.
echo 🌐 ngrok 설치 확인 중...
pip install pyngrok

REM .env 파일 확인
if not exist .env (
    echo.
    echo ⚠️  .env 파일이 없습니다.
    echo.
    echo .env.example를 복사해서 .env로 만들고
    echo 토스증권 API 키를 입력하세요.
    echo.
    echo (또는 앱 실행 후 사이드바에서 입력 가능)
    pause
)

REM Streamlit 앱 실행
echo.
echo ============================================
echo   🚀 Streamlit 앱 시작 중...
echo ============================================
echo.
echo 잠시 후 브라우저에서 앱이 열립니다.
echo.
echo 휴대폰에서 접속하려면:
echo   1. 아래 터미널 메시지에서 ngrok URL 확인
echo   2. 휴대폰 브라우저에서 그 URL 입력
echo   3. 화면 오른쪽 위 공유 버튼 > 홈스크린에 추가
echo.
echo 앱 종료: Ctrl+C
echo.
echo ============================================

python -m streamlit run app.py

pause
