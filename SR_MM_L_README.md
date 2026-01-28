# SR-MM-L (Support/Resistance Measured Moves) Indicator - Python Implementation

## Overview

This is a complete Python implementation of the PineScript "SR-MM-L (Clean)" trading indicator. The indicator identifies support and resistance levels using pivot points and generates trading signals based on price action patterns.

## Files

- **`sr_mm_l_indicator.py`** - Main indicator implementation
- **`test_sr_mm_l_indicator.py`** - Comprehensive test suite
- **`PINESCRIPT_PYTHON_COMPARISON.md`** - Detailed comparison showing all conditions match

## Features

### ✅ Complete PineScript Logic Implementation

All conditions and logic from the original PineScript code are correctly implemented:

1. **Input Parameters**
   - `toggle_p1`, `toggle_p2` - Enable/disable P1 and P2 signals
   - `l1`, `r1` - Left and right bars for P1 pivot calculation
   - `l2`, `r2` - Left and right bars for P2 pivot calculation

2. **Session Time Filters**
   - `t1`: 9:00 AM to 11:00 AM (morning session, exclusive end)
   - `t2`: 11:00 AM to 4:00 PM (afternoon session, inclusive end)

3. **Pivot Points**
   - `R1`, `S1` - Resistance and Support using P1 parameters
   - `R2`, `S2` - Resistance and Support using P2 parameters
   - Uses `pivothigh` and `pivotlow` algorithms
   - `fixnan` forward fills pivot values

4. **Filter Conditions** (used in t2 session)
   - `noAboveR1` - No close above R1 in last 10 bars
   - `noBelowS1` - No close below S1 in last 10 bars
   - `noAboveR2` - No close above R2 in last 10 bars
   - `noBelowS2` - No close below S2 in last 10 bars

5. **Candle Body Filters**
   - `bullBody`: `(high - close) <= (close - low) / 3`
   - `bearBody`: `(close - low) <= (high - close) / 3`

6. **Trading Signals** (20 signals total)

   **T1 Session (9:00-11:00) - All Signals Active:**
   - **P1 Signals (10):**
     - `rBOP1` - Resistance Breakout
     - `rBOLP1` - Resistance Breakout Low
     - `rBOFP1` - Resistance Breakout Fail
     - `rRJP1` - Resistance Rejection
     - `rIBP1` - Resistance Inside Bar
     - `sBDP1` - Support Breakdown
     - `sBDLP1` - Support Breakdown Low
     - `sBDFP1` - Support Breakdown Fail
     - `sRJP1` - Support Rejection
     - `sIBP1` - Support Inside Bar
   
   - **P2 Signals (10):** Same pattern types for R2/S2 levels

   **T2 Session (11:00-16:00) - Limited Signals with Additional Filters:**
   - Only 12 signals active (6 for P1, 6 for P2)
   - Active: `rBOP`, `rRJ`, `rIB`, `sBD`, `sRJ`, `sIB`
   - Inactive: `rBOL`, `rBOF`, `sBDL`, `sBDF`
   - Breakout signals require additional filters (`noAboveR1/R2`, `noBelowS1/S2`)

7. **Combined Signals**
   - `bullP1` = `toggleP1 and (rBOP1 or rBOLP1 or sRJP1 or sIBP1 or sBDFP1)`
   - `bearP1` = `toggleP1 and (sBDP1 or sBDLP1 or rRJP1 or rIBP1 or rBOFP1)`
   - `bullP2` = `toggleP2 and (rBOP2 or rBOLP2 or sRJP2 or sIBP2 or sBDFP2)`
   - `bearP2` = `toggleP2 and (sBDP2 or sBDLP2 or rRJP2 or rIBP2 or rBOFP2)`

8. **Measured Moves**
   - Bullish target: `close + (close - S1)`
   - Bearish target: `close - (R1 - close)`

## Installation

```bash
pip install pandas numpy
```

## Usage

### Basic Usage

```python
import pandas as pd
from sr_mm_l_indicator import SRMMLIndicator

# Load your OHLC data
# DataFrame must have columns: 'timestamp', 'open', 'high', 'low', 'close'
data = pd.DataFrame({
    'timestamp': [...],  # DateTime objects
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...]
})

# Initialize the indicator
indicator = SRMMLIndicator(
    data=data,
    toggle_p1=True,    # Show P1 signals
    toggle_p2=True,    # Show P2 signals
    l1=15,             # Left bars for P1 pivots
    r1=15,             # Right bars for P1 pivots
    l2=30,             # Left bars for P2 pivots
    r2=30              # Right bars for P2 pivots
)

# Calculate all signals
results = indicator.calculate()

# Get simplified view with just signals
signals = indicator.get_signals()

# Print signal summary
print(f"Bullish P1 signals: {results['bullP1'].sum()}")
print(f"Bearish P1 signals: {results['bearP1'].sum()}")
print(f"Bullish P2 signals: {results['bullP2'].sum()}")
print(f"Bearish P2 signals: {results['bearP2'].sum()}")

# Find all bullish signals
bullish_signals = results[results['bullP1'] | results['bullP2']]
print(bullish_signals[['timestamp', 'close', 'R1', 'S1', 'bull_target']])

# Find all bearish signals
bearish_signals = results[results['bearP1'] | results['bearP2']]
print(bearish_signals[['timestamp', 'close', 'R1', 'S1', 'bear_target']])
```

