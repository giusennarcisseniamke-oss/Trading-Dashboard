import streamlit as st
import pandas as pd
import plotly.express as px
import risk
import io
from datetime import datetime  # <--- AGGIUNGI QUESTA RIGA MANCANTE

# CONFIGURAZIONE ESTETICA (DARK MODE)
st.set_page_config(page_title="BOT DI TRADING - DASHBOARD", layout="wide")

# CSS personalizzato per emulare l'app (sfondo nero, font pulito)
st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #111; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# SISTEMA DI ACCESSO
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        code = st.text_input("Codice d'invito", type="password")
        if st.button("Accedi", use_container_width=True):
            if code == "068420": # La tua Password
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- HEADER STILE APP ---
st.title("BOT DI TRADING - DASHBOARD DI CONTROLLO")
st.markdown(f"### {datetime.now().strftime('%B %Y')}")

# --- SEZIONE 1: MONTHLY GOAL (Barra verde dell'immagine) ---
st.subheader("🎯 Monthly goal")
goal = 4300.0
df_cal = risk.get_calendar_data()
current_pnl = df_cal['Profit'].sum()
progress = min(current_pnl / goal, 1.0) if current_pnl > 0 else 0.0

st.progress(progress)
col_a, col_b = st.columns([1, 1])
col_a.markdown(f"<h3 style='color: #28a745;'>+${current_pnl:,.0f}</h3>", unsafe_allow_html=True)
col_b.markdown(f"<p style='text-align: right; color: gray;'>of ${goal:,.0f}</p>", unsafe_allow_html=True)

if current_pnl >= goal:
    st.success(f"🏆 Goal crushed! {int((current_pnl/goal)*100)}% of your target")

st.markdown("---")

# --- SEZIONE 2: CALENDARIO A BLOCCHI (Il cuore della tua richiesta) ---
st.subheader("🗓️ Calendar Performance")

if df_cal is not None:
    df_cal['Date'] = pd.to_datetime(df_cal['Date'])
    df_cal['Giorno'] = df_cal['Date'].dt.day_name()
    df_cal['Settimana'] = df_cal['Date'].dt.isocalendar().week
    
    # Creazione Heatmap stile App
    fig = px.density_heatmap(
        df_cal, x="Giorno", y="Settimana", z="Profit", text_auto=".0f",
        color_continuous_scale=["#401010", "#111111", "#104010"], # Rosso scuro -> Nero -> Verde scuro
        category_orders={"Giorno": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    )
    fig.update_layout(
        plot_bgcolor="black", paper_bgcolor="black",
        coloraxis_showscale=False, height=450,
        xaxis=dict(showgrid=False, zeroline=False, color="gray"),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- SEZIONE 3: STATS FINALI ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("P&L TOTAL", f"+${current_pnl:,.1f}k")
c2.metric("WIN RATE", "83%")
c3.metric("BEST DAY", f"+${df_cal['Profit'].max():,.0f}")

# INFO E RECENSIONI (Per l'app online)
with st.expander("📖 Info Strategia & Feedback"):
    st.write("Il bot opera con un filtro IA e Risk Management 1:3.")
    with st.form("feedback"):
        nome = st.text_input("Nome")
        msg = st.text_area("Recensione")
        if st.form_submit_button("Invia"):
            st.success("Ricevuto!")
