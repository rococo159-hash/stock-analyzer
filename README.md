# 📊 주식분석도구

당신과 아내를 위한 **개인용 주식분석도구**입니다.
로컬 PC에서 실행하고, 휴대폰에서는 앱처럼 사용할 수 있습니다.

---

## ✨ 주요 기능

### 1️⃣ 기술적분석 (자동 신호)
- **이동평균선** (SMA 20/50/200)
  - 골든크로스/데드크로스 감지
- **RSI** (상대강도지수 14일)
  - 과매수/과매도 신호
- **MACD**
  - 신호선 교차 신호
- **스토캐스틱**
  - K%D% 신호

→ **기계적으로 종합 신호 생성** (강한 매수/약한 매수/중립/약한 매도/강한 매도)

### 2️⃣ 실시간 차트
- 토스증권 API 연동
- 최근 200일 데이터
- 4개 지표 한눈에 보기

### 3️⃣ 뉴스 & 시장정보 (개발 예정)
- 최근 1주일 뉴스
- 공매도 정보
- 기관/외국인 거래동향

---

## 🚀 설치 및 실행

### 📋 필수 요구사항

```
✅ Windows 10 이상
✅ Python 3.9 이상
✅ 토스증권 계좌 (API 키 필요)
✅ 인터넷 연결
```

### 1단계: Python 설치

1. https://www.python.org/downloads/ 접속
2. **Windows installer (64-bit)** 다운로드
3. 설치 시 **"Add Python to PATH"** 반드시 체크 ✅

확인:
```
cmd 열기 → python --version
```

### 2단계: 토스증권 API 키 발급

1. 토스증권 앱 열기
2. **설정 > Open API**
3. **Client ID** 복사
4. **Client Secret** 복사

### 3단계: 앱 설정

1. 이 폴더에서 `start.bat` **더블 클릭** 실행

   또는 (CMD 창에서 실행하려면):
   ```
   cd C:\your\folder\path
   start.bat
   ```

2. 처음 실행 시 자동으로:
   - 가상환경 생성
   - 필요한 패키지 설치
   - .env 파일 생성 요청

### 4단계: API 키 입력

**방법 1 - .env 파일 (안전)**
```
.env.example을 복사해서 .env 생성

.env 파일을 열어서:
TOSS_CLIENT_ID=여기에_입력
TOSS_CLIENT_SECRET=여기에_입력

저장 후 앱 재시작
```

**방법 2 - 앱에서 직접 입력**
```
브라우저 왼쪽 사이드바에서 직접 입력
(재시작할 때마다 입력해야 함)
```

### 5단계: 실행

```
start.bat 더블 클릭
또는 CMD에서: python -m streamlit run app.py
```

브라우저가 자동으로 열리면 성공! 🎉

---

## 📱 휴대폰에서 사용

### iOS 또는 Android

1. **PC에서 앱 실행** (start.bat 클릭)

2. **같은 WiFi에 연결**

3. **휴대폰 브라우저에서 접속**
   ```
   로컬 주소 (같은 WiFi):
   http://192.168.x.x:8501
   
   또는 cmd 창에서 표시되는 "로컬 URL" 복사
   ```

4. **앱처럼 설치**
   - 브라우저 **공유 버튼** 클릭
   - **"홈스크린에 추가"** 선택
   - 앱 아이콘 생성 ✅

5. **다음부터는 홈스크린 아이콘으로 실행**

### 외부 WiFi에서 접속 (PC 꺼져있어도)

선택 사항: ngrok 설정
```
1. ngrok 설치 (자동 완료됨)
2. ngrok 터널 생성
3. 휴대폰에서 ngrok URL 접속

(가이드는 앱 실행 후 화면에 표시됨)
```

---

## 🔧 문제 해결

### 1. "Python not found" 오류

```
원인: Python 설치 안 됨 또는 PATH 설정 안 됨

해결:
1. Python 설치 (위 참조)
2. 설치 시 "Add Python to PATH" 체크
3. PC 재부팅
4. start.bat 다시 실행
```

### 2. "API 인증 실패"

```
원인: Client ID/Secret 잘못됨

해결:
1. 토스증권 앱에서 API 키 다시 확인
2. 복사-붙여넣기 할 때 공백 없는지 확인
3. .env 파일 재저장 또는 앱에서 다시 입력
```

### 3. 휴대폰에서 "연결할 수 없음"

```
원인: 같은 WiFi가 아니거나 PC 종료됨

해결:
1. PC와 휴대폰이 같은 WiFi 사용 확인
2. PC에서 start.bat 실행 중 확인
3. 방화벽이 막고 있는지 확인
   - Windows 방화벽 > Streamlit 허용 추가
```

### 4. "ModuleNotFoundError" 오류

```
원인: 패키지 미설치

해결:
cmd를 관리자 권한으로 열어서:
pip install -r requirements.txt
```

---

## 📂 폴더 구조

```
stock-analyzer/
├── app.py                 # 메인 앱
├── requirements.txt       # 필요 패키지
├── start.bat             # Windows 실행 파일 (더블클릭!)
├── .env.example          # API 키 예제
├── .env                  # API 키 (생성되면 .gitignore 됨)
├── .gitignore            # Git 무시 파일
├── README.md             # 이 파일
└── venv/                 # 가상환경 (자동 생성)
```

---

## ⚙️ 설정 변경

### 앱 포트 변경

`.streamlit/config.toml`:
```toml
[server]
port = 8501  # 다른 번호로 변경 가능
```

### 테마 변경

`.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"    # 메인 색상
backgroundColor = "#ffffff"  # 배경
```

---

## 🔒 보안 주의사항

```
⚠️  중요!

1. .env 파일을 GitHub에 업로드하지 마세요
   → .gitignore에 자동 설정됨

2. API Secret을 절대 다른 사람과 공유 금지
   → 탈취되면 계좌가 위험함

3. 스크린샷할 때 API 키 포함 금지

4. start.bat는 안전함 (로컬에서만 실행)
```

---

## 🎯 사용 팁

### 매일 같은 시간에 실행
```
Windows 작업 스케줄러로 자동화 가능
(고급: .bat 파일 스케줄 설정)
```

### 모니터링 설정
```
종목 즐겨찾기 저장
→ 구현 예정
```

---

## 📞 지원

문제 발생 시:

1. README "문제 해결" 섹션 확인
2. start.bat 창의 오류 메시지 읽기
3. Python/패키지 버전 확인
4. PC 재부팅 시도

---

## 📚 토스증권 API 문서

공식 문서: https://developers.tossinvest.com/docs

---

**만든이**: 주식분석도구 v1.0
**마지막 수정**: 2026년 6월
**라이선스**: 개인용 (비상업)

Happy Investing! 🚀📈

