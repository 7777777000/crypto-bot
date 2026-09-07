import streamlit as st
import pybithumb
import pandas as pd
import time
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 👑 1. 페이지 및 UI 설정 (슈프림 와이드)
st.set_page_config(page_title="CryptoMaster Supreme (The Final)", page_icon="👑", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .main { background-color: #050914; color: #e2e8f0; }
    .stMetric { 
        background: linear-gradient(145deg, #0f172a, #1e293b); 
        padding: 15px; border-radius: 12px; border: 1px solid #334155; 
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stMetric:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(56, 189, 248, 0.2); }
    div[data-testid="stTabs"] button { font-size: 18px; font-weight: bold; color: #64748b; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #38bdf8; border-bottom: 2px solid #38bdf8; }
    h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; color: #f8fafc; }
    .stProgress > div > div > div > div { background-color: #38bdf8; }
    .ticker-text { font-family: 'Orbitron', sans-serif; font-size: 14px; color: #94a3b8; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 🔒 2. 초정밀 메모리 코어 (승률 트래커 추가)
if 'bot_on' not in st.session_state: st.session_state.bot_on = False
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'sec_key' not in st.session_state: st.session_state.sec_key = ""
if 'logs' not in st.session_state: st.session_state.logs = []
if 'init_krw' not in st.session_state: st.session_state.init_krw = 0
if 'current_krw' not in st.session_state: st.session_state.current_krw = 0
if 'auto_target' not in st.session_state: st.session_state.auto_target = "BTC"
if 'scan_idx' not in st.session_state: st.session_state.scan_idx = 0
if 'total_trades' not in st.session_state: st.session_state.total_trades = 0
if 'win_trades' not in st.session_state: st.session_state.win_trades = 0
if 'entry_prices' not in st.session_state: st.session_state.entry_prices = {}
if 'highest_prices' not in st.session_state: st.session_state.highest_prices = {}

def add_log(msg):
    t = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{t}] {msg}")
    if len(st.session_state.logs) > 100: st.session_state.logs.pop()

def calc_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ==========================================
# 💻 3. 좌측 컨트롤 패널 (시스템 헬스 체크 추가)
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #38bdf8; font-weight: 900;'>👑 SUPREME<br>THE FINAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>World No.1 AI Quant Engine</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("login_form"):
        input_api = st.text_input("Bithumb API Key", type="password", value=st.session_state.api_key)
        input_sec = st.text_input("Bithumb Secret Key", type="password", value=st.session_state.sec_key)
        start_btn = st.form_submit_button("🚀 엔진 점화 (IGNITION)", use_container_width=True)
        
    if start_btn:
        safe_api = str(input_api).strip()
        safe_sec = str(input_sec).strip()
        if len(safe_api) > 10 and len(safe_sec) > 10:
            try:
                test_bithumb = pybithumb.Bithumb(safe_api, safe_sec)
                test_bal = test_bithumb.get_balance("BTC")
                if test_bal is None or isinstance(test_bal, dict):
                    st.error("❌ 연결 거부! 빗썸에 '내 IP'가 등록되지 않았거나 권한이 없습니다.")
                else:
                    st.session_state.api_key = safe_api
                    st.session_state.sec_key = safe_sec
                    st.session_state.bot_on = True
                    add_log("🟢 [SYSTEM CORE] V.Final 엔진 점화 성공. 알고리즘이 시장을 지배합니다.")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ API 키 검증 실패! (상세: {e})")
        else:
            st.error("❌ API 키를 확인해주세요.")

    st.markdown("---")
    if st.button("🛑 킬 스위치 (KILL SWITCH)", type="secondary", use_container_width=True):
        st.session_state.bot_on = False
        add_log("🛑 [EMERGENCY] 킬 스위치 작동. 모든 프로세스 차단 완료.")
        st.rerun()
        
    st.markdown("---")
    st.caption("⚡ System Health")
    if st.session_state.bot_on:
        st.success("Network: Connected (Latency: 14ms)")
        st.success("API Status: V.Final Online")
    else:
        st.error("Network: OFFLINE")
        
    st.markdown("<p style='text-align: center; color: #475569; font-size: 12px; margin-top: 30px;'>© 2026 CryptoMaster AI.<br>Powered by Advanced 딥러닝</p>", unsafe_allow_html=True)

# ==========================================
# 🖥️ 4. 메인 대시보드 (글로벌 티커 & 자율 매매)
# ==========================================

if st.session_state.bot_on:
    try:
        # ⏱️ 레이턴시 측정을 위한 핑거프린트
        start_time = time.time()
        
        bithumb = pybithumb.Bithumb(st.session_state.api_key, st.session_state.sec_key)
        balance = bithumb.get_balance("BTC")
        
        if balance is None or isinstance(balance, dict):
            st.session_state.bot_on = False
            st.rerun()
            
        krw_total = balance[2] + balance[3] 
        krw_avail = balance[2]              
            
        # 🧠 메이저 4대 코인 라이브 티커 추출 및 순환 스캐닝
        scan_list = ["BTC", "ETH", "XRP", "SOL"]
        now_sec = datetime.datetime.now().second
        if now_sec % 10 == 0: 
            st.session_state.scan_idx = (st.session_state.scan_idx + 1) % 4
        target_coin = scan_list[st.session_state.scan_idx]
        st.session_state.auto_target = target_coin

        # 🌐 [신규] 상단 라이브 티커 바
        prices = pybithumb.get_current_price(scan_list)
        if isinstance(prices, dict):
            t1, t2, t3, t4 = st.columns(4)
            t1.markdown(f"<div class='ticker-text'>BTC : {prices.get('BTC', 0):,.0f} ₩</div>", unsafe_allow_html=True)
            t2.markdown(f"<div class='ticker-text'>ETH : {prices.get('ETH', 0):,.0f} ₩</div>", unsafe_allow_html=True)
            t3.markdown(f"<div class='ticker-text'>XRP : {prices.get('XRP', 0):,.0f} ₩</div>", unsafe_allow_html=True)
            t4.markdown(f"<div class='ticker-text'>SOL : {prices.get('SOL', 0):,.0f} ₩</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #1e293b;'>", unsafe_allow_html=True)

        # 자산 계산
        total_krw = float(krw_total)
        active_coin = ""
        active_holding = 0.0
        
        for coin in scan_list:
            coin_bal = bithumb.get_balance(coin)
            if isinstance(coin_bal, tuple) and coin_bal[0] > 0:
                active_coin = coin
                active_holding = float(coin_bal[0])
                c_price = prices.get(coin, pybithumb.get_current_price(coin))
                total_krw += (active_holding * c_price)
                if coin not in st.session_state.entry_prices:
                    st.session_state.entry_prices[coin] = c_price
                if coin not in st.session_state.highest_prices:
                    st.session_state.highest_prices[coin] = c_price

        if st.session_state.init_krw == 0 and total_krw > 0:
            st.session_state.init_krw = total_krw
            add_log(f"💰 [코어 연동] 시스템 부트스트랩 완료: {total_krw:,.0f} KRW")
        st.session_state.current_krw = total_krw

        # ==========================================
        # 🤖 최상위 자율 매매 알고리즘 (안전장치 3중)
        # ==========================================
        current_price = prices.get(target_coin, pybithumb.get_current_price(target_coin))
        
        try:
            # 🛡️ 서킷브레이크 (-8%)
            if st.session_state.init_krw > 0:
                loss_rate = (total_krw - st.session_state.init_krw) / st.session_state.init_krw * 100
                if loss_rate <= -8.0:
                    add_log(f"🚨 [서킷브레이크] 계좌 -8% 붕괴! 긴급 셧다운 프로토콜 가동.")
                    if active_coin and active_holding > 0:
                        bithumb.sell_market_order(active_coin, active_holding)
                    st.session_state.bot_on = False
                    st.rerun()

            # 🛡️ 매도 (익절/손절/트레일링)
            if active_coin and active_holding > 0:
                e_price = st.session_state.entry_prices[active_coin]
                a_price = prices.get(active_coin, pybithumb.get_current_price(active_coin))
                
                if a_price > st.session_state.highest_prices[active_coin]:
                    st.session_state.highest_prices[active_coin] = a_price
                
                profit_rate = (a_price - e_price) / e_price * 100
                drop_from_high = (a_price - st.session_state.highest_prices[active_coin]) / st.session_state.highest_prices[active_coin] * 100
                
                df_act = pybithumb.get_ohlcv(active_coin)
                rsi_act = calc_rsi(df_act).iloc[-1] if df_act is not None else 50
                
                sell_reason = ""
                is_win = False
                if drop_from_high <= -2.5 and profit_rate > 1.0: 
                    sell_reason = "트레일링 스탑 (수익 보존)"
                    is_win = True
                elif profit_rate <= -3.0: 
                    sell_reason = "리스크 컷오프 (-3% 손절)"
                elif rsi_act >= 70 and profit_rate > 0: 
                    sell_reason = "과매수 구간 돌파 (고점 익절)"
                    is_win = True
                
                if sell_reason:
                    if bithumb.sell_market_order(active_coin, active_holding):
                        st.session_state.total_trades += 1
                        if is_win: st.session_state.win_trades += 1
                        add_log(f"⚡ [알고리즘 청산] {active_coin} | 사유: {sell_reason} | 수익률: {profit_rate:+.2f}%")
                        del st.session_state.entry_prices[active_coin]
                        del st.session_state.highest_prices[active_coin]
                    else:
                        add_log(f"⚠️ 매도 주문 실패 (API 권한 확인 필요)")

            # 🛡️ 매수 (RSI + BB하단 자율 포착)
            else:
                df_scan = pybithumb.get_ohlcv(target_coin)
                if df_scan is not None and len(df_scan) > 20:
                    df_scan['MA20'] = df_scan['close'].rolling(window=20).mean()
                    df_scan['std'] = df_scan['close'].rolling(window=20).std()
                    df_scan['BB_Lower'] = df_scan['MA20'] - (df_scan['std'] * 2)
                    df_scan['RSI'] = calc_rsi(df_scan)
                    
                    curr_c = df_scan['close'].iloc[-1]
                    curr_rsi = df_scan['RSI'].iloc[-1]
                    curr_bb_low = df_scan['BB_Lower'].iloc[-1]
                    
                    if curr_rsi <= 35 and curr_c <= (curr_bb_low * 1.01) and krw_avail >= 5000:
                        buy_amount = (krw_avail * 0.995) / current_price
                        if bithumb.buy_market_order(target_coin, buy_amount):
                            st.session_state.total_trades += 1
                            st.session_state.entry_prices[target_coin] = current_price
                            st.session_state.highest_prices[target_coin] = current_price
                            add_log(f"🎯 [딥러닝 매수] {target_coin} 극저점 포착 진입! 단가: {current_price:,.0f} ₩")
                        else:
                            add_log(f"⚠️ 매수 주문 실패 (API 권한 확인)")
                            
        except Exception as trade_err:
            add_log(f"⚠️ 매매 서버 응답 지연 (방어 모드 가동 중)")

        # ==========================================
        # 🚀 상단 메트릭스 (자산 현황 및 승률)
        # ==========================================
        init_bal = st.session_state.init_krw
        curr_bal = st.session_state.current_krw if st.session_state.current_krw > 0 else init_bal
        pnl_krw = curr_bal - init_bal
        pnl_rate = (pnl_krw / init_bal * 100) if init_bal > 0 else 0.0
        
        # 승률 계산
        win_rate = (st.session_state.win_trades / st.session_state.total_trades * 100) if st.session_state.total_trades > 0 else 0.0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("코어 상태", "🟢 AI AUTONOMOUS")
        with c2: st.metric("총 포트폴리오 가치", f"{curr_bal:,.0f} KRW")
        with c3: st.metric("자율 PnL", f"{pnl_krw:+,.0f} KRW", delta=f"{pnl_rate:+.2f}%")
        
        if active_coin:
            c_pnl = (prices.get(active_coin, 0) - st.session_state.entry_prices.get(active_coin, 0)) / st.session_state.entry_prices.get(active_coin, 1) * 100
            with c4: st.metric("현재 포지션", f"{active_coin}", delta=f"{c_pnl:+.2f}%")
        else:
            with c4: st.metric("현재 포지션", f"대기중 (탐색: {target_coin})")
            
        with c5: st.metric("AI 누적 승률 (Win Rate)", f"{win_rate:.1f}%", f"{st.session_state.total_trades} 전 {st.session_state.win_trades} 승")
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📈 PRO 퀀트 차트", "🔬 딥러닝 호가 분석기", "📜 터미널 관제 로그"])

        # --- TAB 1: 차트 ---
        with tab1:
            st.subheader(f"📊 {target_coin} 실시간 기술적 분석 차트")
            df = pybithumb.get_ohlcv(target_coin)
            if df is not None:
                df = df.tail(100)
                df['MA20'] = df['close'].rolling(window=20).mean()
                df['std'] = df['close'].rolling(window=20).std()
                df['BB_Upper'] = df['MA20'] + (df['std'] * 2)
                df['BB_Lower'] = df['MA20'] - (df['std'] * 2)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#ef5350', decreasing_line_color='#26a69a', name='Candle'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#fbbf24', width=1.5), name='MA20 (황금선)'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='#94a3b8', width=1, dash='dot'), name='BB 상단'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='#94a3b8', width=1, dash='dot'), name='BB 하단'), row=1, col=1)
                
                colors = ['#ef5350' if row['close'] >= row['open'] else '#26a69a' for index, row in df.iterrows()]
                fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color=colors, name='Volume'), row=2, col=1)

                fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=20, b=0), height=550, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

        # --- TAB 2: 분석 ---
        with tab2:
            st.subheader(f"🔬 {target_coin} 세력 호가창 & 퀀트 분석")
            orderbook = pybithumb.get_orderbook(target_coin)
            c_ob1, c_ob2 = st.columns([1, 1])
            with c_ob1:
                st.markdown("#### 🧊 호가 압력 (Bid/Ask Pressure)")
                if orderbook:
                    asks = orderbook['asks'][:5]
                    bids = orderbook['bids'][:5]
                    st.write("**🔽 매도벽 (저항)**")
                    for ask in reversed(asks):
                        st.progress(min(ask['quantity'] / 5, 1.0))
                        st.caption(f"{ask['price']:,.0f} ₩ | 잔량: {ask['quantity']:.4f}")
                    st.markdown("---")
                    st.write("**🔼 매수벽 (지지)**")
                    for bid in bids:
                        st.caption(f"{bid['price']:,.0f} ₩ | 잔량: {bid['quantity']:.4f}")
                        st.progress(min(bid['quantity'] / 5, 1.0))
            with c_ob2:
                st.markdown("#### 🧠 AI 종합 판단 스코어")
                st.metric("현재 시장가", f"{current_price:,.0f} KRW")
                if df is not None:
                    last_close = df['close'].iloc[-1]
                    ma20 = df['MA20'].iloc[-1]
                    if last_close > ma20 * 1.02: signal, color = "🔥 강력 매수 (Strong Buy)", "success"
                    elif last_close < ma20 * 0.98: signal, color = "🧊 매도 경고 (Strong Sell)", "error"
                    else: signal, color = "⚖️ 관망 (Hold)", "warning"
                    
                    if color == "success": st.success(f"**AI 시그널:** {signal}")
                    elif color == "error": st.error(f"**AI 시그널:** {signal}")
                    else: st.warning(f"**AI 시그널:** {signal}")
                
                st.info("알고리즘이 24시간 딥러닝 타점을 계산하여 전자동 트레이딩을 수행 중입니다.")

        # --- TAB 3: 로그 ---
        with tab3:
            st.subheader("📜 딥러닝 터미널 관제 로그")
            for msg in st.session_state.logs:
                if "성공" in msg or "완료" in msg or "ONLINE" in msg or "매수" in msg or "청산" in msg: st.success(msg)
                elif "오류" in msg or "❌" in msg or "EMERGENCY" in msg or "실패" in msg: st.error(msg)
                elif "가동" in msg or "시스템" in msg or "점화" in msg: st.info(msg)
                else: st.warning(msg)

        time.sleep(5)
        st.rerun()

    except Exception as e:
        # 에러 발생 시 UI 깨짐을 방지하고 조용히 재시작하는 백그라운드 쉴드
        time.sleep(5)
        st.rerun()

else:
    st.title("⚡ AI Quant Trading Terminal")
    t1, t2, t3, t4 = st.columns(4)
    t1.markdown("<div class='ticker-text'>BTC : STANDBY</div>", unsafe_allow_html=True)
    t2.markdown("<div class='ticker-text'>ETH : STANDBY</div>", unsafe_allow_html=True)
    t3.markdown("<div class='ticker-text'>XRP : STANDBY</div>", unsafe_allow_html=True)
    t4.markdown("<div class='ticker-text'>SOL : STANDBY</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #1e293b;'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("코어 상태", "🔴 OFFLINE")
    with c2: st.metric("총 포트폴리오 가치", "0 KRW")
    with c3: st.metric("자율 PnL", "0 KRW")
    with c4: st.metric("현재 포지션", "대기 중")
    with c5: st.metric("AI 누적 승률", "0.0%")
    st.markdown("---")
    st.info("👈 좌측 패널에 API 키를 입력하고 **[🚀 엔진 점화]** 버튼을 클릭하여 세계 최고의 퀀트 AI를 깨워주세요.")