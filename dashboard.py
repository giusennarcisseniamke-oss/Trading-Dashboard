import streamlit as st
import pandas as pd
import plotly.express as px
import risk
import time
import io

# Protezione per MT5
try:
    import MetaTrader5 as mt5
    MT5_LIVE = mt5.initialize()
except:
    MT5_LIVE = False

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="BOT DI TRADING - DASHBOARD", layout="wide", page_icon="📈")

# 2. ACCESSO PROTETTO
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        code = st.text_input("Inserisci Codice d'invito", type="password")
        if st.button("Sblocca", use_container_width=True):
            if code == "Trading2026": # PASSWORD
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Codice errato!")
    st.stop()

# 3. HEADER
st.title("BOT DI TRADING - DASHBOARD DI CONTROLLO")
if not MT5_LIVE:
    st.sidebar.warning("⚠️ MODALITÀ DEMO: MetaTrader5 non rilevato sul server.")

# 4. METRICHE LIVE
c1, c2, c3 = st.columns(3)
if MT5_LIVE:
    acc = mt5.account_info()
    c1.metric("Bilancio", f"{acc.balance:.2f} €")
    c2.metric("Profitto Aperto", f"{acc.profit:.2f} €")
    c3.metric("Equity", f"{acc.equity:.2f} €")
else:
    c1.metric("Bilancio (Demo)", "10,250.00 €")
    c2.metric("Profitto Aperto (Demo)", "145.20 €")
    c3.metric("Equity (Demo)", "10,395.20 €")

st.markdown("---")

# 5. CALENDARIO HEATMAP
st.header("🗓️ Calendario Performance")
df_cal = risk.get_calendar_data()
if df_cal is not None:
    df_cal['Date'] = pd.to_datetime(df_cal['Date'])
    df_cal['Giorno'] = df_cal['Date'].dt.day_name()
    df_cal['Settimana'] = df_cal['Date'].dt.isocalendar().week
    fig = px.density_heatmap(
        df_cal, x="Giorno", y="Settimana", z="Profit", text_auto=".2f",
        color_continuous_scale=["#dc3545", "#f8f9fa", "#28a745"],
        category_orders={"Giorno": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 6. REPORT SETTIMANALE ED EXPORT
st.header("🏁 Report Settimanale")
daily_df, total = risk.get_weekly_report()
color_res = "#28a745" if total >= 0 else "#dc3545"

st.markdown(f"<div style='padding:20px; border-left:10px solid {color_res}; background:#f8f9fa;'><h3>Profitto Settimana: <span style='color:{color_res}'>{total:.2f} €</span></h3></div>", unsafe_allow_html=True)

col_g, col_t = st.columns([2, 1])
with col_g:
    st.bar_chart(daily_df.set_index('Data')['Profit'])
with col_t:
    st.dataframe(daily_df, hide_index=True)
    # Download Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        daily_df.to_excel(wr, index=False)
    st.download_button("📥 Scarica Excel", data=buf, file_name="report.xlsx", mime="application/vnd.ms-excel")

# 7. INFO E RECENSIONI
st.markdown("---")
st.subheader("📖 Come opera il Bot")
st.write("Il sistema usa IA per filtrare segnali Telegram e MT5 per l'esecuzione con gestione del rischio 1:3.")

with st.expander("✍️ Lascia una recensione"):
    with st.form("rev"):
        n = st.text_input("Nome")
        v = st.slider("Voto", 1, 5, 5)
        t = st.text_area("Messaggio")
        if st.form_submit_button("Invia"):
            st.success("Grazie!")
