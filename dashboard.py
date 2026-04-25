import streamlit as st
import pandas as pd
import risk
import io
from datetime import datetime

# 1. CONFIGURAZIONE
st.set_page_config(page_title="TRADING CONTROL PANEL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #0e1117; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    .cal-box {
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        min-height: 80px;
        border: 1px solid #333;
    }
    .day-num { font-size: 12px; color: #888; display: block; margin-bottom: 5px; }
    .day-profit { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN (Trading2026)
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1,2,1])
    with col_b:
        code = st.text_input("Codice d'invito", type="password")
        if st.button("Sblocca Dashboard", use_container_width=True):
            if code == "068420": 
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# 3. METRICHE IN ALTO
st.title("BOT DI TRADING - DASHBOARD")
m1, m2, m3 = st.columns(3)
m1.metric("💰 Entrate", "1.000,00 €")
m2.metric("📊 Profitto Aperto", "0,00 €", delta="0,00 €")
m3.metric("⚖️ Capitale a Rischio", "1.000,00 €")

st.markdown("---")

# 4. CALENDARIO A QUADRATI (Custom Style)
st.subheader(f"🗓️ Performance {datetime.now().strftime('%B %Y')}")

df_cal = risk.get_calendar_data()
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

# Intestazione giorni
for i, day in enumerate(days_of_week):
    cols[i].markdown(f"<p style='text-align:center; color:gray;'>{day[:3]}</p>", unsafe_allow_html=True)

# Generazione griglia calendario
if df_cal is not None:
    # Creiamo le righe (settimane)
    for i, row in df_cal.iterrows():
        day_idx = row['Date'].weekday()
        day_num = row['Date'].day
        profit = row['Profit']
        
        # Scegliamo il colore del box
        if profit > 0:
            bg_color = "rgba(40, 167, 69, 0.2)" # Verde trasparente
            text_color = "#28a745"
            prefix = "+"
        elif profit < 0:
            bg_color = "rgba(220, 53, 69, 0.2)" # Rosso trasparente
            text_color = "#dc3545"
            prefix = ""
        else:
            bg_color = "#111" # Nero/Grigio scuro
            text_color = "#555"
            prefix = ""

        with cols[day_idx]:
            st.markdown(f"""
                <div class="cal-box" style="background-color: {bg_color}; border: 1px solid {text_color if profit != 0 else '#333'};">
                    <span class="day-num">{day_num}</span>
                    <span class="day-profit" style="color: {text_color};">{prefix}{profit:,.0f}€</span>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# 5. RESOCONTO SETTIMANALE
st.header("🏁 Resoconto Settimanale")
daily_df, weekly_total = risk.get_weekly_report()
if daily_df is not None:
    st.table(daily_df) # Tabella pulita
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        daily_df.to_excel(writer, index=False)
    st.download_button("📥 Scarica Excel", data=buffer, file_name="report.xlsx")

# 6. INFORMAZIONI SUL BOT (NUOVA SEZIONE RICHIESTA)
st.markdown("---")
col_bot, col_rev = st.columns([2, 1])

with col_bot:
    st.subheader("📘 Informazioni sul Bot")
    st.markdown("""
    <div class="info-card">
    <h3>🤖 Come Opera il Sistema</h3>
    <p>Questo bot non è un semplice copiatore, ma un <b>analista algoritmico avanzato</b>:</p>
    <ul>
        <li><b>Ricezione Segnale:</b> Legge in tempo reale i messaggi dai canali Telegram selezionati.</li>
        <li><b>Filtro AI:</b> Un'Intelligenza Artificiale analizza il testo per capire direzione (BUY/SELL) e asset.</li>
        <li><b>Validazione Tecnica:</b> Il sistema controlla i dati di MetaTrader 5 (prezzo, medie mobili, RSI) per verificare se il segnale ha senso.</li>
        <li><b>Gestione Rischio:</b> Ogni operazione ha un rapporto <b>Rischio : Rendimento di 1 : 3</b>. Non operiamo mai senza Stop Loss.</li>
        <li><b>Protezione Capitale:</b> Il bot calcola la quantità di lotti basandosi sul tuo bilancio per rischiare solo una piccola percentuale fissa.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with st.expander("✍️ Lascia una recensione")
    with st.form("feedback"):
        st.text_input("Nome")
        st.slider("Voto", 1, 5, 5)
        st.text_area("Cosa ne pensi del bot?")
        if st.form_submit_button("Invia Feedback"):
            st.success("Grazie per il tuo messaggio!")
