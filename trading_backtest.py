import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import OneHotEncoder

# ===============================
# CONFIGURATION
# ===============================
CSV_PATH = "static/TSLA_5min_data.csv"
L1, R1_LEN = 15, 15
L2, R2_LEN = 30, 30
TICK_SIZE = 0.01  
TICKS_BUFFER = 2  

# ===============================
# 1. DATA PREPARATION & LABELING
# ===============================
def prepare_data(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()

    df = df.loc[:, ~df.columns.duplicated()].copy()
    if 'Unnamed: 0' in df.columns: df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').drop_duplicates(subset=['date']).reset_index(drop=True)

    # --- Pivot Engine ---
    def get_pine_pivots(highs, lows, l, r):
        p_highs, p_lows = np.full(len(highs), np.nan), np.full(len(lows), np.nan)
        last_h, last_l = np.nan, np.nan
        for i in range(len(highs)):
            if i >= (l + r):
                idx = i - r
                val_h, val_l = highs[idx], lows[idx]
                if all(val_h > highs[idx-l:idx]) and all(val_h > highs[idx+1:idx+r+1]):
                    last_h = val_h
                if all(val_l < lows[idx-l:idx]) and all(val_l < lows[idx+1:idx+r+1]):
                    last_l = val_l
            p_highs[i], p_lows[i] = last_h, last_l
        return p_highs, p_lows

    df['R1'], df['S1'] = get_pine_pivots(df['high'].values, df['low'].values, L1, R1_LEN)
    df['R2'], df['S2'] = get_pine_pivots(df['high'].values, df['low'].values, L2, R2_LEN)

    # --- AI Features ---
    df['rsi'] = 100 - (100 / (1 + df['close'].diff().clip(lower=0).rolling(14).mean() / 
                              df['close'].diff().clip(upper=0).abs().rolling(14).mean()))
    df['volatility'] = df['high'] - df['low']
    df['body_size'] = abs(df['close'] - df['open'])

    # --- Logic Helpers ---
    df['bullBody'] = (df['high'] - df['close']) <= (df['close'] - df['low']) / 3
    df['bearBody'] = (df['close'] - df['low']) <= (df['high'] - df['close']) / 3
    h1, l1 = df['high'].shift(1), df['low'].shift(1)
    df['is_IB'] = (df['high'] < h1) & (df['low'] > l1)

    def get_pine_filter(close_s, level_s, op='>'):
        lvl_prev = level_s.shift(1)
        cond = (close_s.shift(1) > lvl_prev) if op == '>' else (close_s.shift(1) < lvl_prev)
        return cond.fillna(False).astype(int).rolling(10).sum() == 0

    # --- Labeled Signal Engine ---
    def get_signals_and_labels(R_raw, S_raw, noA, noB, hour, prefix):
        R, S = R_raw.shift(1), S_raw.shift(1)
        t1, t2 = (hour >= 9) & (hour < 11), (hour >= 11) & (hour <= 16)

        # 1. Define Conditions (Boolean Series)
        # Bullish
        c_rBOP = (t1 | (t2 & noA)) & R.notna() & (df['open'] < R) & (df['close'] > R) & df['bullBody']
        c_rBOLP = (t1) & R.notna() & (df['low'] < R) & (df['close'] > R) & df['bullBody']
        c_sBDFP = (t1) & S.notna() & (df['low'] < S) & (df['close'] > S) & df['bullBody']
        c_sRJP = (t1 | t2) & S.notna() & (df['open'] < S) & (df['close'] > S) & df['bullBody']
        c_sIBP = (t1 | t2) & S.notna() & (h1 > S) & (l1 < S) & df['is_IB'] & df['bullBody']

        # Bearish
        c_sBDP = (t1 | (t2 & noB)) & S.notna() & (df['open'] > S) & (df['close'] < S) & df['bearBody']
        c_sBDLP = (t1) & S.notna() & (df['high'] > S) & (df['close'] < S) & df['bearBody']
        c_rBOFP = (t1) & R.notna() & (df['high'] > R) & (df['close'] < R) & df['bearBody']
        c_rRJP = (t1 | t2) & R.notna() & (df['open'] > R) & (df['close'] < R) & df['bearBody']
        c_rIBP = (t1 | t2) & R.notna() & (l1 < R) & (h1 > R) & df['is_IB'] & df['bearBody']

        # 2. Assign Labels (Priority: First match in list wins)
        # We use np.select to map Boolean -> String Label
        bull_conds = [c_rBOP, c_rBOLP, c_sBDFP, c_sRJP, c_sIBP]
        bull_names = [f'{prefix}_rBOP', f'{prefix}_rBOLP', f'{prefix}_sBDFP', f'{prefix}_sRJP', f'{prefix}_sIBP']
        
        bear_conds = [c_sBDP, c_sBDLP, c_rBOFP, c_rRJP, c_rIBP]
        bear_names = [f'{prefix}_sBDP', f'{prefix}_sBDLP', f'{prefix}_rBOFP', f'{prefix}_rRJP', f'{prefix}_rIBP']

        # Generate Label Columns (default to "None")
        lbl_bull = np.select(bull_conds, bull_names, default='None')
        lbl_bear = np.select(bear_conds, bear_names, default='None')

        # Targets
        tgt_bull = df['close'] + (df['close'] - S)
        tgt_bear = df['close'] - (R - df['close'])

        return lbl_bull, lbl_bear, tgt_bull, tgt_bear

    hour = df['date'].dt.hour
    
    # Compute P1 & P2 Labels
    l_b1, l_br1, t_b1, t_br1 = get_signals_and_labels(df['R1'], df['S1'], get_pine_filter(df['close'], df['R1'], '>'), get_pine_filter(df['close'], df['S1'], '<'), hour, "P1")
    l_b2, l_br2, t_b2, t_br2 = get_signals_and_labels(df['R2'], df['S2'], get_pine_filter(df['close'], df['R2'], '>'), get_pine_filter(df['close'], df['S2'], '<'), hour, "P2")

    # Merge P1 and P2 (P1 takes priority if both occur)
    df['setup_label'] = np.where(l_b1 != 'None', l_b1,
                                 np.where(l_br1 != 'None', l_br1,
                                          np.where(l_b2 != 'None', l_b2,
                                                   np.where(l_br2 != 'None', l_br2, 'None'))))
    
    # Determine Signal Type based on label
    df['signal_type'] = np.where(df['setup_label'].str.contains('_rBOP|_rBOLP|_sBDFP|_sRJP|_sIBP'), 'BULL',
                                 np.where(df['setup_label'] != 'None', 'BEAR', 'NONE'))
    
    # Merge Targets
    df['target'] = t_b1.fillna(t_b2).fillna(t_br1).fillna(t_br2)
    
    return df.dropna()

# ===============================
# 2. BACKTEST WITH LABELS
# ===============================
def run_backtest(df):
    trades = []
    active_trade = None
    pending_order = None 

    print("Running Backtest...")
    
    for i in range(len(df)):
        row = df.iloc[i]
        
        # 1. Check Pending Order (Fill or Kill on Next Bar)
        if pending_order:
            if i > pending_order['bar_idx'] + 1:
                pending_order = None # Expired
            elif i == pending_order['bar_idx'] + 1:
                triggered = False
                if pending_order['side'] == 'BULL':
                    if row['high'] >= pending_order['entry']: triggered = True
                else:
                    if row['low'] <= pending_order['entry']: triggered = True
                
                if triggered:
                    active_trade = pending_order
                    active_trade['start_idx'] = i
                    pending_order = None
                else:
                    pending_order = None # Cancelled

        # 2. Manage Active Trade
        if active_trade:
            is_bull = active_trade['side'] == 'BULL'
            sl_hit = (row['low'] <= active_trade['sl']) if is_bull else (row['high'] >= active_trade['sl'])
            tp_hit = (row['high'] >= active_trade['tp']) if is_bull else (row['low'] <= active_trade['tp'])
            
            if sl_hit or tp_hit:
                # Prioritize SL if both hit in same candle (conservative)
                active_trade['result'] = 0 if sl_hit else 1
                active_trade['end_idx'] = i
                trades.append(active_trade)
                active_trade = None
            continue 

        # 3. New Signals (Only if no trade/order active)
        if pending_order is None and active_trade is None and row['signal_type'] != 'NONE':
            setup_name = row['setup_label']
            
            if row['signal_type'] == 'BULL':
                entry = row['high'] + (TICK_SIZE * TICKS_BUFFER)
                sl = row['low']
                tp = entry + abs(row['target'] - row['close']) 
                pending_order = {
                    'side': 'BULL', 'entry': entry, 'sl': sl, 'tp': tp,
                    'bar_idx': i, 'setup': setup_name,
                    # AI Features
                    'rsi': row['rsi'], 'volatility': row['volatility']
                }
            else: # BEAR
                entry = row['low'] - (TICK_SIZE * TICKS_BUFFER)
                sl = row['high']
                tp = entry - abs(row['close'] - row['target'])
                pending_order = {
                    'side': 'BEAR', 'entry': entry, 'sl': sl, 'tp': tp,
                    'bar_idx': i, 'setup': setup_name,
                    # AI Features
                    'rsi': row['rsi'], 'volatility': row['volatility']
                }

    return pd.DataFrame(trades)

# ===============================
# 3. AI TRAINING & SETUP METRICS
# ===============================
def analyze_and_train(trade_df):
    if trade_df.empty:
        print("No trades generated.")
        return

    print("\n" + "="*40)
    print("      SETUP PERFORMANCE METRICS")
    print("="*40)
    
    # --- A. Setup-based Metrics ---
    # Group by 'setup' and calculate stats
    stats = trade_df.groupby('setup')['result'].agg(['count', 'mean'])
    stats['mean'] = stats['mean'] * 100 # Convert to percentage
    stats.columns = ['Count', 'Win Rate %']
    print(stats.sort_values('Win Rate %', ascending=False))
    print("-" * 40)
    print(f"Total Win Rate: {trade_df['result'].mean():.2%}")

    # --- B. AI Training ---
    print("\nTraining AI on Setup Context...")
    
    # 1. Feature Engineering: One-Hot Encode the 'setup' label
    # We combine numerical features (RSI, Volatility) with the categorical Setup Name
    
    features = trade_df[['rsi', 'volatility']]
    encoder = OneHotEncoder(sparse_output=False)
    setup_encoded = encoder.fit_transform(trade_df[['setup']])
    
    # Create clean feature set
    X_encoded = pd.DataFrame(setup_encoded, columns=encoder.get_feature_names_out(['setup']))
    X = pd.concat([features.reset_index(drop=True), X_encoded.reset_index(drop=True)], axis=1)
    y = trade_df['result']

    # 2. Train/Test Split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Train Model
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # 4. Results
    preds = model.predict(X_val)
    print("\n--- AI Model Performance (Validation Set) ---")
     # Visualizing how we grade the AI
    print(classification_report(y_val, preds, target_names=['LOSS', 'WIN']))
    
    # Feature Importance (Does Setup Name matter more than RSI?)
    print("\n--- Key Drivers (Feature Importance) ---")
    importances = pd.Series(model.feature_importances_, index=X.columns)
    print(importances.sort_values(ascending=False).head(5))

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    df = prepare_data(CSV_PATH)
    results = run_backtest(df)
    analyze_and_train(results)
