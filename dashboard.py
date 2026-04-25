import streamlit as st
import pandas as pd
import plotly.express as px
import risk
import io
from datetime import datetime

# 1. CONFIGURAZIONE ESTETICA (DARK MODE)
st.set_page_config(page_title="BOT DI TRADING - PRO DASHBOARD", layout="wide")

# CSS per rendere lo sfondo nero e lo stile moderno come nell'app
st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #111; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    div[data-testid="stExpander"] { background-color: #111; border: 1px solid #333; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DI ACCESSO PROTETTO
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        st.info("Dashboard Privata. Solo utenti invitati.")
        code = st.text_input("Inserisci Codice d'invito", type="password")
        if st.button("Sblocca Dashboard", use_container_width=True):
            if code == "Trading2026": # CAMBIA QUI LA TUA PASSWORD
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Codice errato!")
    st.stop()

# 3. HEADER E GOAL MENSILE (Stile 'Goal Crushed')
st.title("BOT DI TRADING - DASHBOARD DI CONTROLLO")
st.markdown(f"### {datetime.now().strftime('%B %Y')}")

goal = 4300.0
df_cal = risk.get_calendar_data()
total_pnl = df_cal['Profit'].sum()
progress = min(total_pnl / goal, 1.0) if total_pnl > 0 else 0.0

st.subheader("🎯 Monthly goal")
st.progress(progress)
col_goal_a, col_goal_b = st.columns([1, 1])
col_goal_a.markdown(f"<h2 style='color: #28a745; margin-top:0;'>+${total_pnl:,.0f}</h2>", unsafe_allow_html=True)
col_goal_b.markdown(f"<p style='text-align: right; color: gray; font-size: 1.2rem;'>of ${goal:,.0f}</p>", unsafe_allow_html=True)

if total_pnl >= goal:
    st.success(f"🏆 Goal crushed! Hai raggiunto il {int((total_pnl/goal)*100)}% del tuo target mensile.")

st.markdown("---")

# 4. IL NUOVO GRAFICO A BLOCCHI (CALENDARIO)
st.subheader("🗓️ Calendar Performance")
if df_cal is not None:
    df_cal['Date'] = pd.to_datetime(df_cal['Date'])
    df_cal['Giorno'] = df_cal['Date'].dt.day_name()
    df_cal['Settimana'] = df_cal['Date'].dt.isocalendar().week
    
    fig = px.density_heatmap(
        df_cal, x="Giorno", y="Settimana", z="Profit", text_auto=".0f",
        color_continuous_scale=["#401010", "#111111", "#104010"], # Rosso scuro -> Nero -> Verde scuro
        category_orders={"Giorno": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    )
    fig.update_layout(
        plot_bgcolor="black", paper_bgcolor="black",
        coloraxis_showscale=False, height=450,
        xaxis=dict(showgrid=False, zeroline=False, color="gray", side="top"),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

# 5. STATISTICHE FINALI (P&L, Win Rate, Best Day)
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("YOUR P&L TOTAL", f"+${total_pnl/1000:,.1f}k")
c2.metric("WIN RATE", "83%")
c3.metric("BEST DAY", f"+${df_cal['Profit'].max():,.0f}")

# 6. DESCRIZIONE BOT E RECENSIONI (Come nel video)
st.markdown("---")
col_info, col_rev = st.columns([2, 1])

with col_info:
    st.subheader("📘 Informazioni sul Bot")
    st.markdown("""
    Questo bot non è un semplice copiatore, ma un **analista algoritmico avanzato**:
    1. **Ricezione Segnale:** Legge in tempo reale i messaggi dai canali Telegram selezionati.
    2. **Filtro AI:** Un'Intelligenza Artificiale analizza il testo per capire direzione e asset.
    3. **Validazione Tecnica:** Il sistema controlla i dati di MetaTrader 5 (prezzo, medie mobili, RSI).
    4. **Gestione Rischio:** Rapporto Rischio:Rendimento di 1:3 con Stop Loss obbligatorio.
    """)

with col_rev:
    st.subheader("✍️ Lascia una recensione")
    with st.form("feedback_form"):
        u_name = st.text_input("Tuo Nome")
        u_rating = st.slider("Voto", 1, 5, 5)
        u_text = st.text_area("Cosa ne pensi?")
        if st.form_submit_button("Invia Feedback"):
            if u_name and u_text:
                with open("reviews.txt", "a") as f:
                    f.write(f"{datetime.now().date()} | {u_name} | {u_rating}/5 | {u_text}\n")
                st.success("Grazie per il feedback!")

st.markdown("<br><center><small style='color:gray;'>BOT DI TRADING © 2026 - ACCESSO SOLO SU INVITO</small></center>", unsafe_allow_html=True)
