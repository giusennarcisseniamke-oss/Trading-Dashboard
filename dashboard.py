import streamlit as st
import pandas as pd
import risk
import io
from datetime import datetime

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="TRADING CONTROL PANEL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #0e1117; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    .cal-box {
        border-radius: 8px; padding: 10px; text-align: center;
        margin-bottom: 10px; min-height: 85px; border: 1px solid #333;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .day-num { font-size: 11px; color: #888; text-align: left; font-weight: bold; }
    .day-profit { font-size: 15px; font-weight: bold; margin-top: 5px; }
    .info-card { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACCESSO PRIVATO ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        code = st.text_input("Codice d'invito", type="password")
        if st.button("Accedi", use_container_width=True):
            if code == "Trading2026": 
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- 3. HEADER E METRICHE ---
st.title("BOT DI TRADING - DASHBOARD")
m1, m2, m3 = st.columns(3)
m1.metric("💰 Entrate", "1.000,00 €")
m2.metric("📊 Profitto Aperto", "0,00 €", delta="0,00 €")
m3.metric("⚖️ Capitale a Rischio", "1.000,00 €")

st.markdown("---")

# --- 4. CALENDARIO ORDINATO (MONDAY - FRIDAY) ---
st.subheader(f"🗓️ Performance {datetime.now().strftime('%B %Y')}")

df_cal = risk.get_calendar_data()
df_cal['Date'] = pd.to_datetime(df_cal['Date'])

# Filtro giorni lavorativi e ordinamento
df_work = df_cal[df_cal['Date'].dt.weekday < 5].copy().sort_values('Date')
df_work['WeekNum'] = df_work['Date'].dt.isocalendar().week

days_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
cols = st.columns(5)

# Intestazione Colonne
for i, day in enumerate(days_eng):
    cols[i].markdown(f"<p style='text-align:center; color:gray; font-weight:bold;'>{day}</p>", unsafe_allow_html=True)

# Griglia Calendario
if not df_work.empty:
    weeks = df_work['WeekNum'].unique()
    for week in weeks:
        df_week = df_work[df_work['WeekNum'] == week]
        for i in range(5): # Monday to Friday
            with cols[i]:
                day_data = df_week[df_week['Date'].dt.weekday == i]
                if not day_data.empty:
                    row = day_data.iloc[0]
                    profit = row['Profit']
                    
                    if profit > 0:
                        bg, txt, pref = "rgba(40, 167, 69, 0.15)", "#28a745", "+"
                    elif profit < 0:
                        bg, txt, pref = "rgba(220, 53, 69, 0.15)", "#dc3545", ""
                    else:
                        bg, txt, pref = "#111", "#555", ""

                    st.markdown(f"""
                        <div class="cal-box" style="background-color: {bg}; border: 1px solid {txt if profit != 0 else '#333'};">
                            <span class="day-num">{row['Date'].day}</span>
                            <span class="day-profit" style="color: {txt};">{pref}{profit:,.0f}€</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="cal-box" style="border: 1px solid transparent;"></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. RESOCONTO SETTIMANALE ---
st.header("🏁 Resoconto Settimanale")
daily_df, _ = risk.get_weekly_report()
if daily_df is not None:
    st.table(daily_df)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as wr: daily_df.to_excel(wr, index=False)
    st.download_button("📥 Scarica Report Excel", data=buffer, file_name="trading_report.xlsx")

# --- 6. INFO BOT E RECENSIONI (UNITE) ---
st.markdown("---")
col_info, col_rev = st.columns([2, 1])

with col_info:
    st.subheader("📘 Informazioni sul Bot")
    st.markdown("""
    <div class="info-card">
        <h4>🤖 Come Opera il Sistema</h4>
        <p>Questo bot è un analista algoritmico avanzato:</p>
        <ul>
            <li><b>Ricezione Segnale:</b> Legge in tempo reale i messaggi dai canali Telegram.</li>
            <li><b>Filtro AI:</b> Analizza il testo per capire direzione (BUY/SELL) e asset.</li>
            <li><b>Validazione Tecnica:</b> Controlla i dati di MetaTrader 5 (prezzo, medie mobili, RSI).</li>
            <li><b>Gestione Rischio:</b> Rapporto Rischio:Rendimento di 1:3. Sempre con Stop Loss.</li>
            <li><b>Protezione Capitale:</b> Calcola i lotti in base al bilancio per rischiare una % fissa.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_rev:
    st.subheader("✍️ Lascia una recensione")
    with st.form("feedback_form"):
        u_name = st.text_input("Tuo Nome")
        u_rating = st.slider("Voto", 1, 5, 5)
        u_text = st.text_area("Cosa ne pensi del bot?")
        submit = st.form_submit_button("Invia Feedback")
        
        if submit:
            if u_name and u_text:
                st.success(f"Grazie {u_name}! Feedback inviato con successo.")
            else:
                st.error("Per favore, compila tutti i campi.")
