import streamlit as st
import pandas as pd
import plotly.express as px
import risk  # Assicurati che risk.py sia aggiornato con le funzioni get_weekly_report e get_calendar_data
try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None
import time
import io

# 1. CONFIGURAZIONE PAGINA E TITOLO SCHEDA BROWSER
st.set_page_config(
    page_title="BOT DI TRADING - DASHBOARD", 
    layout="wide", 
    page_icon="📈"
)

# 2. FUNZIONE SISTEMA DI ACCESSO PROTETTO
def check_access():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<br><br><h1 style='text-align: center;'>🔒 ACCESSO RISERVATO</h1>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1,2,1])
        with col_b:
            st.info("Questa Dashboard è privata. Inserisci il codice d'invito per visualizzare le performance live.")
            invite_code = st.text_input("Codice d'invito", type="password")
            if st.button("Sblocca Dashboard", use_container_width=True):
                # --- IMPOSTA QUI LA TUA PASSWORD ---
                if invite_code == "068420": 
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Codice errato. Contatta l'amministratore per un invito.")
        return False
    return True

# Se l'utente ha inserito il codice corretto, mostriamo la dashboard
if check_access():
    
    # 3. TITOLO PRINCIPALE
    st.title("BOT DI TRADING - DASHBOARD DI CONTROLLO MULTI-ASSET")
    
    # --- STATO ACCOUNT IN TEMPO REALE ---
    col1, col2, col3 = st.columns(3)
    if mt5.initialize():
        acc = mt5.account_info()
        if acc:
            col1.metric("💰 Bilancio", f"{acc.balance:.2f} €")
            profit_val = acc.profit
            p_color = "normal" if profit_val >= 0 else "inverse"
            col2.metric("📊 Profitto Aperto", f"{profit_val:.2f} €", delta=f"{profit_val:.2f} €", delta_color=p_color)
            col3.metric("⚖️ Equity", f"{acc.equity:.2f} €")
    else:
        st.warning("MetaTrader 5 non connesso. Assicurati che l'app MT5 sia aperta.")

    st.markdown("---")

    # --- SEZIONE CALENDARIO HEATMAP (STILE GOAL CRUSHED) ---
    st.header("🗓️ Calendario Performance Mensile")
    df_cal = risk.get_calendar_data()
    
    if df_cal is not None:
        df_cal['Date'] = pd.to_datetime(df_cal['Date'])
        # Prepariamo i nomi dei giorni e il numero della settimana
        df_cal['Giorno'] = df_cal['Date'].dt.day_name()
        df_cal['Settimana'] = df_cal['Date'].dt.isocalendar().week
        
        fig = px.density_heatmap(
            df_cal, 
            x="Giorno", 
            y="Settimana", 
            z="Profit", 
            text_auto=".2f",
            color_continuous_scale=["#dc3545", "#f8f9fa", "#28a745"], # Rosso -> Grigio -> Verde
            category_orders={"Giorno": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        )
        fig.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔎 Nessun dato storico trovato per il calendario mensile.")

    st.markdown("---")

    # --- SEZIONE RESOCONTO SETTIMANALE ED ESPORTAZIONE ---
    st.header("🏁 Resoconto Settimanale")
    report = risk.get_weekly_report()
    
    if report:
        daily_df, weekly_total = report
        color_box = "#28a745" if weekly_total >= 0 else "#dc3545"
        
        # Box Profitto Totale
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; border-left: 10px solid {color_box}; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size: 1.2rem; color:#6c757d;">Profitto Netto Totale Settimana</p>
                <h1 style="margin:0; color:{color_box}; font-size: 3rem;">{weekly_total:.2f} €</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spazio

        # Layout Grafico e Tabella affiancati
        c_graph, c_table = st.columns([2, 1])
        
        with c_graph:
            st.subheader("📈 Andamento Giornaliero")
            st.bar_chart(daily_df.set_index('Data')['Profit'])

        with c_table:
            st.subheader("📋 Dettaglio")
            def style_profit(v):
                return 'color: green' if v >= 0 else 'color: red'
            
            st.dataframe(daily_df.style.applymap(style_profit, subset=['Profit']), hide_index=True, use_container_width=True)
            
            # --- TASTO DOWNLOAD EXCEL ---
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                daily_df.to_excel(writer, index=False, sheet_name='Report_Settimanale')
            
            st.download_button(
                label="📥 Scarica Report Excel",
                data=buffer,
                file_name=f"Report_Trading_{time.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
    else:
        st.info("In attesa di operazioni chiuse per generare il grafico.")

    # --- SEZIONE DESCRIZIONE E RECENSIONI ---
    st.markdown("---")
    st.header("📘 Informazioni sul Bot")
    
    col_info, col_rev = st.columns([2, 1])
    
    with col_info:
        st.markdown("""
        ### 🤖 Come Opera il Sistema
        Questo bot non è un semplice copiatore, ma un **analista algoritmico avanzato**:
        
        1. **Ricezione Segnale:** Legge in tempo reale i messaggi dai canali Telegram selezionati.
        2. **Filtro AI:** Un'Intelligenza Artificiale analizza il testo per capire direzione (BUY/SELL) e asset.
        3. **Validazione Tecnica:** Il sistema controlla i dati di MetaTrader 5 (prezzo, medie mobili, RSI) per confermare se il segnale ha senso.
        4. **Gestione Rischio:** Ogni operazione ha un rapporto **Rischio:Rendimento di 1:3**. Non operiamo mai senza Stop Loss.
        5. **Protezione Capitale:** Il bot calcola la quantità di lotti basandosi sul tuo bilancio per rischiare solo una piccola percentuale fissa.
        """)
        
    with col_rev:
        st.markdown("### ✍️ Lascia una Recensione")
        with st.form("feedback_form"):
            user_name = st.text_input("Tuo Nome")
            user_rating = st.select_slider("Voto", options=[1, 2, 3, 4, 5], value=5)
            user_text = st.text_area("Cosa ne pensi del bot?")
            
            if st.form_submit_button("Invia Feedback"):
                if user_name and user_text:
                    with open("reviews.txt", "a") as f:
                        f.write(f"{time.strftime('%Y-%m-%d')} | {user_name} | {user_rating}/5 | {user_text}\n")
                    st.success("Grazie! Recensione salvata con successo.")
                else:
                    st.warning("Per favore, compila tutti i campi.")

    # Footer finale
    st.markdown("<br><hr><center><p style='color: grey;'>BOT DI TRADING © 2026 - Dashboard Privata Ad Accesso Invitato</p></center>", unsafe_allow_html=True)

# Per far girare la dashboard: streamlit run dashboard.py
