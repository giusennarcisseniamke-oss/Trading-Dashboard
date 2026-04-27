import pandas as pd
import os
from datetime import datetime

FILE_EXCEL = "data/trading_tax_calculator.xlsx"
RR_RATIO=3


def get_calendar_data():
    if not os.path.exists(FILE_EXCEL):
        print(f"❌ File non trovato in: {FILE_EXCEL}")
        return pd.DataFrame(columns=['Date', 'Profit'])
    try:
        # Legge il foglio dei trade
        df = pd.read_excel(FILE_EXCEL, sheet_name="Trade Log")
        
        # Pulizia nomi colonne (toglie spazi extra)
        df.columns = df.columns.str.strip()

        # Rinominiamo le colonne per la dashboard se hanno nomi diversi
        # Adatta 'Data' e 'Profitto' ai nomi reali che hai nel tuo Excel
        rename_dict = {
            'Data': 'Date',
            'Profitto': 'Profit',
            'PROFITTO': 'Profit',
            'DATA': 'Date'
        }
        df = df.rename(columns=rename_dict)

        # Convertiamo la colonna Date in formato data vero
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Rimuoviamo righe con date non valide o profitti vuoti
        df = df.dropna(subset=['Date', 'Profit'])

        # Raggruppiamo per giorno (somma i profitti se fai più trade al giorno)
        df_daily = df.groupby(df['Date'].dt.date)['Profit'].sum().reset_index()
        
        # Ri-trasformiamo in datetime per compatibilità con la dashboard
        df_daily['Date'] = pd.to_datetime(df_daily['Date'])
        
        return df_daily

    except Exception as e:
        print(f"❌ Errore lettura Excel: {e}")
        return pd.DataFrame(columns=['Date', 'Profit'])

def get_weekly_report():
    df = get_calendar_data()
    if df.empty:
        return pd.DataFrame(columns=['Data', 'Profitto (€)']), 0.0
    
    last_7 = df.tail(7).copy()
    last_7['Data_Str'] = last_7['Date'].dt.strftime('%d/%m/%Y')
    weekly_total = last_7['Profit'].sum()
    
    report_df = last_7[['Data_Str', 'Profit']].rename(columns={'Data_Str': 'Data', 'Profit': 'Profitto (€)'})
    return report_df, weekly_total

def calculate_sl_tp(entry, direction, symbol):
    import filters
    # Usa l'ATR per decidere quanto deve essere lontano lo Stop Loss
    atr = filters.get_atr(symbol)
    
    # Se l'ATR fallisce, usiamo un fallback basato sul simbolo
    if atr is None or atr == 0:
        dist = 3 if "XAU" in symbol else 0.0030
    else:
        dist = atr * 1.5 # Lo SL è 1.5 volte la volatilità attuale

    if direction == "BUY":
        return round(entry - dist, 5), round(entry + (dist * 3), 5)
    else:
        return round(entry + dist, 5), round(entry - (dist * 3), 5)
