import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import warnings
warnings.filterwarnings('ignore')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================
# 한글 폰트 설정
# ============================================
def set_korean_font():
    system = platform.system()
    if system == "Windows":
        candidates = ["Malgun Gothic", "Gulim", "Batang"]
    elif system == "Darwin":
        candidates = ["AppleGothic", "Apple SD Gothic Neo"]
    else:
        candidates = ["NanumGothic", "Noto Sans CJK KR"]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams['font.family'] = font
            break
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

st.set_page_config(
    page_title="주식분석도구",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# 토스증권 API 클래스
# ============================================
class TossInvestAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://openapi.tossinvest.com"

    def get_access_token(self):
        if self.access_token and datetime.now() < self.token_expires_at:
            return self.access_token
        try:
            response = requests.post(
                f"{self.base_url}/oauth2/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data['access_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'] - 300)
            return self.access_token
        except Exception as e:
            st.error(f"토큰 발급 실패: {str(e)}")
            return None

    def get_headers(self):
        token = self.get_access_token()
        if not token:
            return None
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_stock_info(self, symbol):
        try:
            headers = self.get_headers()
            if not headers:
                return None
            response = requests.get(
                f"{self.base_url}/api/v1/stocks",
                headers=headers, params={"symbols": symbol}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result') and len(data['result']) > 0:
                return data['result'][0]
            return None
        except Exception:
            return None

    def get_quote(self, symbol):
        try:
            headers = self.get_headers()
            if not headers:
                return None
            response = requests.get(
                f"{self.base_url}/api/v1/prices",
                headers=headers, params={"symbols": symbol}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result') and len(data['result']) > 0:
                return data['result'][0]
            return None
        except Exception as e:
            st.error(f"시세 조회 실패: {str(e)}")
            return None

    def get_price_limits(self, symbol):
        try:
            headers = self.get_headers()
            if not headers:
                return None
            response = requests.get(
                f"{self.base_url}/api/v1/price-limits",
                headers=headers, params={"symbol": symbol}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result'):
                return data['result']
            return None
        except Exception:
            return None

    def get_candles(self, symbol, interval='1d', count=200):
        try:
            headers = self.get_headers()
            if not headers:
                return None
            response = requests.get(
                f"{self.base_url}/api/v1/candles",
                headers=headers,
                params={"symbol": symbol, "interval": interval, "count": count},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get('result') and data['result'].get('candles'):
                candles = data['result']['candles']
                df = pd.DataFrame(candles)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                df.rename(columns={
                    'openPrice': 'open', 'highPrice': 'high',
                    'lowPrice': 'low', 'closePrice': 'close'
                }, inplace=True)
                return df
            return None
        except Exception as e:
            st.error(f"캔들 데이터 조회 실패: {str(e)}")
            return None

# ============================================
# 기술지표 계산
# ============================================
def calculate_sma(data, period):
    return data.rolling(window=period).mean()

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, fast=12, slow=26, signal=9):
    ema_fast = data.ewm(span=fast).mean()
    ema_slow = data.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_percent = k_percent.rolling(window=d_period).mean()
    return k_percent, d_percent

# ============================================
# 점수화 시스템 (-5 ~ +5)
# ============================================
def analyze_indicators(df):
    if len(df) < 200:
        return None

    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)

    sma20 = calculate_sma(close, 20)
    sma50 = calculate_sma(close, 50)
    sma200 = calculate_sma(close, 200)
    rsi = calculate_rsi(close, 14)
    macd_line, signal_line, histogram = calculate_macd(close)
    k_percent, d_percent = calculate_stochastic(high, low, close)

    current_price = close.iloc[-1]
    rsi_now = rsi.iloc[-1]
    k_now = k_percent.iloc[-1]
    d_now = d_percent.iloc[-1]
    hist_now = histogram.iloc[-1]
    hist_prev = histogram.iloc[-2] if len(histogram) > 1 else 0

    details = []
    raw_score = 0

    sma_points = 0
    above = []
    if current_price > sma20.iloc[-1]:
        sma_points += 1; above.append("20일")
    if current_price > sma50.iloc[-1]:
        sma_points += 1; above.append("50일")
    if current_price > sma200.iloc[-1]:
        sma_points += 1; above.append("200일")
    sma_contrib = (sma_points - 1.5) / 1.5 * 1.25
    raw_score += sma_contrib
    if sma_points == 3:
        sma_msg = "주가가 20·50·200일선을 모두 위에 둠 (강한 상승 추세)"
    elif sma_points == 0:
        sma_msg = "주가가 모든 이동평균선 아래 (약세 추세)"
    else:
        sma_msg = f"주가가 {', '.join(above)}선 위 (혼조)"
    details.append(("이동평균선", sma_contrib, sma_msg))

    if rsi_now < 30:
        rsi_contrib = 1.25
        rsi_msg = f"RSI {rsi_now:.0f} — 과매도 구간 (반등 가능성, 매수 관점)"
    elif rsi_now > 70:
        rsi_contrib = -1.25
        rsi_msg = f"RSI {rsi_now:.0f} — 과매수 구간 (조정 가능성, 매도 관점)"
    elif rsi_now < 45:
        rsi_contrib = 0.5
        rsi_msg = f"RSI {rsi_now:.0f} — 중립~약세 (저점 근처)"
    elif rsi_now > 55:
        rsi_contrib = -0.5
        rsi_msg = f"RSI {rsi_now:.0f} — 중립~강세 (고점 근처)"
    else:
        rsi_contrib = 0
        rsi_msg = f"RSI {rsi_now:.0f} — 완전 중립"
    raw_score += rsi_contrib
    details.append(("RSI", rsi_contrib, rsi_msg))

    if hist_now > 0 and hist_prev < 0:
        macd_contrib = 1.25
        macd_msg = "MACD 골든크로스 발생 (상승 전환 신호)"
    elif hist_now < 0 and hist_prev > 0:
        macd_contrib = -1.25
        macd_msg = "MACD 데드크로스 발생 (하락 전환 신호)"
    elif hist_now > 0:
        macd_contrib = 0.6
        macd_msg = "MACD 히스토그램 양(+) (상승 모멘텀 유지)"
    else:
        macd_contrib = -0.6
        macd_msg = "MACD 히스토그램 음(-) (하락 모멘텀)"
    raw_score += macd_contrib
    details.append(("MACD", macd_contrib, macd_msg))

    if k_now < 20 and d_now < 20:
        stoch_contrib = 1.25
        stoch_msg = f"스토캐스틱 {k_now:.0f} — 과매도 (매수 관점)"
    elif k_now > 80 and d_now > 80:
        stoch_contrib = -1.25
        stoch_msg = f"스토캐스틱 {k_now:.0f} — 과매수 (매도 관점)"
    elif k_now < 40:
        stoch_contrib = 0.5
        stoch_msg = f"스토캐스틱 {k_now:.0f} — 낮은 편 (반등 여지)"
    elif k_now > 60:
        stoch_contrib = -0.5
        stoch_msg = f"스토캐스틱 {k_now:.0f} — 높은 편"
    else:
        stoch_contrib = 0
        stoch_msg = f"스토캐스틱 {k_now:.0f} — 중립"
    raw_score += stoch_contrib
    details.append(("스토캐스틱", stoch_contrib, stoch_msg))

    final_score = max(-5, min(5, round(raw_score, 1)))

    return {
        'sma20': sma20, 'sma50': sma50, 'sma200': sma200,
        'rsi': rsi, 'macd': macd_line, 'signal_line': signal_line,
        'histogram': histogram, 'k_percent': k_percent, 'd_percent': d_percent,
        'score': final_score, 'details': details
    }

def score_to_label(score):
    if score >= 4:
        return "🟢 강한 매수 구간", "지표 대부분이 매수에 우호적입니다."
    elif score >= 2:
        return "🟡 약한 매수 구간", "일부 지표가 매수 쪽으로 기울어 있습니다."
    elif score > -2:
        return "⚪ 관망 구간", "신호가 엇갈립니다. 추세를 더 지켜볼 시점입니다."
    elif score > -4:
        return "🟠 약한 매도 구간", "일부 지표가 매도/조정 쪽으로 기울어 있습니다."
    else:
        return "🔴 강한 매도 구간", "지표 대부분이 약세를 가리킵니다."

KR_STOCKS = {
    "삼성전자": "005930", "SK하이닉스": "000660", "LG전자": "066570",
    "현대차": "005380", "LG화학": "051910", "카카오": "035720",
    "NAVER": "035420", "POSCO홀딩스": "005490", "셀트리온": "068270",
    "삼성바이오로직스": "207940",
}
US_STOCKS = {
    "Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "NVIDIA (NVDA)": "NVDA",
    "Tesla (TSLA)": "TSLA", "Amazon (AMZN)": "AMZN", "Alphabet (GOOGL)": "GOOGL",
    "Meta (META)": "META", "Netflix (NFLX)": "NFLX",
}

def main():
    st.title("📊 주식분석도구")

    api_key = os.getenv("TOSS_CLIENT_ID", "")
    api_secret = os.getenv("TOSS_CLIENT_SECRET", "")

    if not api_key or not api_secret:
        with st.sidebar:
            st.header("⚙️ API 설정")
            st.caption("입력 후 .env 파일에 저장하면 다음부터 자동 로그인됩니다.")
            api_key = st.text_input("Client ID", type="password")
            api_secret = st.text_input("Client Secret", type="password")
            if not api_key or not api_secret:
                st.warning("⚠️ API 키를 입력해주세요")
        if not api_key or not api_secret:
            st.info("""
            👈 왼쪽 사이드바(>)에서 토스증권 API 키를 입력하면 시작됩니다.

            **키를 숨기려면(자동 로그인):** 앱 폴더의 `.env` 파일에 아래처럼 저장하세요.
            ```
            TOSS_CLIENT_ID=발급받은_아이디
            TOSS_CLIENT_SECRET=발급받은_시크릿
            NGROK_AUTH_TOKEN=ngrok토큰
            ```
            저장 후 앱을 재시작하면 입력칸이 사라지고 자동으로 로그인됩니다.
            """)
            return

    api = TossInvestAPI(api_key, api_secret)

    market = st.radio("시장 선택", ["🇰🇷 국내주식", "🇺🇸 미국주식"], horizontal=True)

    if market == "🇰🇷 국내주식":
        stock_dict = KR_STOCKS
        placeholder = "예: 005930"
    else:
        stock_dict = US_STOCKS
        placeholder = "예: AAPL"

    col1, col2 = st.columns(2)
    with col1:
        selected_name = st.selectbox("인기 종목에서 선택", list(stock_dict.keys()))
        selected_symbol = stock_dict[selected_name]
    with col2:
        custom_symbol = st.text_input(f"또는 직접 입력 ({placeholder})")
        if custom_symbol:
            selected_symbol = custom_symbol.strip().upper()
            selected_name = selected_symbol

    if st.button("📊 분석 시작", type="primary"):
        analyze_stock(api, selected_symbol, selected_name)

def analyze_stock(api, symbol, name):
    with st.spinner("데이터 로드 중..."):
        info = api.get_stock_info(symbol)
        quote = api.get_quote(symbol)
        limits = api.get_price_limits(symbol)
        candles = api.get_candles(symbol, interval='1d', count=200)

    if not quote:
        st.error("❌ 종목 정보를 조회할 수 없습니다. 종목 코드를 확인해주세요.")
        return
    if candles is None or len(candles) < 100:
        st.error("❌ 캔들 데이터가 충분하지 않습니다 (200일 데이터 필요).")
        return

    display_name = name
    currency = quote.get('currency', 'KRW')
    if info and info.get('name'):
        display_name = info['name']

    current_price = float(quote.get('lastPrice', 0))
    unit = "원" if currency == "KRW" else "$"

    st.markdown(f"## {display_name} ({symbol})")

    cols = st.columns(4)
    with cols[0]:
        st.metric("현재가", f"{current_price:,.0f}{unit}")
    with cols[1]:
        if limits and limits.get('upperLimitPrice'):
            st.metric("상한가", f"{float(limits['upperLimitPrice']):,.0f}{unit}")
        else:
            st.metric("상한가", "-")
    with cols[2]:
        if limits and limits.get('lowerLimitPrice'):
            st.metric("하한가", f"{float(limits['lowerLimitPrice']):,.0f}{unit}")
        else:
            st.metric("하한가", "-")
    with cols[3]:
        if info and info.get('market'):
            st.metric("시장", info['market'])
        else:
            st.metric("통화", currency)

    st.markdown("---")

    result = analyze_indicators(candles)
    if result is None:
        st.warning("데이터가 부족하여 점수를 계산할 수 없습니다.")
        return

    score = result['score']
    label, summary = score_to_label(score)

    score_col1, score_col2 = st.columns([1, 2])
    with score_col1:
        st.metric("종합 점수", f"{score} / 5")
        pct = (score + 5) / 10
        st.progress(pct)
    with score_col2:
        st.markdown(f"### {label}")
        st.caption(summary)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 차트", "📊 지표 해설", "ℹ️ 정보"])

    with tab1:
        draw_chart(candles, result, display_name)

    with tab2:
        st.subheader("📊 지표별 점수 근거")
        st.caption("각 지표가 종합 점수에 기여한 정도와 그 의미입니다. (투자 조언이 아닌 객관적 지표 해석)")
        for indicator_name, contrib, msg in result['details']:
            sign = "🟢" if contrib > 0.3 else "🔴" if contrib < -0.3 else "⚪"
            c1, c2 = st.columns([1, 4])
            with c1:
                st.markdown(f"**{indicator_name}**")
                st.markdown(f"{sign} {contrib:+.2f}")
            with c2:
                st.write(msg)
            st.markdown("")

        st.info("""
**점수 해석 가이드**
- **+4 ~ +5**: 🟢 강한 매수 구간
- **+2 ~ +3**: 🟡 약한 매수 구간
- **-1 ~ +1**: ⚪ 관망 구간
- **-3 ~ -2**: 🟠 약한 매도 구간
- **-5 ~ -4**: 🔴 강한 매도 구간

⚠️ 이 점수는 기술적 지표만을 객관적으로 수치화한 것입니다. 기업 가치·뉴스·시장 상황은 반영되지 않으며, 최종 판단과 책임은 본인에게 있습니다.
        """)

    with tab3:
        st.subheader("📋 종목 정보")
        st.write(f"**종목명:** {display_name}")
        st.write(f"**종목코드:** {symbol}")
        st.write(f"**현재가:** {current_price:,.0f}{unit}")
        if info:
            if info.get('englishName'):
                st.write(f"**영문명:** {info['englishName']}")
            if info.get('market'):
                st.write(f"**시장:** {info['market']}")
            if info.get('listDate'):
                st.write(f"**상장일:** {info['listDate']}")
            if info.get('sharesOutstanding'):
                st.write(f"**발행주식수:** {int(info['sharesOutstanding']):,}주")

def draw_chart(candles, result, name):
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
    fig.suptitle(f'{name} - 기술분석 차트', fontsize=16, fontweight='bold')

    close = candles['close'].astype(float)
    ts = candles['timestamp']

    axes[0].plot(ts, close, label='종가', linewidth=2, color='black')
    axes[0].plot(ts, result['sma20'], label='SMA20', alpha=0.7, linestyle='--')
    axes[0].plot(ts, result['sma50'], label='SMA50', alpha=0.7, linestyle='--')
    axes[0].plot(ts, result['sma200'], label='SMA200', alpha=0.7, linestyle='--')
    axes[0].set_ylabel('가격')
    axes[0].legend(loc='upper left')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(ts, result['rsi'], label='RSI', color='purple', linewidth=2)
    axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.5, label='과매수(70)')
    axes[1].axhline(y=30, color='b', linestyle='--', alpha=0.5, label='과매도(30)')
    axes[1].set_ylabel('RSI')
    axes[1].legend(loc='upper left')
    axes[1].set_ylim([0, 100])
    axes[1].grid(True, alpha=0.3)

    axes[2].bar(ts, result['histogram'], label='MACD Histogram', alpha=0.5, color='gray')
    axes[2].plot(ts, result['macd'], label='MACD', color='blue', linewidth=2)
    axes[2].plot(ts, result['signal_line'], label='Signal', color='red', linestyle='--', linewidth=2)
    axes[2].set_ylabel('MACD')
    axes[2].set_xlabel('날짜')
    axes[2].legend(loc='upper left')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

if __name__ == "__main__":
    main()