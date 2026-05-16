import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="EasyCharts Pro - Ultra Scanner", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .header {background: linear-gradient(135deg, #6b46c1, #7c3aed); padding: 35px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.3);}
    .scan-btn {background: linear-gradient(135deg, #ef4444, #f87171); color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 18px; margin: 15px 0; cursor: pointer;}
    .metric-card {padding: 20px; border-radius: 15px; text-align: center; color: white; font-weight: bold; box-shadow: 0 5px 15px rgba(0,0,0,0.2); min-height: 140px;}
    .nifty-card {background: linear-gradient(135deg, #a855f7, #c084fc);}
    .bank-card {background: linear-gradient(135deg, #22c55e, #86efac); color: black;}
    .panel {background: linear-gradient(135deg, #f59e0b, #fb923c); color: white; padding: 12px; border-radius: 10px; font-weight: bold; text-align: center; margin: 15px 0;}
    .status-bar {background: #ecfdf5; color: #166534; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin: 15px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🚀 EasyCharts Pro - Ultra Scanner</h1>
    <p>AI-Powered Multi-Index & Option Master Scanner</p>
</div>
""", unsafe_allow_html=True)

def fetch_analysis(ticker, name):
    try:
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        if df.empty or len(df) < 30: return None
        
        df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
        df['EMA13'] = df['Close'].ewm(span=13, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['EMA55'] = df['Close'].ewm(span=55, adjust=False).mean()
        
        last = df.iloc[-1]
        price = round(float(last['Close']), 2)
        
        # Simple RSI calculation (without pandas_ta)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        strike_gap = 50 if "NIFTY" in name else 100
        atm_strike = round(price / strike_gap) * strike_gap
        
        bullish = (price > last['EMA8'] > last['EMA13'] > last['EMA21'] > last['EMA55'])
        bearish = (price < last['EMA8'] < last['EMA13'] < last['EMA21'] < last['EMA55'])
        
        if bullish:
            status, style, strike = "STRONG BUY (CE) 🚀", "buy-zone", f"{atm_strike} CE"
        elif bearish:
            status, style, strike = "STRONG SELL (PE) 📉", "sell-zone", f"{atm_strike} PE"
        else:
            status, style, strike = "NO TREND ⏳", "wait-zone", "Searching..."
            
        return {
            "Name": name, "Price": price, "Status": status, "Style": style, "Strike": strike,
            "RSI": round(rsi, 1)
        }
    except:
        return None

if st.button("🚀 START MARKET SCAN", type="primary", use_container_width=True):
    with st.spinner("Scanning Market..."):
        indices = [("^NSEI", "NIFTY 50"), ("^NSEBANK", "BANK NIFTY")]
        results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_analysis, idx[0], idx[1]) for idx in indices]
            for f in as_completed(futures):
                res = f.result()
                if res: results.append(res)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="panel">NIFTY 50</div>', unsafe_allow_html=True)
            if results:
                st.write(f"Price: {results[0]['Price']}")
                st.write(results[0]['Status'])
        with col2:
            st.markdown('<div class="panel">BANK NIFTY</div>', unsafe_allow_html=True)
            if len(results) > 1:
                st.write(f"Price: {results[1]['Price']}")
                st.write(results[1]['Status'])

        st.success(f"✅ Scan Completed at {datetime.now().strftime('%I:%M:%S %p')}")

else:
    st.info("👆 'START MARKET SCAN' ബട്ടൺ ക്ലിക്ക് ചെയ്യുക")

st.caption("Beautiful Ultra Scanner • No pandas_ta dependency • Stable on Streamlit Cloud")
