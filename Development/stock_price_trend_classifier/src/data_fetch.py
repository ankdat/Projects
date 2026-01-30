import yfinance as yf
import pandas as pd
from pathlib import Path


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical stock price data from Yahoo Finance.
    """
    df = yf.download(ticker, start=start_date, end=end_date)
    return df


def save_raw_data(df: pd.DataFrame, ticker: str):
    """
    Save raw stock data to data/raw directory.
    """
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = data_dir / f"{ticker}.csv"
    df.to_csv(file_path)
    print(f"Raw data saved to {file_path}")


if __name__ == "__main__":
    ticker = "AAPL"          # we start with ONE stock
    start_date = "2024-01-01"
    end_date = "2026-01-15"

    df = fetch_stock_data(ticker, start_date, end_date)
    save_raw_data(df, ticker)
