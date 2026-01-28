# Trading Backtesting System

This Python script implements a trading backtesting and AI training system for analyzing TSLA 5-minute trading data.

## Overview

The script performs three main functions:
1. **Data Preparation & Labeling**: Processes historical price data and identifies trading setup patterns
2. **Backtesting**: Simulates trades based on identified patterns
3. **AI Training**: Uses machine learning to analyze which setups perform best

## Features

- **Pivot Point Detection**: Identifies resistance (R1, R2) and support (S1, S2) levels using a Pine Script-inspired algorithm
- **Technical Indicators**: Calculates RSI, volatility, and candlestick body characteristics
- **Multiple Trading Setups**: Identifies 10 different bullish and bearish patterns
- **AI-Powered Analysis**: Uses Random Forest classifier to evaluate setup performance
- **Setup Performance Metrics**: Detailed win-rate analysis by setup type

## Requirements

```bash
pip install pandas numpy scikit-learn
```

## Usage

1. Place your TSLA 5-minute data CSV in the `static/` directory
2. Run the script:
   ```bash
   python trading_backtest.py
   ```

## Data Format

The CSV file should contain the following columns:
- `date`: Timestamp
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price

## Configuration

Key parameters can be adjusted at the top of the script:
- `CSV_PATH`: Path to the data file
- `L1, R1_LEN`: First pivot lookback/lookahead periods (default: 15)
- `L2, R2_LEN`: Second pivot lookback/lookahead periods (default: 30)
- `TICK_SIZE`: Price increment (default: 0.01)
- `TICKS_BUFFER`: Entry buffer in ticks (default: 2)

## Output

The script outputs:
1. Setup performance metrics showing win rates for each pattern
2. AI model performance metrics on validation set
3. Feature importance analysis showing key drivers of success
