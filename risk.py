import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

def get_weekly_report():
    """Recupera i dati settimanali: reali se MT5 è presente, demo se è su Cloud."""
    if MT5_AVAILABLE and mt5.initialize():
        # --- LOGICA DATI REALI ---
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        history = mt5.history_deals_get(start_date, end_date)
        
        if history:
            data = []
            for deal in history:
                if deal.entry == mt5.DEAL_ENTRY_OUT:
                    data.append({
                        'Data': datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d'),
                        'Profit': deal.profit
                    })
            if data:
                df = pd.DataFrame(data)
                daily_summary = df.groupby('Data')['Profit'].sum().reset_index()
                return daily_summary, df['Profit'].sum()
    
    # --- LOGICA DATI DEMO (Per Cloud/GitHub) ---
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    profits = [120.50, -45.20, 89.00, 210.10, -15.00, 55.00, 130.00]
    df_demo = pd.DataFrame({'Data': dates, 'Profit': profits})
    return df_demo, df_demo['Profit'].sum()

def get_calendar_data():
    """Recupera i dati per la heatmap: reali se MT5 è presente, demo se è su Cloud."""
    if MT5_AVAILABLE and mt5.initialize():
        fine = datetime.now()
        inizio = fine - timedelta(days=30)
        history = mt5.history_deals_get(inizio, fine)
        if history:
            data = [{'Date': datetime.fromtimestamp(d.time).date(), 'Profit': d.profit} 
                    for d in history if d.entry == mt5.DEAL_ENTRY_OUT]
            if data:
                df = pd.DataFrame(data)
                return df.groupby('Date')['Profit'].sum().reset_index()

    # --- DATI DEMO PER IL CALENDARIO ---
    dr = pd.date_range(end=datetime.now(), periods=30)
    df_cal_demo = pd.DataFrame({'Date': dr, 'Profit': np.random.uniform(-50, 150, size=30)})
    return df_cal_demo

def calculate_lot_size(balance, risk_percent, stop_loss_pips):
    risk_amount = balance * (risk_percent / 100)
    return round(risk_amount / (stop_loss_pips * 10), 2)
