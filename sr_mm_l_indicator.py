"""
SR-MM-L (Clean) - Support/Resistance Measured Moves Indicator
Python implementation matching the PineScript version

This indicator identifies support and resistance levels using pivot points
and generates trading signals based on price action patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, time


class SRMMLIndicator:
    """
    Support/Resistance Measured Moves (SR-MM-L) Indicator
    
    This class implements the complete logic from the PineScript indicator including:
    - Pivot point calculations (P1 and P2)
    - Time-based session filtering (t1: 9:00-11:00, t2: 11:00-16:00)
    - Multiple signal patterns (Breakout, Breakout Low, Breakout Fail, Rejection, Inside Bar)
    - Measured move targets
    """
    
    def __init__(self, data, toggle_p1=True, toggle_p2=True, 
                 l1=15, r1=15, l2=30, r2=30):
        """
        Initialize the indicator with parameters matching PineScript inputs
        
        Args:
            data: DataFrame with columns ['open', 'high', 'low', 'close', 'timestamp']
            toggle_p1: Show P1 signals (default: True)
            toggle_p2: Show P2 signals (default: True)
            l1: Left bars for P1 pivots (default: 15)
            r1: Right bars for P1 pivots (default: 15)
            l2: Left bars for P2 pivots (default: 30)
            r2: Right bars for P2 pivots (default: 30)
        """
        self.data = data.copy()
        self.toggle_p1 = toggle_p1
        self.toggle_p2 = toggle_p2
        self.l1 = l1
        self.r1 = r1
        self.l2 = l2
        self.r2 = r2
        
        # Initialize result columns
        self._initialize_columns()
        
    def _initialize_columns(self):
        """Initialize all signal and pivot columns"""
        # Pivot columns
        self.data['R1'] = np.nan
        self.data['S1'] = np.nan
        self.data['R2'] = np.nan
        self.data['S2'] = np.nan
        
        # Signal columns for P1
        self.data['rBOP1'] = False
        self.data['rBOLP1'] = False
        self.data['rBOFP1'] = False
        self.data['rRJP1'] = False
        self.data['rIBP1'] = False
        self.data['sBDP1'] = False
        self.data['sBDLP1'] = False
        self.data['sBDFP1'] = False
        self.data['sRJP1'] = False
        self.data['sIBP1'] = False
        
        # Signal columns for P2
        self.data['rBOP2'] = False
        self.data['rBOLP2'] = False
        self.data['rBOFP2'] = False
        self.data['rRJP2'] = False
        self.data['rIBP2'] = False
        self.data['sBDP2'] = False
        self.data['sBDLP2'] = False
        self.data['sBDFP2'] = False
        self.data['sRJP2'] = False
        self.data['sIBP2'] = False
        
        # Combined signals
        self.data['bullP1'] = False
        self.data['bullP2'] = False
        self.data['bearP1'] = False
        self.data['bearP2'] = False
        
        # Session flags
        self.data['t1'] = False
        self.data['t2'] = False
        
    def _pivothigh(self, series, left, right):
        """
        Calculate pivot highs matching PineScript's pivothigh function
        
        A pivot high is identified when the high at the center is higher than
        all highs in the left and right windows.
        """
        result = pd.Series(index=series.index, dtype=float)
        
        for i in range(left, len(series) - right):
            center = series.iloc[i]
            left_window = series.iloc[i-left:i]
            right_window = series.iloc[i+1:i+right+1]
            
            if (center > left_window.max() if len(left_window) > 0 else True) and \
               (center > right_window.max() if len(right_window) > 0 else True):
                result.iloc[i] = center
                
        return result
    
    def _pivotlow(self, series, left, right):
        """
        Calculate pivot lows matching PineScript's pivotlow function
        
        A pivot low is identified when the low at the center is lower than
        all lows in the left and right windows.
        """
        result = pd.Series(index=series.index, dtype=float)
        
        for i in range(left, len(series) - right):
            center = series.iloc[i]
            left_window = series.iloc[i-left:i]
            right_window = series.iloc[i+1:i+right+1]
            
            if (center < left_window.min() if len(left_window) > 0 else True) and \
               (center < right_window.min() if len(right_window) > 0 else True):
                result.iloc[i] = center
                
        return result
    
    def _fixnan(self, series):
        """
        Forward fill NaN values matching PineScript's fixnan function
        """
        return series.ffill()
    
    def _calculate_sessions(self):
        """
        Calculate session time filters matching PineScript logic
        t1: 9:00 to 11:00
        t2: 11:00 to 16:00
        """
        for idx in self.data.index:
            if 'timestamp' in self.data.columns:
                ts = pd.to_datetime(self.data.loc[idx, 'timestamp'])
                current_time = ts.time()
                
                # t1 session: 9:00 to 11:00 (exclusive end)
                self.data.loc[idx, 't1'] = (
                    current_time >= time(9, 0) and 
                    current_time < time(11, 0)
                )
                
                # t2 session: 11:00 to 16:00 (inclusive end)
                self.data.loc[idx, 't2'] = (
                    current_time >= time(11, 0) and 
                    current_time <= time(16, 0)
                )
    
    def _calculate_pivots(self):
        """
        Calculate pivot points R1, S1, R2, S2 matching PineScript logic
        """
        # Calculate raw pivots
        r1_raw = self._pivothigh(self.data['high'], self.l1, self.r1)
        s1_raw = self._pivotlow(self.data['low'], self.l1, self.r1)
        r2_raw = self._pivothigh(self.data['high'], self.l2, self.r2)
        s2_raw = self._pivotlow(self.data['low'], self.l2, self.r2)
        
        # Apply fixnan (forward fill)
        self.data['R1'] = self._fixnan(r1_raw)
        self.data['S1'] = self._fixnan(s1_raw)
        self.data['R2'] = self._fixnan(r2_raw)
        self.data['S2'] = self._fixnan(s2_raw)
    
    def _calculate_filters(self):
        """
        Calculate filter conditions matching PineScript logic
        noAboveR1: No close above R1 in last 10 bars
        noBelowS1: No close below S1 in last 10 bars
        noAboveR2: No close above R2 in last 10 bars
        noBelowS2: No close below S2 in last 10 bars
        """
        window = 10
        
        self.data['noAboveR1'] = False
        self.data['noBelowS1'] = False
        self.data['noAboveR2'] = False
        self.data['noBelowS2'] = False
        
        for i in range(window, len(self.data)):
            # Check previous 10 bars (indices i-10 to i-1)
            prev_closes = self.data['close'].iloc[i-window:i]
            
            # noAboveR1: sum of (close[1] > R1[1]) over 10 bars == 0
            r1_prev = self.data['R1'].iloc[i-window:i]
            self.data.loc[self.data.index[i], 'noAboveR1'] = \
                not (prev_closes > r1_prev).any()
            
            # noBelowS1: sum of (close[1] < S1[1]) over 10 bars == 0
            s1_prev = self.data['S1'].iloc[i-window:i]
            self.data.loc[self.data.index[i], 'noBelowS1'] = \
                not (prev_closes < s1_prev).any()
            
            # noAboveR2: sum of (close[1] > R2[1]) over 10 bars == 0
            r2_prev = self.data['R2'].iloc[i-window:i]
            self.data.loc[self.data.index[i], 'noAboveR2'] = \
                not (prev_closes > r2_prev).any()
            
            # noBelowS2: sum of (close[1] < S2[1]) over 10 bars == 0
            s2_prev = self.data['S2'].iloc[i-window:i]
            self.data.loc[self.data.index[i], 'noBelowS2'] = \
                not (prev_closes < s2_prev).any()
    
    def _calculate_candle_filters(self):
        """
        Calculate candle body filters matching PineScript logic
        bullBody: (high - close) <= (close - low) / 3
        bearBody: (close - low) <= (high - close) / 3
        """
        o = self.data['open']
        h = self.data['high']
        l = self.data['low']
        c = self.data['close']
        
        self.data['bullBody'] = (h - c) <= (c - l) / 3
        self.data['bearBody'] = (c - l) <= (h - c) / 3
    
    def _calculate_signals(self):
        """
        Calculate all trading signals matching PineScript logic
        Includes both t1 and t2 session conditions
        """
        for i in range(1, len(self.data)):
            idx = self.data.index[i]
            prev_idx = self.data.index[i-1]
            
            # Current bar values
            o = self.data.loc[idx, 'open']
            h = self.data.loc[idx, 'high']
            l = self.data.loc[idx, 'low']
            c = self.data.loc[idx, 'close']
            
            # Previous bar values
            h_prev = self.data.loc[prev_idx, 'high']
            l_prev = self.data.loc[prev_idx, 'low']
            
            # Pivot values
            R1 = self.data.loc[idx, 'R1']
            S1 = self.data.loc[idx, 'S1']
            R2 = self.data.loc[idx, 'R2']
            S2 = self.data.loc[idx, 'S2']
            
            # Candle filters
            bullBody = self.data.loc[idx, 'bullBody']
            bearBody = self.data.loc[idx, 'bearBody']
            
            # Session flags
            t1 = self.data.loc[idx, 't1']
            t2 = self.data.loc[idx, 't2']
            
            # Filter conditions (for t2 session)
            noAboveR1 = self.data.loc[idx, 'noAboveR1']
            noBelowS1 = self.data.loc[idx, 'noBelowS1']
            noAboveR2 = self.data.loc[idx, 'noAboveR2']
            noBelowS2 = self.data.loc[idx, 'noBelowS2']
            
            # ============= T1 SESSION LOGIC =============
            if t1:
                # P1 Signals
                self.data.loc[idx, 'rBOP1'] = (
                    not pd.isna(R1) and o < R1 and c > R1 and bullBody
                )
                self.data.loc[idx, 'rBOLP1'] = (
                    not pd.isna(R1) and l < R1 and c > R1 and bullBody
                )
                self.data.loc[idx, 'rBOFP1'] = (
                    not pd.isna(R1) and h > R1 and c < R1 and bearBody
                )
                self.data.loc[idx, 'rRJP1'] = (
                    not pd.isna(R1) and o > R1 and c < R1 and bearBody
                )
                self.data.loc[idx, 'rIBP1'] = (
                    not pd.isna(R1) and l_prev < R1 and h_prev > R1 and
                    h < h_prev and l > l_prev and bearBody
                )
                
                self.data.loc[idx, 'sBDP1'] = (
                    not pd.isna(S1) and o > S1 and c < S1 and bearBody
                )
                self.data.loc[idx, 'sBDLP1'] = (
                    not pd.isna(S1) and h > S1 and c < S1 and bearBody
                )
                self.data.loc[idx, 'sBDFP1'] = (
                    not pd.isna(S1) and l < S1 and c > S1 and bullBody
                )
                self.data.loc[idx, 'sRJP1'] = (
                    not pd.isna(S1) and o < S1 and c > S1 and bullBody
                )
                self.data.loc[idx, 'sIBP1'] = (
                    not pd.isna(S1) and h_prev > S1 and l_prev < S1 and
                    h < h_prev and l > l_prev and bullBody
                )
                
                # P2 Signals
                self.data.loc[idx, 'rBOP2'] = (
                    not pd.isna(R2) and o < R2 and c > R2 and bullBody
                )
                self.data.loc[idx, 'rBOLP2'] = (
                    not pd.isna(R2) and l < R2 and c > R2 and bullBody
                )
                self.data.loc[idx, 'rBOFP2'] = (
                    not pd.isna(R2) and h > R2 and c < R2 and bearBody
                )
                self.data.loc[idx, 'rRJP2'] = (
                    not pd.isna(R2) and o > R2 and c < R2 and bearBody
                )
                self.data.loc[idx, 'rIBP2'] = (
                    not pd.isna(R2) and l_prev < R2 and h_prev > R2 and
                    h < h_prev and l > l_prev and bearBody
                )
                
                self.data.loc[idx, 'sBDP2'] = (
                    not pd.isna(S2) and o > S2 and c < S2 and bearBody
                )
                self.data.loc[idx, 'sBDLP2'] = (
                    not pd.isna(S2) and h > S2 and c < S2 and bearBody
                )
                self.data.loc[idx, 'sBDFP2'] = (
                    not pd.isna(S2) and l < S2 and c > S2 and bullBody
                )
                self.data.loc[idx, 'sRJP2'] = (
                    not pd.isna(S2) and o < S2 and c > S2 and bullBody
                )
                self.data.loc[idx, 'sIBP2'] = (
                    not pd.isna(S2) and h_prev > S2 and l_prev < S2 and
                    h < h_prev and l > l_prev and bullBody
                )
            
            # ============= T2 SESSION LOGIC =============
            elif t2:
                # P1 Signals (limited set with additional filters)
                self.data.loc[idx, 'rBOP1'] = (
                    not pd.isna(R1) and noAboveR1 and o < R1 and c > R1 and bullBody
                )
                self.data.loc[idx, 'rRJP1'] = (
                    not pd.isna(R1) and o > R1 and c < R1 and bearBody
                )
                self.data.loc[idx, 'rIBP1'] = (
                    not pd.isna(R1) and l_prev < R1 and h_prev > R1 and
                    h < h_prev and l > l_prev and bearBody
                )
                
                self.data.loc[idx, 'sBDP1'] = (
                    not pd.isna(S1) and noBelowS1 and o > S1 and c < S1 and bearBody
                )
                self.data.loc[idx, 'sRJP1'] = (
                    not pd.isna(S1) and o < S1 and c > S1 and bullBody
                )
                self.data.loc[idx, 'sIBP1'] = (
                    not pd.isna(S1) and h_prev > S1 and l_prev < S1 and
                    h < h_prev and l > l_prev and bullBody
                )
                
                # P2 Signals (limited set with additional filters)
                self.data.loc[idx, 'rBOP2'] = (
                    not pd.isna(R2) and noAboveR2 and o < R2 and c > R2 and bullBody
                )
                self.data.loc[idx, 'rRJP2'] = (
                    not pd.isna(R2) and o > R2 and c < R2 and bearBody
                )
                self.data.loc[idx, 'rIBP2'] = (
                    not pd.isna(R2) and l_prev < R2 and h_prev > R2 and
                    h < h_prev and l > l_prev and bearBody
                )
                
                self.data.loc[idx, 'sBDP2'] = (
                    not pd.isna(S2) and noBelowS2 and o > S2 and c < S2 and bearBody
                )
                self.data.loc[idx, 'sRJP2'] = (
                    not pd.isna(S2) and o < S2 and c > S2 and bullBody
                )
                self.data.loc[idx, 'sIBP2'] = (
                    not pd.isna(S2) and h_prev > S2 and l_prev < S2 and
                    h < h_prev and l > l_prev and bullBody
                )
    
    def _calculate_combined_signals(self):
        """
        Calculate combined bull/bear signals matching PineScript logic
        bullP1 = toggleP1 and (rBOP1 or rBOLP1 or sRJP1 or sIBP1 or sBDFP1)
        bearP1 = toggleP1 and (sBDP1 or sBDLP1 or rRJP1 or rIBP1 or rBOFP1)
        bullP2 = toggleP2 and (rBOP2 or rBOLP2 or sRJP2 or sIBP2 or sBDFP2)
        bearP2 = toggleP2 and (sBDP2 or sBDLP2 or rRJP2 or rIBP2 or rBOFP2)
        """
        self.data['bullP1'] = self.toggle_p1 & (
            self.data['rBOP1'] | self.data['rBOLP1'] | 
            self.data['sRJP1'] | self.data['sIBP1'] | self.data['sBDFP1']
        )
        
        self.data['bearP1'] = self.toggle_p1 & (
            self.data['sBDP1'] | self.data['sBDLP1'] | 
            self.data['rRJP1'] | self.data['rIBP1'] | self.data['rBOFP1']
        )
        
        self.data['bullP2'] = self.toggle_p2 & (
            self.data['rBOP2'] | self.data['rBOLP2'] | 
            self.data['sRJP2'] | self.data['sIBP2'] | self.data['sBDFP2']
        )
        
        self.data['bearP2'] = self.toggle_p2 & (
            self.data['sBDP2'] | self.data['sBDLP2'] | 
            self.data['rRJP2'] | self.data['rIBP2'] | self.data['rBOFP2']
        )
    
    def _calculate_measured_moves(self):
        """
        Calculate measured move targets matching PineScript logic
        
        For bullish signals: target = close + (close - S1)
        For bearish signals: target = close - (R1 - close)
        """
        self.data['bull_target'] = np.nan
        self.data['bear_target'] = np.nan
        
        # Bullish measured moves
        bull_mask = self.data['bullP1'] | self.data['bullP2']
        self.data.loc[bull_mask, 'bull_target'] = \
            self.data.loc[bull_mask, 'close'] + \
            (self.data.loc[bull_mask, 'close'] - self.data.loc[bull_mask, 'S1'])
        
        # Bearish measured moves
        bear_mask = self.data['bearP1'] | self.data['bearP2']
        self.data.loc[bear_mask, 'bear_target'] = \
            self.data.loc[bear_mask, 'close'] - \
            (self.data.loc[bear_mask, 'R1'] - self.data.loc[bear_mask, 'close'])
    
    def calculate(self):
        """
        Run the complete indicator calculation matching PineScript logic
        
        Returns:
            DataFrame with all signals and pivot levels
        """
        # Step 1: Calculate session times
        self._calculate_sessions()
        
        # Step 2: Calculate pivot points
        self._calculate_pivots()
        
        # Step 3: Calculate filter conditions
        self._calculate_filters()
        
        # Step 4: Calculate candle body filters
        self._calculate_candle_filters()
        
        # Step 5: Calculate all signals
        self._calculate_signals()
        
        # Step 6: Calculate combined signals
        self._calculate_combined_signals()
        
        # Step 7: Calculate measured moves
        self._calculate_measured_moves()
        
        return self.data
    
    def get_signals(self):
        """
        Get only the signal columns for easy analysis
        
        Returns:
            DataFrame with signal columns and basic OHLC data
        """
        signal_cols = [
            'timestamp', 'open', 'high', 'low', 'close',
            'R1', 'S1', 'R2', 'S2',
            't1', 't2',
            'bullP1', 'bearP1', 'bullP2', 'bearP2',
            'bull_target', 'bear_target'
        ]
        return self.data[[col for col in signal_cols if col in self.data.columns]]


def main():
    """
    Example usage of the SR-MM-L indicator
    """
    # Example: Create sample data
    # In real usage, load your OHLC data with timestamps
    dates = pd.date_range('2024-01-01 09:00:00', periods=200, freq='5min')
    
    # Generate sample price data (replace with real data)
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 0.5)
    high = close + np.abs(np.random.randn(200) * 0.3)
    low = close - np.abs(np.random.randn(200) * 0.3)
    open_price = close + np.random.randn(200) * 0.2
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close
    })
    
    # Initialize and calculate indicator
    indicator = SRMMLIndicator(
        data=data,
        toggle_p1=True,
        toggle_p2=True,
        l1=15,
        r1=15,
        l2=30,
        r2=30
    )
    
    results = indicator.calculate()
    signals = indicator.get_signals()
    
    # Print signals
    print("SR-MM-L Indicator Results:")
    print("=" * 80)
    print(f"Total bars: {len(results)}")
    print(f"Bullish P1 signals: {results['bullP1'].sum()}")
    print(f"Bearish P1 signals: {results['bearP1'].sum()}")
    print(f"Bullish P2 signals: {results['bullP2'].sum()}")
    print(f"Bearish P2 signals: {results['bearP2'].sum()}")
    print("\nRecent Signals:")
    print(signals.tail(10))


if __name__ == "__main__":
    main()
