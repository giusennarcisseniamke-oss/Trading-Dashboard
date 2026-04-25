import streamlit as st
import pandas as pd
import plotly.express as px
import risk
import io
from datetime import datetime

# 1. CONFIGURAZIONE
st.set_page_config(page_title="TRADING CONTROL PANEL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #0e1117; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { font-size: 40px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        code = st.text_input("Codice d'invito", type="password")
        if st.button("Sblocca", use_container_width=True):
            if code == "068420": 
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# 3. METRICHE PERSONALIZZATE (COME DA TUA IMMAGINE)
st.title("BOT DI TRADING - DASHBOARD DI CONTROLLO")
m1, m2, m3 = st.columns(3)

# Dati per le metriche (Se MT5 è collegato usa i veri, altrimenti demo)
val_entrate = 1000.00
val_profitto_aperto = 0.00
val_capitale = 1000.00

m1.metric("💰 Matrimonio", f"{val_entrate:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'))
m2.metric("📊 Profitto Aperto", f"{val_profitto_aperto:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'), delta="0,00 €")
m3.metric("⚖️ Azioni", f"{val_capitale:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'))

st.markdown("---")

# 4. GOAL MENSILE E CALENDARIO
st.subheader("🎯 Monthly goal")
goal = 4300.0
df_cal = risk.get_calendar_data()
total_pnl = df_cal['Profit'].sum()
progress = min(total_pnl / goal, 1.0) if total_pnl > 0 else 0.0

st.progress(progress)
cg1, cg2 = st.columns([1, 1])
cg1.markdown(f"<h2 style='color: #28a745;'>+${total_pnl:,.0f}</h2>", unsafe_allow_html=True)
cg2.markdown(f"<p style='text-align: right; color: gray;'>target: ${goal:,.0f}</p>", unsafe_allow_html=True)

st.subheader("🗓️ Calendar Performance")
df_cal['Date'] = pd.to_datetime(df_cal['Date'])
df_cal['Giorno'] = df_cal['Date'].dt.day_name()
df_cal['Settimana'] = df_cal['Date'].dt.isocalendar().week

fig = px.density_heatmap(
    df_cal, x="Giorno", y="Settimana", z="Profit", text_auto=".0f",
    color_continuous_scale=["#401010", "#111111", "#104010"],
    category_orders={"Giorno": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
)
fig.update_layout(plot_bgcolor="black", paper_bgcolor="black", coloraxis_showscale=False, height=400, margin=dict(l=0,r=0,t=30,b=0))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 5. RESOCONTO SETTIMANALE (TABELLA E DOWNLOAD)
st.header("🏁 Resoconto Settimanale")
daily_df, weekly_total = risk.get_weekly_report()

if daily_df is not None:
    col_tab, col_space = st.columns([2, 1])
    with col_tab:
        st.dataframe(daily_df.style.format({"Profit": "{:.2f} €"}), hide_index=True, use_container_width=True)
        
        # Tasto Download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            daily_df.to_excel(writer, index=False, sheet_name='Settimana')
        
        st.download_button(
            label="📥 Scarica Report Settimanale (Excel)",
            data=buffer,
            file_name=f"Trading_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )

# 6. INFO E FEEDBACK
st.markdown("---")
c_info, c_rev = st.columns([2, 1])
with c_info:
    st.subheader("📘 Informazioni sul Bot")
    st.write("Sistema algoritmico avanzato con filtro AI e Risk Management 1:3.")
with c_rev:
    st.subheader("✍️ Recensione")
    with st.form("f"):
        st.text_input("Nome")
        st.slider("Voto", 1, 5, 5)
        st.text_area("Messaggio")
        st.form_submit_button("Invia")
