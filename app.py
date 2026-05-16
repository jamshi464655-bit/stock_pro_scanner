import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

# ===================== SAFE IMPORT =====================
try:
    import pandas_ta as ta
except ImportError as e:
    st.error("❌ pandas-ta is not installed properly.")
    st.info("Check that requirements.txt has 'pandas-ta==0.3.14b0' and 'numpy==1.26.4'")
    st.stop()

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="EasyCharts Pro - Nifty 500 Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def play_alert():
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-07a.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_stock_symbols():
    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
               "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN", "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND",
               "HCLTECH", "WIPRO", "POWERGRID", "NTPC", "TATAMOTORS", "BAJAJFINSV", "M&M", "TECHM", "ADANIPORTS", "ONGC",
               "TATASTEEL", "COALINDIA", "HINDALCO", "INDUSINDBK", "JSWSTEEL", "GRASIM", "DIVISLAB", "DRREDDY", "CIPLA",
               "ZOMATO", "TRENT", "DMART", "SUZLON", "RVNL", "BEL", "HAL", "IRCTC", "POLYCAB", "DIXON", "PERSISTENT",
               "LTTS", "COFORGE", "AUBANK", "IDFCFIRSTB", "TVSMOTOR", "OBEROIRLTY", "PAGEIND", "PIIND"]
    return sorted(list(set(symbols)))

def analyze_all_indicators(symbols, batch_size=200):
    pre, live, mom = [], [], []
    symbols = symbols[:batch_size]
    tickers = [f"{s}.NS" for s in symbols]

    progress_bar = st.progress(0)
    status = st.empty()

    try:
        status.text(f"📥 Downloading data for {len(tickers)} stocks...")
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False, threads=True)

        for idx, s in enumerate(symbols):
            progress_bar.progress((idx + 1) / len(symbols))
            status.text(f"🔍 Analyzing {s}...")

            try:
                df = data[f"{s}.NS"].copy() if len(tickers) > 1 else data.copy()
                df = df.dropna()
                if len(df) < 150:
                    continue

                ltp = round(df['Close'].iloc[-1], 2)
                prev_close = round(df['Close'].iloc[-2], 2)
                change_pct = round(((ltp - prev_close) / prev_close) * 100, 2)

                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema200 = ta.ema(df['Close'], length=200).iloc[-1]
                adx = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14'].iloc[-1] if not ta.adx(df['High'], df['Low'], df['Close']).empty else 0
                bb = ta.bbands(df['Close'], length=20)
                upper_bb = bb['BBU_20_2.0'].iloc[-1]
                vol_ratio = round(df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1], 2) if df['Volume'].rolling(20).mean().iloc[-1] > 0 else 0

                # Signals
                if ltp > upper_bb and vol_ratio > 1.5 and 60 < rsi < 85:
                    signal = "🟢 STRONG BUY"
                    cat = "live"
                    conf = 85
                elif abs(ltp - ema200) / ema200 < 0.05 and 45 < rsi < 62:
                    signal = "🔵 BUY SETUP"
                    cat = "pre"
                    conf = 65
                elif ltp > ema200 and rsi > 55 and adx > 23:
                    signal = "🔥 MOMENTUM"
                    cat = "mom"
                    conf = 75
                else:
                    continue

                stock = {
                    "Symbol": s, "Signal": signal, "LTP": ltp, "Change%": f"{change_pct}%",
                    "RSI": round(rsi, 1), "Vol Ratio": vol_ratio, "Confidence": f"{conf}%"
                }

                if cat == "live": live.append(stock)
                elif cat == "pre": pre.append(stock)
                elif cat == "mom": mom.append(stock)

            except:
                continue

    except Exception as e:
        st.error(f"Error: {e}")

    progress_bar.empty()
    status.empty()
    return pre, live, mom

# ===================== MAIN UI =====================
st.markdown("<div class='main-header'><h1>📈 EasyCharts Pro - Nifty 500 Scanner</h1></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    st.success(f"Loaded {len(load_stock_symbols())} Stocks")
    batch_size = st.slider("Stocks to Scan", 50, 500, 200, 50)

if st.button('🚀 START MARKET SCAN', type="primary"):
    with st.spinner("Scanning..."):
        pre, live, mom = analyze_all_indicators(load_stock_symbols(), batch_size)

    if live:
        play_alert()
        st.balloons()

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Pre-Breakout", len(pre))
    with col2: st.metric("Live Breakouts", len(live))
    with col3: st.metric("Momentum", len(mom))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🔵 Pre-Breakout")
        st.dataframe(pd.DataFrame(pre), use_container_width=True) if pre else st.info("None found")
    with c2:
        st.subheader("🟢 Live Breakouts")
        st.dataframe(pd.DataFrame(live), use_container_width=True) if live else st.info("None found")
    with c3:
        st.subheader("🔥 Momentum")
        st.dataframe(pd.DataFrame(mom), use_container_width=True) if mom else st.info("None found")

st.caption("Nifty 500 Scanner")
