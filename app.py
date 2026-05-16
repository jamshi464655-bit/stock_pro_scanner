import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import time

# ===================== SAFE IMPORT =====================
try:
    import pandas_ta as ta
except ImportError:
    st.error("❌ pandas-ta package is not installed!")
    st.info("Please ensure your requirements.txt contains: **pandas-ta==0.3.14b0**")
    st.stop()

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="EasyCharts Pro - Nifty 500 Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
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
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 19px;
        padding: 16px;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def play_alert():
    st.markdown("""
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/beep-07a.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_stock_symbols():
    symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL",
        "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN", "SUNPHARMA", "ULTRACEMCO",
        "BAJFINANCE", "NESTLEIND", "HCLTECH", "WIPRO", "POWERGRID", "NTPC", "TATAMOTORS", "BAJAJFINSV",
        "M&M", "TECHM", "ADANIPORTS", "ONGC", "TATASTEEL", "COALINDIA", "HINDALCO", "INDUSINDBK",
        "JSWSTEEL", "GRASIM", "DIVISLAB", "DRREDDY", "CIPLA", "APOLLOHOSP", "BRITANNIA", "EICHERMOT",
        "HEROMOTOCO", "BAJAJ-AUTO", "TATACONSUM", "SBILIFE", "HDFCLIFE", "ADANIENT", "ADANIGREEN",
        "TATAPOWER", "PIDILITIND", "SIEMENS", "HAVELLS", "DLF", "DMART", "INDIGO", "VEDL", "GODREJCP",
        "GAIL", "BOSCHLTD", "CHOLAFIN", "MUTHOOTFIN", "PNB", "CANBK", "RECLTD", "NMDC", "ICICIGI",
        "SRF", "TORNTPHARM", "DABUR", "MARICO", "PEL", "BANKBARODA", "MOTHERSON", "SHREECEM",
        "AMBUJACEM", "TRENT", "INDUSTOWER", "BERGEPAINT", "COLPAL", "LTIM", "HINDPETRO", "BPCL",
        "IOCL", "SAIL", "LUPIN", "BIOCON", "ZOMATO", "DIXON", "POLYCAB", "TVSMOTOR", "PERSISTENT",
        "COFORGE", "LTTS", "AUBANK", "IDFCFIRSTB", "IRCTC", "JUBLFOOD", "OBEROIRLTY", "PAGEIND",
        "PIIND", "SYNGENE", "UBL", "BEL", "HAL", "SUZLON", "RVNL", "TRIDENT", "VBL", "ZEEL",
        "AAVAS", "AFFLE", "ANGELONE", "ATUL", "AUROPHARMA", "BATAINDIA", "BHARATFORG", "CLEAN",
        "CUMMINSIND", "CYIENT", "DEEPAKNTR", "GODREJPROP", "HDFCAMC", "LAURUSLABS", "MAXHEALTH",
        "NYKAA", "SONACOMS", "TATATECH", "ALKEM", "ABB", "ADANIENSOL", "APARINDS", "BHEL",
        "CARBORUNIV", "CDSL", "EMAMILTD", "HONAUT", "IGL", "JKCEMENT", "KPITTECH", "LINDEINDIA",
        "MAZDOCK", "PRAJIND", "SOLARINDS", "SUPREMEIND", "THERMAX", "VIPIND", "ZYDUSLIFE"
    ]
    return sorted(list(set(symbols)))

def analyze_all_indicators(symbols, batch_size=250):
    pre_breakout, live_breakout, momentum = [], [], []
    symbols = symbols[:batch_size]
    tickers = [f"{s}.NS" for s in symbols]

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text(f"📥 Downloading data for {len(tickers)} stocks...")
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', 
                          progress=False, threads=True)

        for idx, s in enumerate(symbols):
            progress = (idx + 1) / len(symbols)
            progress_bar.progress(progress)
            status_text.text(f"🔍 Analyzing {s}...")

            try:
                df = data[f"{s}.NS"].copy() if len(tickers) > 1 else data.copy()
                df = df.dropna()

                if len(df) < 150:
                    continue

                ltp = round(df['Close'].iloc[-1], 2)
                prev_close = round(df['Close'].iloc[-2], 2)
                change_pct = round(((ltp - prev_close) / prev_close) * 100, 2)

                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                ema20 = ta.ema(df['Close'], length=20).iloc[-1]
                ema50 = ta.ema(df['Close'], length=50).iloc[-1]
                ema200 = ta.ema(df['Close'], length=200).iloc[-1]

                adx_df = ta.adx(df['High'], df['Low'], df['Close'])
                adx = adx_df['ADX_14'].iloc[-1] if not adx_df.empty else 0

                bb = ta.bbands(df['Close'], length=20, std=2)
                upper_bb = bb['BBU_20_2.0'].iloc[-1]

                vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
                vol_ratio = round(df['Volume'].iloc[-1] / vol_ma, 2) if vol_ma > 0 else 0

                # Signal Logic
                if (ltp > upper_bb and vol_ratio > 1.5 and 60 < rsi < 85):
                    signal = "🟢 STRONG BUY"
                    reason = f"Breakout + {vol_ratio}x Volume"
                    cat = "live"
                    conf = min(95, 70 + int(vol_ratio * 6))

                elif (abs(ltp - ema200) / ema200 <= 0.05 and 45 < rsi < 62):
                    signal = "🔵 BUY SETUP"
                    reason = "Near 200 EMA Support"
                    cat = "pre"
                    conf = 68

                elif (ltp > ema200 and ltp > ema50 and rsi > 55 and adx > 23):
                    signal = "🔥 MOMENTUM"
                    reason = f"Strong Trend | ADX {round(adx,1)}"
                    cat = "mom"
                    conf = 78
                else:
                    continue

                stock = {
                    "Symbol": s,
                    "Signal": signal,
                    "LTP": ltp,
                    "Change%": f"{change_pct}%",
                    "RSI": round(rsi, 1),
                    "Vol Ratio": vol_ratio,
                    "ADX": round(adx, 1),
                    "Confidence": f"{conf}%",
                    "Reason": reason
                }

                if cat == "live":
                    live_breakout.append(stock)
                elif cat == "pre":
                    pre_breakout.append(stock)
                elif cat == "mom":
                    momentum.append(stock)

            except:
                continue

        progress_bar.empty()
        status_text.empty()

    except Exception as e:
        st.error(f"Error during analysis: {e}")

    return pre_breakout, live_breakout, momentum

# ===================== UI =====================
st.markdown("""
    <div class='main-header'>
        <h1>📈 EasyCharts Pro - Nifty 500 Scanner</h1>
        <p>Real-time Breakout & Momentum Scanner</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Scanner Settings")
    all_symbols = load_stock_symbols()
    st.success(f"✅ Loaded {len(all_symbols)} Stocks")

    batch_size = st.slider("Stocks to Scan", 50, 500, 250, 25)
    st.markdown("---")
    st.markdown("**Signal Legend**")
    st.markdown("""
    - 🟢 **STRONG BUY** → Live Breakout  
    - 🔵 **BUY SETUP** → Pre-Breakout  
    - 🔥 **MOMENTUM** → Strong Trend
    """)

if st.button('🚀 START MARKET SCAN', type="primary"):
    with st.spinner("Scanning Nifty 500 stocks..."):
        pre, live, mom = analyze_all_indicators(load_stock_symbols(), batch_size)

    if live:
        play_alert()
        st.balloons()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='stat-box'><h2>{len(pre)}</h2><p>Pre-Breakout</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-box'><h2>{len(live)}</h2><p>Live Breakouts</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-box'><h2>{len(mom)}</h2><p>Momentum</p></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🔵 Pre-Breakout Setups")
        if pre:
            st.dataframe(pd.DataFrame(pre), use_container_width=True, height=450)
        else:
            st.info("No pre-breakout setups found")
    with c2:
        st.subheader("🟢 Live Breakouts")
        if live:
            st.dataframe(pd.DataFrame(live), use_container_width=True, height=450)
        else:
            st.info("No live breakouts found")
    with c3:
        st.subheader("🔥 Momentum Stocks")
        if mom:
            st.dataframe(pd.DataFrame(mom), use_container_width=True, height=450)
        else:
            st.info("No momentum stocks found")

    st.success(f"✅ Scan Completed at {datetime.now().strftime('%I:%M:%S %p')}")

st.caption("Nifty 500 Scanner | Built for Indian Traders")
