# Crypto Data Pipeline

A Python-based data pipeline for downloading, cleaning, and updating cryptocurrency market data for quantitative research.

## Project Objective

The objective of this project is to build a reliable and reproducible data pipeline for crypto quantitative research. The pipeline focuses on collecting OHLCV market data, cleaning raw time-series data, handling missing or duplicated records, and storing data in a structured CSV format for future strategy research and backtesting.

## Why This Project Matters

In quantitative trading, data quality is critical. Before building any trading strategy, it is important to make sure that the underlying data is complete, consistent, and correctly formatted. This project demonstrates practical data engineering skills that are directly relevant to systematic trading research.

## Current Features

- Download crypto OHLCV data
- Store market data in CSV format
- Normalize timestamps
- Remove duplicate records
- Prepare datasets for future backtesting
- Organize code for reproducible research

## Planned Features

- Binance API integration
- Incremental data updates
- Data validation checks
- Missing data detection
- Multiple symbol support
- Multiple timeframe support
- Basic return and volatility calculations
- Connection to future momentum strategy backtest

## Tools and Libraries

- Python
- pandas
- requests
- ccxt
- CSV data storage
- Binance market data

## Repository Structure

```text
crypto-data-pipeline/
├── README.md
├── requirements.txt
├── src/
│   └── download_binance_ohlcv.py
└── data/
    └── .gitkeep
```

## Research Use Case

This pipeline is designed to support future research projects such as:

- Crypto momentum strategies
- Trend-following strategies
- Volatility-based position sizing
- Event-driven crypto research
- Cross-sectional coin selection models

## Status

This project is currently completed. The first version focuses on building a clean and reliable Binance OHLCV data pipeline.

## Author

Bryan Wong  
Clinical Pharmacist | Crypto Quant Researcher | Python Algo Trading Developer
