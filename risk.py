import pandas as pd
from datetime import datetime, timedelta

# Proviamo a importare MT5, se fallisce creiamo dati finti per la demo
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

def get_weekly_report():
    if not MT5_AVAILABLE or not mt5.terminal_info():
        # DATI DEMO PER IL CLOUD
        df = pd.DataFrame({
            'Data': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)],
            'Profit': [150.0, -50.0, 200.0, 100.0, -20.0]
        })
        return df, df['Profit'].sum()
    
    # ... (qui tieni il codice originale che legge da MT5) ...
    return None # Sostituisci con la logica originale se MT5_AVAILABLE

def get_calendar_data():
    if not MT5_AVAILABLE or not mt5.terminal_info():
        # DATI DEMO PER IL CALENDARIO (stile immagine che hai inviato)
        dates = pd.date_range(end=datetime.now(), periods=20)
        df = pd.DataFrame({'Date': dates, 'Profit': [100 if i%3!=0 else -50 for i in range(20)]})
        return df
    
    # ... (qui tieni il codice originale) ...
    return None
