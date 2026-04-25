import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

def get_calendar_data():
    if MT5_AVAILABLE and mt5.initialize():
        fine = datetime.now()
        inizio = fine - timedelta(days=31)
        history = mt5.history_deals_get(inizio, fine)
        if history:
            data = [{'Date': datetime.fromtimestamp(d.time).date(), 'Profit': d.profit} 
                    for d in history if d.entry == mt5.DEAL_ENTRY_OUT]
            if data:
                df = pd.DataFrame(data)
                df = df.groupby('Date')['Profit'].sum().reset_index()
                df['Date'] = pd.to_datetime(df['Date'])
                return df

    # DATI DEMO (Se non c'è MT5)
    dr = pd.date_range(end=datetime.now(), periods=28)
    profits = [843, 493, -68, 0, 572, 602, 0, 527, 1100, -342, 0, 567, 121, 1100, 562, -596, 276, 0, 150, 400]
    while len(profits) < len(dr): profits.append(0)
    df_demo = pd.DataFrame({'Date': dr, 'Profit': profits[:len(dr)]})
    return df_demo

def get_weekly_report():
    df = get_calendar_data()
    if df is not None:
        df['Date_Str'] = df['Date'].dt.strftime('%Y-%m-%d')
        last_7 = df.tail(7).copy()
        return last_7[['Date_Str', 'Profit']].rename(columns={'Date_Str': 'Data'}), last_7['Profit'].sum()
    return None, 0
