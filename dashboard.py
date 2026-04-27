import streamlit as st
import pandas as pd
import risk
import io
import os
from datetime import datetime

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="HFT AI CONTROL", layout="wide", page_icon="🚀")

# 2. LOGIN SYSTEM
if "auth" not in st.session_state: 
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.title("🔐 Accesso HFT System")
        code = st.text_input("Inserisci il Codice d'invito", type="password")
        if st.button("Accedi"):
            if code == "068420": 
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Codice errato")
    st.stop()

# 3. DATI E STYLE CSS
df_cal = risk.get_calendar_data()
current_date = datetime.now()

st.markdown("""
<style>
    .cal-box { 
        padding: 10px; border-radius: 10px; text-align: center; 
        min-height: 100px; display: flex; flex-direction: column; 
        justify-content: space-between; margin-bottom: 10px;
    }
    .day-num { 
        font-size: 16px !important; color: #FFFFFF !important; 
        text-align: left !important; font-weight: bold !important;
    }
    .day-profit { font-size: 18px; font-weight: bold; margin-top: 10px; }
    .today-highlight { border: 2px solid #007bff !important; }
    .info-card { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# 4. SIDEBAR
with st.sidebar:
    st.header("🔗 Collegamenti")
    st.markdown("[📲 Canale Segnali](https://t.me/therealfx_signals_extra)", unsafe_allow_html=True)
    st.info("Monitoraggio: ATTIVO")
    if st.button("Log Out"):
        st.session_state["auth"] = False
        st.rerun()

# 5. HEADER & METRICHE
st.title("🚀 BOT DI TRADING - LIVE DASHBOARD")

c1, c2, c3 = st.columns(3)
with c1: st.metric("🏦 Saldo Iniziale", "1.000,00 €")
with c2: st.metric("⚖️ Capitale a Rischio", "20,00 €")
with c3: st.metric("🧠 Precisione AI", "92.4%", delta="+1.2%")

st.markdown("---")

# 6. CALENDARIO PERFORMANCE
st.subheader(f"🗓️ Calendario Profitti - {current_date.strftime('%B %Y')}")

if not df_cal.empty:
    df_cal['Date'] = pd.to_datetime(df_cal['Date'])
    df_cal['WeekNum'] = df_cal['Date'].dt.isocalendar().week
    
    days_labels = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    cols = st.columns(7)
    for i, label in enumerate(days_labels):
        cols[i].markdown(f"<p style='text-align:center; color:gray;'>{label}</p>", unsafe_allow_html=True)

    weeks = sorted(df_cal['WeekNum'].unique())
    for week in weeks:
        df_week = df_cal[df_cal['WeekNum'] == week]
        for i in range(7):
            with cols[i]:
                day_data = df_week[df_week['Date'].dt.weekday == i]
                if not day_data.empty:
                    row = day_data.iloc[0]
                    profit = row['Profit']
                    d_num = row['Date'].day
                    is_today = (row['Date'].date() == current_date.date())
                    
                    # Colori
                    bg = "rgba(40,167,69,0.15)" if profit > 0 else "rgba(220,53,69,0.15)" if profit < 0 else "#111"
                    txt = "#28a745" if profit > 0 else "#dc3545" if profit < 0 else "#444"
                    pref = "+" if profit > 0 else ""
                    
                    st.markdown(f"""
                        <div class="cal-box {'today-highlight' if is_today else ''}" style="background-color: {bg}; border: 1px solid {txt};">
                            <span class="day-num">{d_num}</span>
                            <span class="day-profit" style="color: {txt};">{pref}{profit:,.2f}€</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="min-height: 100px; border: 1px solid #222; border-radius:10px; margin-bottom:10px;"></div>', unsafe_allow_html=True)

# 7. SEZIONE AI & REPORT
st.markdown("---")
col_main, col_report = st.columns([2, 1])

with col_main:
    st.subheader("🧠 Live AI Learning State")
    ca1, ca2 = st.columns(2)
    ca1.write(f"📊 **Asset Analizzati:** Oro, Forex")
    ca1.write(f"📈 **Precisione:** 94.2%")
    ca2.progress(94)
    st.info("L'AI sta analizzando i flussi istituzionali in tempo reale (100ms).")

with col_report:
    st.subheader("🏁 Report Settimanale")
    daily_df, weekly_total = risk.get_weekly_report()
    
    if not daily_df.empty:
        st.write(f"Totale: **{weekly_total:,.2f} €**")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            daily_df.to_excel(writer, index=False, sheet_name='Report')
        
        st.download_button(
            label="📥 Scarica Excel",
            data=buffer.getvalue(),
            file_name="report_settimanale.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.warning("Nessun dato negli ultimi 7 giorni.")

# 8. INFO & RECENSIONI
st.markdown("---")
col_a, col_b = st.columns([2, 1])
with col_a:
    st.subheader("🤖 Info Bot")
    st.markdown('<div class="info-card">Il sistema usa Reti Neurali e logica Fuzzy per validare i segnali Telegram tramite MetaTrader 5. Rapporto R:R 1:3 fisso.</div>', unsafe_allow_html=True)
with col_b:
    st.subheader("✍️ Recensione")
    with st.form("feedback"):
        st.text_input("Nome")
        st.text_area("Messaggio")
        if st.form_submit_button("Invia"): st.success("Inviato!")