### Advanced Usage - Filter by Session

```python
# Get T1 session signals only (9:00-11:00)
t1_signals = results[results['t1'] & (results['bullP1'] | results['bearP1'])]

# Get T2 session signals only (11:00-16:00)
t2_signals = results[results['t2'] & (results['bullP1'] | results['bearP1'])]
```

### Custom Parameters

```python
# Use different pivot parameters
indicator = SRMMLIndicator(
    data=data,
    toggle_p1=True,
    toggle_p2=False,  # Disable P2 signals
    l1=10,            # Shorter lookback for P1
    r1=10,
    l2=20,
    r2=20
)
```

## Testing

Run the comprehensive test suite:

```bash
python test_sr_mm_l_indicator.py
```

The test suite verifies:
- ✅ Initialization and parameter handling
- ✅ Session time calculations
- ✅ Candle body filters
- ✅ Pivot point calculations
- ✅ T1 session signal generation
- ✅ T2 session signal generation with filters
- ✅ Combined signal logic
- ✅ Measured move calculations
- ✅ Complete workflow integration

## Signal Patterns Explained

### Resistance Patterns (Bullish)
- **rBO** (Breakout): Open below resistance, close above
- **rBOL** (Breakout Low): Low touches below resistance, close above
- **rBOF** (Breakout Fail): High breaks resistance, close back below (bearish)
- **rRJ** (Rejection): Open above resistance, close below (bearish)
- **rIB** (Inside Bar): Previous bar engulfed resistance, current bar inside (bearish)

### Support Patterns (Bearish)
- **sBD** (Breakdown): Open above support, close below
- **sBDL** (Breakdown Low): High touches above support, close below
- **sBDF** (Breakdown Fail): Low breaks support, close back above (bullish)
- **sRJ** (Rejection): Open below support, close above (bullish)
- **sIB** (Inside Bar): Previous bar engulfed support, current bar inside (bullish)

## Data Requirements

Your input DataFrame must have these columns:
- `timestamp`: DateTime objects with time information
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price

**Important:** The timestamp must include intraday time information for session filtering to work correctly.

## Output Columns

The `calculate()` method returns a DataFrame with all original columns plus:

### Pivot Levels
- `R1`, `S1` - Primary pivot levels
- `R2`, `S2` - Secondary pivot levels

### Session Flags
- `t1`, `t2` - Boolean flags for each session

### Filters
- `noAboveR1`, `noBelowS1`, `noAboveR2`, `noBelowS2`
- `bullBody`, `bearBody`

### Individual Signals (20 total)
- P1: `rBOP1`, `rBOLP1`, `rBOFP1`, `rRJP1`, `rIBP1`, `sBDP1`, `sBDLP1`, `sBDFP1`, `sRJP1`, `sIBP1`
- P2: `rBOP2`, `rBOLP2`, `rBOFP2`, `rRJP2`, `rIBP2`, `sBDP2`, `sBDLP2`, `sBDFP2`, `sRJP2`, `sIBP2`

### Combined Signals
- `bullP1`, `bearP1`, `bullP2`, `bearP2`

### Targets
- `bull_target` - Measured move target for bullish signals
- `bear_target` - Measured move target for bearish signals

## Verification

See `PINESCRIPT_PYTHON_COMPARISON.md` for a detailed line-by-line comparison showing that all conditions and logic from the PineScript code are correctly implemented in Python.

## Key Differences from PineScript

1. **Array Indexing**: Python uses 0-based indexing, PineScript uses offset notation
2. **NaN Handling**: Uses pandas `.ffill()` instead of PineScript's `fixnan()`
3. **Data Structure**: Uses pandas DataFrame instead of PineScript series
4. **Time Handling**: Uses Python's datetime instead of PineScript's timestamp functions

All logical conditions remain identical to the PineScript version.

## Performance Notes

- Pivot calculations use rolling windows - performance scales with data size
- For large datasets (>10,000 bars), consider processing in chunks
- Session filtering is done per-row and is relatively fast
- Most computational cost is in pivot point identification

## License

This implementation is provided as-is for educational and trading purposes.

## Contributing

When modifying the code, ensure all tests pass:
```bash
python test_sr_mm_l_indicator.py
```

Always maintain parity with the original PineScript logic documented in `PINESCRIPT_PYTHON_COMPARISON.md`.
