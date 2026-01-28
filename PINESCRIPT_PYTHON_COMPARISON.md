# PineScript to Python Comparison - SR-MM-L Indicator

This document provides a detailed comparison between the PineScript code and the Python implementation to verify that all conditions and logic are correctly implemented.

## ✅ 1. Input Parameters

| PineScript | Python | Status |
|------------|--------|--------|
| `toggleP1 = input(true, "Show P1 Signals")` | `toggle_p1=True` | ✅ Matched |
| `toggleP2 = input(true, "Show P2 Signals")` | `toggle_p2=True` | ✅ Matched |
| `l1 = input(15, "Left Bars P1")` | `l1=15` | ✅ Matched |
| `r1 = input(15, "Right Bars P1")` | `r1=15` | ✅ Matched |
| `l2 = input(30, "Left Bars P2")` | `l2=30` | ✅ Matched |
| `r2 = input(30, "Right Bars P2")` | `r2=30` | ✅ Matched |

## ✅ 2. Session Time Filters

| PineScript | Python | Status |
|------------|--------|--------|
| `t1 = time >= timestamp(year, month, dayofmonth, 9, 0) and time < timestamp(year, month, dayofmonth, 11, 0)` | `current_time >= time(9, 0) and current_time < time(11, 0)` | ✅ Matched |
| `t2 = time >= timestamp(year, month, dayofmonth, 11, 0) and time <= timestamp(year, month, dayofmonth, 16, 0)` | `current_time >= time(11, 0) and current_time <= time(16, 0)` | ✅ Matched |

**Note:** Both implementations correctly handle:
- t1: 9:00 AM to 11:00 AM (exclusive end)
- t2: 11:00 AM to 4:00 PM (inclusive end)

## ✅ 3. Pivot Point Calculations

| PineScript | Python | Status |
|------------|--------|--------|
| `R1 = fixnan(pivothigh(l1, r1))` | `self._fixnan(self._pivothigh(self.data['high'], self.l1, self.r1))` | ✅ Matched |
| `S1 = fixnan(pivotlow(l1, r1))` | `self._fixnan(self._pivotlow(self.data['low'], self.l1, self.r1))` | ✅ Matched |
| `R2 = fixnan(pivothigh(l2, r2))` | `self._fixnan(self._pivothigh(self.data['high'], self.l2, self.r2))` | ✅ Matched |
| `S2 = fixnan(pivotlow(l2, r2))` | `self._fixnan(self._pivotlow(self.data['low'], self.l2, self.r2))` | ✅ Matched |

**Implementation Details:**
- `pivothigh`: Identifies highs where the center value is higher than all values in left and right windows
- `pivotlow`: Identifies lows where the center value is lower than all values in left and right windows
- `fixnan`: Forward fills NaN values (equivalent to pandas `fillna(method='ffill')`)

## ✅ 4. Filter Conditions

| PineScript | Python | Status |
|------------|--------|--------|
| `noAboveR1 = sum(close[1] > R1[1] ? 1 : 0, 10) == 0` | `not (prev_closes > r1_prev).any()` over 10 bars | ✅ Matched |
| `noBelowS1 = sum(close[1] < S1[1] ? 1 : 0, 10) == 0` | `not (prev_closes < s1_prev).any()` over 10 bars | ✅ Matched |
| `noAboveR2 = sum(close[1] > R2[1] ? 1 : 0, 10) == 0` | `not (prev_closes > r2_prev).any()` over 10 bars | ✅ Matched |
| `noBelowS2 = sum(close[1] < S2[1] ? 1 : 0, 10) == 0` | `not (prev_closes < s2_prev).any()` over 10 bars | ✅ Matched |

**Logic:** These filters check if NO close in the previous 10 bars was above/below the respective pivot level.

## ✅ 5. Candle Body Filters

| PineScript | Python | Status |
|------------|--------|--------|
| `bullBody = (high - close) <= (close - low) / 3` | `(h - c) <= (c - l) / 3` | ✅ Matched |
| `bearBody = (close - low) <= (high - close) / 3` | `(c - l) <= (h - c) / 3` | ✅ Matched |

**Purpose:** 
- `bullBody`: Confirms bullish candle with small upper wick
- `bearBody`: Confirms bearish candle with small lower wick

## ✅ 6. Signal Declarations (T1 Session - 9:00 to 11:00)

