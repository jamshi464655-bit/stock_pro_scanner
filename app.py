import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time
from datetime import datetime

st.set_page_config(page_title="EasyCharts Pro - Nifty 500 Scanner", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 10px 0;
    }
    .category-header {
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 15px 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 18px;
        padding: 15px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def play_alert():
    audio_html = """
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/beep-07a.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_stock_symbols():
    """Load Nifty 500 stocks"""
    symbols = [
        # Nifty 50
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", 
        "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
        "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "HCLTECH", "WIPRO", "POWERGRID",
        "NTPC", "TATAMOTORS", "BAJAJFINSV", "M&M", "TECHM", "ADANIPORTS", "ONGC", "TATASTEEL",
        "COALINDIA", "HINDALCO", "INDUSINDBK", "JSWSTEEL", "GRASIM", "DIVISLAB", "DRREDDY",
        "CIPLA", "APOLLOHOSP", "BRITANNIA", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO", 
        "TATACONSUM", "SBILIFE", "HDFCLIFE", "ADANIENT", "ADANIGREEN", "TATAPOWER", "PIDILITIND",
        
        # Nifty Next 50
        "ADANIENSOL", "SIEMENS", "HAVELLS", "DLF", "DMART", "INDIGO", "VEDL", "GODREJCP",
        "GAIL", "BOSCHLTD", "CHOLAFIN", "MUTHOOTFIN", "PNB", "CANBK", "RECLTD", "NMDC",
        "ICICIGI", "SRF", "TORNTPHARM", "DABUR", "MARICO", "PEL", "BANKBARODA", "MOTHERSON",
        "SHREECEM", "AMBUJACEM", "TRENT", "INDUSTOWER", "BERGEPAINT", "COLPAL", "LTIM",
        "HINDPETRO", "BPCL", "IOCL", "SAIL", "LUPIN", "BIOCON", "NAUKRI", "ZOMATO", "PAYTM",
        "DIXON", "POLYCAB", "CROMPTON", "VOLTAS", "TVSMOTOR", "ASHOKLEY", "ESCORTS", "MRF",
        "CONCOR", "GMRINFRA",
        
        # Mid Cap 150 (Popular)
        "PERSISTENT", "COFORGE", "LTTS", "MPHASIS", "OFSS", "L&TFH", "SBICARD", "ABCAPITAL",
        "AUBANK", "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "IDFC", "IDEA", "JINDALSTEL",
        "SAIL", "TATACHEM", "UPL", "ADANIPOWER", "APLAPOLLO", "ASTRAL", "CANBK", "CUMMINSIND",
        "DEEPAKNTR", "GODREJPROP", "HDFCAMC", "ICICIPRULI", "IRCTC", "JUBLFOOD", "LAURUSLABS",
        "LICI", "MAX", "METROPOLIS", "NYKAA", "OBEROIRLTY", "PAGEIND", "PIIND", "POLICYBZR",
        "PVR", "SYNGENE", "TATACOMM", "TATACOFFEE", "TIINDIA", "UBL", "MCDOWELL-N", "WHIRLPOOL",
        
        # Small Cap Popular
        "AAVAS", "AEGISCHEM", "AFFLE", "ANGELONE", "ANURAS", "APTUS", "ASAHIINDIA", "ATUL",
        "AUROPHARMA", "AXISCADES", "BAJAJCON", "BALRAMCHIN", "BATAINDIA", "BEL", "BHARATFORG",
        "BIRLACORPN", "BSE", "CAMPUS", "CARBORUNIV", "CENTRALBK", "CESC", "CHAMBLFERT", "CLEAN",
        "CMI", "CRAFTSMAN", "CREDITACC", "CUB", "CYIENT", "DATAPATTNS", "DEEPAKFERT", "DELTACORP",
        "DEVYANI", "DHANUKA", "DHANI", "DIVISLAB", "DREDGECORP", "EASEMYTRIP", "ELECON", "EMAMILTD",
        
        # IT Sector
        "INFY", "TCS", "WIPRO", "HCLTECH", "TECHM", "LTIM", "PERSISTENT", "COFORGE", "MPHASIS",
        "LTTS", "OFSS", "SONATSOFTW", "MINDTREE", "CYIENT", "ROUTE", "MASTEK", "INTELLECT",
        "KPITTECH", "ZENSAR", "ROLTA", "NIIT", "DATAPATTNS", "TATAELXSI", "HAPPSTMNDS",
        
        # Banking & Finance
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "AUBANK",
        "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "RBLBANK", "YESBANK", "PNB", "CANBK",
        "BANKBARODA", "UNIONBANK", "INDIANB", "CENTRALBK", "IOB", "MAHABANK", "BAJFINANCE",
        "BAJAJFINSV", "CHOLAFIN", "MUTHOOTFIN", "SBICARD", "HDFCAMC", "CDSL", "CAMS",
        
        # Pharma
        "SUNPHARMA", "DIVISLAB", "DRREDDY", "CIPLA", "LUPIN", "BIOCON", "TORNTPHARM", "ALKEM",
        "AUROPHARMA", "ABBOTINDIA", "IPCALAB", "LALPATHLAB", "METROPOLIS", "THYROCARE", "SYNGENE",
        "LAURUSLABS", "GRANULES", "NATCOPHARMA", "AJANTPHARM", "GLAXO", "PFIZER",
        
        # Auto
        "MARUTI", "TATAMOTORS", "M&M", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO", "TVSMOTOR",
        "ASHOKLEY", "ESCORTS", "MOTHERSON", "BALKRISIND", "MRF", "APOLLOTYRE", "CEAT",
        "EXIDEIND", "AMARAJABAT", "BOSCHLTD", "SCHAEFFLER", "SKFINDIA", "SUPRAJIT",
        
        # Infrastructure & Construction
        "LT", "ADANIPORTS", "GAIL", "NTPC", "POWERGRID", "COALINDIA", "SAIL", "NMDC",
        "DLF", "OBEROIRLTY", "GODREJPROP", "PRESTIGE", "BRIGADE", "SOBHA", "IRCON", "RVNL",
        "NCC", "KNR", "PNC", "GPIL", "J&KBANK", "GICRE",
        
        # FMCG
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO", "GODREJCP", "COLPAL",
        "TATACONSUM", "UBL", "MCDOWELL-N", "RADICO", "EMAMILTD", "JYOTHYLAB", "VBL", "CCL",
        "GILLETTE", "HONASA", "VARUNbeverages",
        
        # Retail & Consumption
        "DMART", "TRENT", "TITAN", "RELAXO", "BATAINDIA", "ABFRL", "SHOPERSTOP", "NYKAA",
        "JUBLFOOD", "WESTLIFE", "DEVYANI", "SAPPHIRE", "RAYMOND", "SIYARAM",
        
        # Telecom & Media
        "BHARTIARTL", "INDIGO", "HATHWAY", "DEN", "ZEEL", "PVR", "SAREGAMA", "NAZARA",
        "NETWORK18", "TV18BRDCST",
        
        # Metals & Mining
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "SAIL", "NMDC", "COALINDIA", "JINDALSTEL",
        "NATIONALUM", "HINDZINC", "RATNAMANI", "APARINDS", "WELSPUNIND", "WELCORP",
        
        # Cement
        "ULTRACEMCO", "AMBUJACEM", "SHREECEM", "DALMIACEM", "RAMCOCEM", "JKCEMENT", "HEIDELBERG",
        "INDIACEM", "ORIENTCEM", "STARCEM",
        
        # Energy & Oil
        "RELIANCE", "ONGC", "BPCL", "IOCL", "HINDPETRO", "GAIL", "PETRONET", "GUJGASLTD",
        "IGL", "MGL", "ADANIGAS", "AEGISLOG", "ATGL",
        
        # Chemicals
        "UPL", "PIDILITIND", "SRF", "DEEPAKNTR", "AARTI", "BALRAMCHIN", "GNFC", "CHAMBLFERT",
        "NAVINFLUOR", "ALKYLAMINE", "TATACHEM", "TATACHEMICALS", "AKZOINDIA",
        
        # Capital Goods
        "LT", "SIEMENS", "ABB", "CUMMINSIND", "BOSCHLTD", "BHEL", "BEL", "HAL", "GRINDWELL",
        "KPIT", "THERMAX", "CARBORUNIV", "KALPATPOWR", "SKFINDIA", "TIMKEN",
        
        # Consumer Durables
        "VOLTAS", "HAVELLS", "CROMPTON", "DIXON", "POLYCAB", "WHIRLPOOL", "BLUESTARCO",
        "SYMPHONY", "ORIENTELEC", "VGUARD", "KEI",
        
        # Textiles
        "RAYMOND", "ARVIND", "SIYARAM", "WELSPUNIND", "VARDHACRLC", "TRIDENT", "KPR",
        
        # Hotels & Tourism
        "INDHOTEL", "LEMONTREE", "CHALET", "EIH", "MAHINDCIE",
        
        # Logistics
        "CONCOR", "VRL", "MAHLOG", "TCI", "AEGISLOG", "ALLCARGO", "BLUEDART", "GATI",
        
        # New Age Tech
        "ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "CARTRADE", "EASEMYTRIP", "ROUTE",
        "ANGELONE", "DELHIVERY", "FINO",
        
        # Additional Quality Stocks
        "APLAPOLLO", "ASTRAL", "ATUL", "CLEAN", "FINEORG", "HBLPOWER", "HERITGFOOD",
        "HONAUT", "JKPAPER", "KAJARIACER", "KANSAINER", "LAURUSLABS", "LINDEINDIA",
        "LUXIND", "METROBRAND", "MFSL", "NAVINFLUOR", "PAGEIND", "PIIND", "PNBHOUSING",
        "POONAWALLA", "PRAJIND", "RAJESHEXPO", "SIS", "SOLARINDS", "SUDARSCHEM",
        "SUNTV", "SUPREMEIND", "SWANENERGY", "TANLA", "TATAINVEST", "TTKPRESTIG",
        "UTIAMC", "VIPIND", "VINATIORGA", "WESTLIFE", "ZYDUSLIFE"
    ]
    
    # Remove duplicates
    symbols = list(set(symbols))
    return sorted(symbols)

def analyze_all_indicators(symbols, batch_size=100):
    pre_breakout, live_breakout, momentum = [], [], []
    
    symbols = symbols[:batch_size]
    tickers = [f"{s}.NS" for s in symbols]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"📊 Downloading data for {len(tickers)} stocks...")
        data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False, threads=True)
        
        for idx, s in enumerate(symbols):
            try:
                progress = (idx + 1) / len(symbols)
                progress_bar.progress(progress)
                status_text.text(f"🔍 Analyzing {s} ({idx+1}/{len(symbols)})...")
                
                if len(tickers) == 1:
                    df = data.copy()
                else:
                    df = data[f"{s}.NS"].copy()
                
                df = df.dropna()
                
                if len(df) < 150:
                    continue
                
                ltp = round(df['Close'].iloc[-1], 2)
                prev_close = round(df['Close'].iloc[-2], 2)
                change_pct = round(((ltp - prev_close) / prev_close) * 100, 2)
                
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                
                ema_200 = ta.ema(df['Close'], length=200).iloc[-1]
                ema_50 = ta.ema(df['Close'], length=50).iloc[-1]
                ema_20 = ta.ema(df['Close'], length=20).iloc[-1]
                
                adx_df = ta.adx(df['High'], df['Low'], df['Close'])
                adx = adx_df['ADX_14'].iloc[-1] if adx_df is not None else 0
                
                bbands = ta.bbands(df['Close'], length=20, std=2)
                upper_bb = bbands['BBU_20_2.0'].iloc[-1]
                lower_bb = bbands['BBL_20_2.0'].iloc[-1]
                middle_bb = bbands['BBM_20_2.0'].iloc[-1]
                
                vol_ma_20 = df['Volume'].rolling(20).mean().iloc[-1]
                curr_vol = df['Volume'].iloc[-1]
                vol_ratio = round(curr_vol / vol_ma_20, 2) if vol_ma_20 > 0 else 0
                
                macd = ta.macd(df['Close'])
                macd_line = macd['MACD_12_26_9'].iloc[-1] if macd is not None else 0
                signal_line = macd['MACDs_12_26_9'].iloc[-1] if macd is not None else 0
                
                supertrend = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                st_trend = supertrend['SUPERTd_10_3.0'].iloc[-1] if supertrend is not None else 0
                
                signal = "🟡 WAIT"
                reason = "Consolidating"
                category = None
                confidence = 0
                
                if (ltp > upper_bb and 
                    curr_vol > vol_ma_20 * 1.5 and 
                    rsi > 60 and rsi < 85 and 
                    ltp > ema_20 and
                    st_trend == 1):
                    
                    signal = "🟢 STRONG BUY"
                    reason = f"BB Breakout + {vol_ratio}x Volume + RSI {round(rsi, 1)}"
                    category = "live"
                    confidence = min(95, 70 + (vol_ratio * 5))
                
                elif (ema_200 * 0.97 <= ltp <= ema_200 * 1.05 and 
                      rsi > 45 and rsi < 60 and
                      ltp > ema_50 and
                      vol_ratio > 0.8):
                    
                    signal = "🔵 BUY SETUP"
                    reason = f"Near 200 EMA Support | RSI {round(rsi, 1)}"
                    category = "pre"
                    confidence = 65
                
                elif (ltp > ema_200 and 
                      ltp > ema_50 and 
                      ltp > ema_20 and
                      rsi > 55 and 
                      adx > 25 and
                      macd_line > signal_line):
                    
                    signal = "🔥 MOMENTUM"
                    reason = f"Triple EMA + ADX {round(adx, 1)} + MACD Bull"
                    category = "mom"
                    confidence = 75
                
                elif (ltp < ema_20 and 
                      ltp > ema_50 and 
                      rsi > 40 and rsi < 55 and
                      ltp > ema_200):
                    
                    signal = "🟠 PULLBACK"
                    reason = f"Pullback to EMA20 | RSI {round(rsi, 1)}"
                    category = "pre"
                    confidence = 60
                
                elif ltp < ema_200 or rsi < 30:
                    signal = "🔴 AVOID"
                    reason = "Downtrend | Below 200 EMA" if ltp < ema_200 else "Oversold"
                    confidence = 0
                
                stock_res = {
                    "Symbol": s,
                    "Signal": signal,
                    "LTP": ltp,
                    "Change%": f"{change_pct}%",
                    "RSI": round(rsi, 1),
                    "ADX": round(adx, 1),
                    "Vol Ratio": vol_ratio,
                    "Confidence": f"{round(confidence)}%",
                    "Reason": reason
                }
                
                if category == "live":
                    live_breakout.append(stock_res)
                elif category == "pre":
                    pre_breakout.append(stock_res)
                elif category == "mom":
                    momentum.append(stock_res)
                
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"Error during analysis: {e}")
    
    return pre_breakout, live_breakout, momentum

st.markdown("""
    <div class='main-header'>
        <h1>📈 EasyCharts Pro - Nifty 500 Scanner</h1>
        <p>AI-Powered Multi-Indicator Stock Scanner (500+ Stocks)</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Scanner Settings")
    
    all_symbols = load_stock_symbols()
    st.info(f"📊 Total Stocks Available: {len(all_symbols)}")
    
    batch_size = st.slider("Stocks to Scan", 50, 500, 100, 50)
    
    auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
    refresh_interval = st.selectbox("Refresh Interval (mins)", [1, 2, 5, 10], index=0)
    
    show_details = st.checkbox("Show Detailed Metrics", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 Signal Legend")
    st.markdown("""
    - 🟢 **STRONG BUY**: Live breakout
    - 🔵 **BUY SETUP**: Pre-breakout
    - 🔥 **MOMENTUM**: Strong trend
    - 🟠 **PULLBACK**: Buy on dips
    - 🔴 **AVOID**: Downtrend
    """)
    
    st.markdown("---")
    st.info(f"⏰ Current Time: {datetime.now().strftime('%I:%M:%S %p')}")

if st.button('🚀 START MARKET SCAN', key='scan_button'):
    try:
        symbols = load_stock_symbols()
        
        if not symbols:
            st.error("❌ No symbols loaded!")
        else:
            st.info(f"📋 Scanning {min(batch_size, len(symbols))} stocks from Nifty 500...")
            
            with st.spinner('🔍 Scanning markets...'):
                pre, live, mom = analyze_all_indicators(symbols, batch_size)
            
            if live:
                play_alert()
                st.balloons()
                st.success(f"🎯 Found {len(live)} Live Breakouts!")
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.markdown(f"""
                    <div class='stat-box'>
                        <h2>{len(pre)}</h2>
                        <p>Pre-Breakout Setups</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                    <div class='stat-box'>
                        <h2>{len(live)}</h2>
                        <p>Live Breakouts</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                st.markdown(f"""
                    <div class='stat-box'>
                        <h2>{len(mom)}</h2>
                        <p>Momentum Stocks</p>
                    </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("<div class='category-header' style='background:#FF9800;'>🔵 Pre-Breakout Setups</div>", unsafe_allow_html=True)
                if pre:
                    df_pre = pd.DataFrame(pre)
                    if not show_details:
                        df_pre = df_pre[['Symbol', 'Signal', 'LTP', 'RSI', 'Confidence']]
                    st.dataframe(df_pre, use_container_width=True, height=400)
                else:
                    st.info("No pre-breakout setups found")
            
            with col2:
                st.markdown("<div class='category-header' style='background:#4CAF50;'>🟢 Live Breakouts</div>", unsafe_allow_html=True)
                if live:
                    df_live = pd.DataFrame(live)
                    if not show_details:
                        df_live = df_live[['Symbol', 'Signal', 'LTP', 'Vol Ratio', 'Confidence']]
                    st.dataframe(df_live, use_container_width=True, height=400)
                else:
                    st.info("No live breakouts found")
            
            with col3:
                st.markdown("<div class='category-header' style='background:#2196F3;'>🔥 Strong Momentum</div>", unsafe_allow_html=True)
                if mom:
                    df_mom = pd.DataFrame(mom)
                    if not show_details:
                        df_mom = df_mom[['Symbol', 'Signal', 'LTP', 'ADX', 'Confidence']]
                    st.dataframe(df_mom, use_container_width=True, height=400)
                else:
                    st.info("No momentum stocks found")
            
            st.markdown("---")
            col_export1, col_export2, col_export3 = st.columns(3)
            
            if pre:
                with col_export1:
                    csv_pre = pd.DataFrame(pre).to_csv(index=False)
                    st.download_button("📥 Download Pre-Breakout", csv_pre, "pre_breakout.csv", "text/csv")
            
            if live:
                with col_export2:
                    csv_live = pd.DataFrame(live).to_csv(index=False)
                    st.download_button("📥 Download Live Breakout", csv_live, "live_breakout.csv", "text/csv")
            
            if mom:
                with col_export3:
                    csv_mom = pd.DataFrame(mom).to_csv(index=False)
                    st.download_button("📥 Download Momentum", csv_mom, "momentum.csv", "text/csv")
            
            st.success(f"✅ Scan completed at {time.strftime('%I:%M:%S %p')}")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")

if auto_refresh:
    time.sleep(refresh_interval * 60)
    st.rerun()
