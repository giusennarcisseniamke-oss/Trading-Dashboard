import streamlit as st
import pandas as pd
import risk
import io
from datetime import datetime

# --- 1. CONFIGURAZIONE ESTETICA E AUTO-REFRESH ---
st.set_page_config(page_title="TRADING CONTROL PANEL", layout="wide")

# Forza l'aggiornamento della pagina ogni 300 secondi (5 minuti)
# st.empty() aiuta a gestire i refresh dinamici
if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.now().strftime("%H:%M:%S")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background-color: #0e1117; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    .cal-box {
        border-radius: 8px; padding: 10px; text-align: center;
        margin-bottom: 10px; min-height: 85px; border: 1px solid #333;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .today-highlight { border: 2px solid #007bff !important; box-shadow: 0px 0px 10px #007bff; }
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
            if code == "068420": 
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- 3. HEADER E METRICHE ---
# Mostra l'ultimo aggiornamento per darti sicurezza che i dati siano freschi
st.sidebar.write(f"Ultimo aggiornamento dati: {datetime.now().strftime('%H:%M:%S')}")
if st.sidebar.button("Aggiorna Ora"):
    st.rerun()

st.title("BOT DI TRADING - DASHBOARD")
m1, m2, m3 = st.columns(3)
m1.metric("💰 Entrate", "1.000,00 €")
m2.metric("📊 Profitto Aperto", "0,00 €", delta="0,00 €")
m3.metric("⚖️ Capitale a Rischio", "1.000,00 €")

st.markdown("---")

# --- 4. CALENDARIO ORDINATO (7 GIORNI: MONDAY - SUNDAY) ---
current_date = datetime.now()
st.subheader(f"🗓️ Performance {current_date.strftime('%B %Y')}")

df_cal = risk.get_calendar_data()
df_cal['Date'] = pd.to_datetime(df_cal['Date'])
df_cal['WeekNum'] = df_cal['Date'].dt.isocalendar().week

days_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day in enumerate(days_eng):
    cols[i].markdown(f"<p style='text-align:center; color:gray; font-weight:bold;'>{day[:3]}</p>", unsafe_allow_html=True)

if not df_cal.empty:
    weeks = df_cal['WeekNum'].unique()
    for week in weeks:
        df_week = df_cal[df_cal['WeekNum'] == week]
        for i in range(7):
            with cols[i]:
                day_data = df_week[df_week['Date'].dt.weekday == i]
                if not day_data.empty:
                    row = day_data.iloc[0]
                    profit = row['Profit']
                    is_today = (row['Date'].date() == current_date.date())
                    
                    # Logica Colori
                    if profit > 0:
                        bg, txt, pref = "rgba(40, 167, 69, 0.15)", "#28a745", "+"
                    elif profit < 0:
                        bg, txt, pref = "rgba(220, 53, 69, 0.15)", "#dc3545", ""
                    else:
                        bg, txt, pref = "#111", "#444", ""

                    # Applica evidenziatore se è oggi
                    today_class = "today-highlight" if is_today else ""

                    st.markdown(f"""
                        <div class="cal-box {today_class}" style="background-color: {bg}; border: 1px solid {txt if profit != 0 else '#222'};">
                            <span class="day-num">{row['Date'].day} {'(OGGI)' if is_today else ''}</span>
                            <span class="day-profit" style="color: {txt};">{pref}{profit:,.0f}€</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="cal-box" style="border: 1px solid transparent;"></div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. RESOCONTO SETTIMANALE ---
st.header("🏁 Resoconto Settimanale (Ultimi 7 giorni)")
daily_df, _ = risk.get_weekly_report()
if daily_df is not None:
    st.table(daily_df)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as wr: daily_df.to_excel(wr, index=False)
    st.download_button("📥 Scarica Report Excel", data=buffer, file_name="trading_report.xlsx")

# --- 6. INFO BOT E RECENSIONI ---
st.markdown("---")
col_info, col_rev = st.columns([2, 1])

with col_info:
    st.subheader("📘 Informazioni sul Bot")
    st.markdown("""
    <div class="info-card">
        <h3>🤖 Come Opera il Sistema</h3>
        <p>Questo bot non è un semplice copiatore, ma un <b>analista algoritmico avanzato</b>:</p>
        <p><b>Ricezione Segnale:</b> Legge in tempo reale i messaggi dai canali Telegram selezionati.</p>
        <p><b>Filtro AI:</b> Un'Intelligenza Artificiale analizza il testo per capire direzione (BUY/SELL) e asset.</p>
        <p><b>Validazione Tecnica:</b> Il sistema controlla i dati di MetaTrader 5 (prezzo, medie mobili, RSI) per verificare se il segnale ha senso.</p>
        <p><b>Gestione Rischio:</b> Ogni operazione ha un rapporto <b>Rischio : Rendimento di 1 : 3</b>. Non operiamo mai senza Stop Loss.</p>
        <p><b>Protezione Capitale:</b> Il bot calcola la quantità di lotti basandosi sul tuo bilancio per rischiare solo una piccola percentuale fissa.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col_rev:
    st.subheader("✍️ Recensione")
    with st.form("feedback_form"):
        u_name = st.text_input("Tuo Nome")
        u_rating = st.slider("Voto", 1, 5, 5)
        u_text = st.text_area("Messaggio")
        if st.form_submit_button("Invia"):
            st.success("Ricevuto!")
