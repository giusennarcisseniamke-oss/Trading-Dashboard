import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def get_weekly_report():
    """Restituisce il riepilogo settimanale per la dashboard."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Recupera i deal chiusi nell'ultima settimana
    history = mt5.history_deals_get(start_date, end_date)
    
    if history is None or len(history) == 0:
        return None

    data = []
    for deal in history:
        # Consideriamo solo le operazioni chiuse (out)
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            data.append({
                'Data': datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d'),
                'Profit': deal.profit
            })
    
    if not data: 
        return None
    
    df = pd.DataFrame(data)
    # Raggruppa per giorno
    daily_summary = df.groupby('Data')['Profit'].sum().reset_index()
    total_weekly = df['Profit'].sum()
    
    return daily_summary, total_weekly

def get_calendar_data():
    """Restituisce i dati formattati per la Heatmap del calendario."""
    fine = datetime.now()
    inizio = fine - timedelta(days=30)
    
    history = mt5.history_deals_get(inizio, fine)
    
    if history is None or len(history) == 0:
        return None
    
    data = []
    for deal in history:
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            data.append({
                'Date': datetime.fromtimestamp(deal.time).date(),
                'Profit': deal.profit
            })
    
    if not data:
        return None
        
    df = pd.DataFrame(data)
    # Raggruppa per data per sommare i profitti giornalieri
    return df.groupby('Date')['Profit'].sum().reset_index()

# Funzione ausiliaria per calcoli di rischio (da usare prima di inviare ordini)
def calculate_lot_size(balance, risk_percent, stop_loss_pips):
    """Calcola la size dell'ordine basata sul capitale e sul rischio."""
    risk_amount = balance * (risk_percent / 100)
    # Esempio semplificato: rischio / stop loss in euro
    # Da personalizzare in base allo strumento
    return round(risk_amount / (stop_loss_pips * 10), 2)