### P1 Resistance Signals (Bullish)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| rBOP1 | `not na(R1) and open < R1 and close > R1 and bullBody` | Same logic | ✅ Matched |
| rBOLP1 | `not na(R1) and low < R1 and close > R1 and bullBody` | Same logic | ✅ Matched |
| rBOFP1 | `not na(R1) and high > R1 and close < R1 and bearBody` | Same logic | ✅ Matched |
| rRJP1 | `not na(R1) and open > R1 and close < R1 and bearBody` | Same logic | ✅ Matched |
| rIBP1 | `not na(R1) and low[1] < R1 and high[1] > R1 and high < high[1] and low > low[1] and bearBody` | Same logic | ✅ Matched |

### P1 Support Signals (Bearish)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| sBDP1 | `not na(S1) and open > S1 and close < S1 and bearBody` | Same logic | ✅ Matched |
| sBDLP1 | `not na(S1) and high > S1 and close < S1 and bearBody` | Same logic | ✅ Matched |
| sBDFP1 | `not na(S1) and low < S1 and close > S1 and bullBody` | Same logic | ✅ Matched |
| sRJP1 | `not na(S1) and open < S1 and close > S1 and bullBody` | Same logic | ✅ Matched |
| sIBP1 | `not na(S1) and high[1] > S1 and low[1] < S1 and high < high[1] and low > low[1] and bullBody` | Same logic | ✅ Matched |

### P2 Resistance Signals (Bullish)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| rBOP2 | `not na(R2) and open < R2 and close > R2 and bullBody` | Same logic | ✅ Matched |
| rBOLP2 | `not na(R2) and low < R2 and close > R2 and bullBody` | Same logic | ✅ Matched |
| rBOFP2 | `not na(R2) and high > R2 and close < R2 and bearBody` | Same logic | ✅ Matched |
| rRJP2 | `not na(R2) and open > R2 and close < R2 and bearBody` | Same logic | ✅ Matched |
| rIBP2 | `not na(R2) and low[1] < R2 and high[1] > R2 and high < high[1] and low > low[1] and bearBody` | Same logic | ✅ Matched |

### P2 Support Signals (Bearish)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| sBDP2 | `not na(S2) and open > S2 and close < S2 and bearBody` | Same logic | ✅ Matched |
| sBDLP2 | `not na(S2) and high > S2 and close < S2 and bearBody` | Same logic | ✅ Matched |
| sBDFP2 | `not na(S2) and low < S2 and close > S2 and bullBody` | Same logic | ✅ Matched |
| sRJP2 | `not na(S2) and open < S2 and close > S2 and bullBody` | Same logic | ✅ Matched |
| sIBP2 | `not na(S2) and high[1] > S2 and low[1] < S2 and high < high[1] and low > low[1] and bullBody` | Same logic | ✅ Matched |

## ✅ 7. Signal Declarations (T2 Session - 11:00 to 16:00)

**KEY DIFFERENCE:** In t2 session, only specific signals are active, and some require additional filters.

### P1 Signals (Limited Set)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| rBOP1 | `not na(R1) and noAboveR1 and open < R1 and close > R1 and bullBody` | Same logic with noAboveR1 | ✅ Matched |
| rRJP1 | `not na(R1) and open > R1 and close < R1 and bearBody` | Same logic | ✅ Matched |
| rIBP1 | `not na(R1) and low[1] < R1 and high[1] > R1 and high < high[1] and low > low[1] and bearBody` | Same logic | ✅ Matched |
| sBDP1 | `not na(S1) and noBelowS1 and open > S1 and close < S1 and bearBody` | Same logic with noBelowS1 | ✅ Matched |
| sRJP1 | `not na(S1) and open < S1 and close > S1 and bullBody` | Same logic | ✅ Matched |
| sIBP1 | `not na(S1) and high[1] > S1 and low[1] < S1 and high < high[1] and low > low[1] and bullBody` | Same logic | ✅ Matched |

**Missing in T2:** rBOLP1, rBOFP1, sBDLP1, sBDFP1 (correctly excluded in Python)

### P2 Signals (Limited Set)

| Signal | PineScript Condition | Python Implementation | Status |
|--------|---------------------|----------------------|--------|
| rBOP2 | `not na(R2) and noAboveR2 and open < R2 and close > R2 and bullBody` | Same logic with noAboveR2 | ✅ Matched |
| rRJP2 | `not na(R2) and open > R2 and close < R2 and bearBody` | Same logic | ✅ Matched |
| rIBP2 | `not na(R2) and low[1] < R2 and high[1] > R2 and high < high[1] and low > low[1] and bearBody` | Same logic | ✅ Matched |
| sBDP2 | `not na(S2) and noBelowS2 and open > S2 and close < S2 and bearBody` | Same logic with noBelowS2 | ✅ Matched |
| sRJP2 | `not na(S2) and open < S2 and close > S2 and bullBody` | Same logic | ✅ Matched |
| sIBP2 | `not na(S2) and high[1] > S2 and low[1] < S2 and high < high[1] and low > low[1] and bullBody` | Same logic | ✅ Matched |

