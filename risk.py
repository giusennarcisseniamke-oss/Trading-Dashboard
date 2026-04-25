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
                return df.groupby('Date')['Profit'].sum().reset_index()

    # DATI DEMO PER ONLINE
    dr = pd.date_range(end=datetime.now(), periods=30)
    profits = [843, 493, -68, 324, 572, 602, 498, 527, 1100, -342, 632, 567, 121, 1100, 562, -596, 276, 150, 400, -20]
    while len(profits) < len(dr): profits.append(np.random.randint(-100, 600))
    df_demo = pd.DataFrame({'Date': dr, 'Profit': profits[:len(dr)]})
    return df_demo

def get_weekly_report():
    df = get_calendar_data()
    if df is not None:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        last_7 = df.tail(7).copy()
        return last_7.rename(columns={'Date': 'Data'}), last_7['Profit'].sum()
    return None, 0