**Missing in T2:** rBOLP2, rBOFP2, sBDLP2, sBDFP2 (correctly excluded in Python)

## ✅ 8. Combined Signal Logic

| PineScript | Python | Status |
|------------|--------|--------|
| `bullP1 = toggleP1 and (rBOP1 or rBOLP1 or sRJP1 or sIBP1 or sBDFP1)` | `self.toggle_p1 & (self.data['rBOP1'] \| ... \| self.data['sBDFP1'])` | ✅ Matched |
| `bearP1 = toggleP1 and (sBDP1 or sBDLP1 or rRJP1 or rIBP1 or rBOFP1)` | `self.toggle_p1 & (self.data['sBDP1'] \| ... \| self.data['rBOFP1'])` | ✅ Matched |
| `bullP2 = toggleP2 and (rBOP2 or rBOLP2 or sRJP2 or sIBP2 or sBDFP2)` | `self.toggle_p2 & (self.data['rBOP2'] \| ... \| self.data['sBDFP2'])` | ✅ Matched |
| `bearP2 = toggleP2 and (sBDP2 or sBDLP2 or rRJP2 or rIBP2 or rBOFP2)` | `self.toggle_p2 & (self.data['sBDP2'] \| ... \| self.data['rBOFP2'])` | ✅ Matched |

## ✅ 9. Measured Moves

| PineScript | Python | Status |
|------------|--------|--------|
| Bullish: `tgt = close + (close - S1)` | `close + (close - S1)` | ✅ Matched |
| Bearish: `tgt = close - (R1 - close)` | `close - (R1 - close)` | ✅ Matched |

**Implementation:** Targets are calculated for both `bullP1 or bullP2` and `bearP1 or bearP2` signals.

## 📋 Summary of All Conditions

### ✅ All Implemented Features:

1. **Input Parameters** - All 6 parameters correctly mapped
2. **Session Filters** - Both t1 and t2 sessions with correct time ranges
3. **Pivot Calculations** - R1, S1, R2, S2 with fixnan
4. **Filter Conditions** - All 4 filter conditions (noAboveR1, noBelowS1, noAboveR2, noBelowS2)
5. **Candle Filters** - bullBody and bearBody
6. **T1 Session Signals** - All 20 signals (10 for P1, 10 for P2)
7. **T2 Session Signals** - Correct subset of 12 signals (6 for P1, 6 for P2) with additional filters
8. **Combined Signals** - All 4 combined signals (bullP1, bearP1, bullP2, bearP2)
9. **Measured Moves** - Both bullish and bearish target calculations

### 🎯 Key Differences Between T1 and T2 (Correctly Implemented):

**T1 Session (9:00-11:00):**
- All 20 signals active (10 per pivot level)
- No additional filters required

**T2 Session (11:00-16:00):**
- Only 12 signals active (6 per pivot level)
- Additional filters required for breakout signals (noAboveR1/R2, noBelowS1/S2)
- Missing signals in T2: rBOLP1, rBOFP1, sBDLP1, sBDFP1, rBOLP2, rBOFP2, sBDLP2, sBDFP2

### 📊 Signal Pattern Meanings:

- **rBO** (Resistance Breakout): Open below, close above resistance
- **rBOL** (Resistance Breakout Low): Low below, close above resistance
- **rBOF** (Resistance Breakout Fail): High above, close below resistance
- **rRJ** (Resistance Rejection): Open above, close below resistance
- **rIB** (Resistance Inside Bar): Previous bar engulfed resistance, current bar inside
- **sBD** (Support Breakdown): Open above, close below support
- **sBDL** (Support Breakdown Low): High above, close below support
- **sBDF** (Support Breakdown Fail): Low below, close above support
- **sRJ** (Support Rejection): Open below, close above support
- **sIB** (Support Inside Bar): Previous bar engulfed support, current bar inside

## ✅ Conclusion

The Python implementation **CORRECTLY** implements all conditions and logic from the PineScript code:

- ✅ All input parameters matched
- ✅ Session time filters correctly implemented
- ✅ Pivot calculations using proper algorithms
- ✅ Filter conditions correctly calculated
- ✅ All candle body filters implemented
- ✅ All 20 T1 session signals correctly implemented
- ✅ Correct subset of 12 T2 session signals with additional filters
- ✅ Combined signal logic matches exactly
- ✅ Measured move calculations identical
- ✅ Proper handling of NaN values and array indexing

**The Python code is a complete and accurate translation of the PineScript indicator.**
