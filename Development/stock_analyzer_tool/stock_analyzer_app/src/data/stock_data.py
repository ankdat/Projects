"""
Stock Data Fetching Module
Provides functionality to fetch real-time and historical stock data from various sources
"""

import sys
import os
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """
    Class to fetch stock data from various sources
    Currently supports:
    - NASDAQ stocks via Yahoo Finance
    - BSE stocks via Yahoo Finance (with BSE ticker format)
    """
    
    def __init__(self):
        """Initialize the StockDataFetcher"""
        self.cache = {}  # Simple cache to store recent data
        self.cache_expiry = {}  # Track when cache entries expire
        self.cache_duration = 60  # Cache duration in seconds for real-time data
        
    def _get_yahoo_ticker(self, symbol, market):
        """
        Convert symbol to Yahoo Finance ticker format based on market
        
        Args:
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            str: Yahoo Finance formatted ticker
        """
        if market.upper() == 'NASDAQ':
            return symbol
        elif market.upper() == 'BSE':
            # BSE tickers in Yahoo Finance are typically appended with .BO
            return f"{symbol}.BO"
        else:
            raise ValueError(f"Unsupported market: {market}. Supported markets are NASDAQ and BSE.")
    
    def get_real_time_data(self, symbol, market='NASDAQ'):
        """
        Get real-time stock data
        
        Args:
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            dict: Real-time stock data
        """
        cache_key = f"{symbol}_{market}_realtime"
        current_time = datetime.now()
        
        # Check if we have cached data that's still valid
        if cache_key in self.cache and current_time < self.cache_expiry.get(cache_key, current_time):
            logger.info(f"Returning cached real-time data for {symbol} ({market})")
            return self.cache[cache_key]
        
        try:
            # Convert to Yahoo Finance ticker format
            ticker = self._get_yahoo_ticker(symbol, market)
            
            # Fetch data using yfinance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get the latest price data
            hist = stock.history(period="1d")
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol} ({market})")
            
            # Extract relevant real-time data
            real_time_data = {
                'symbol': symbol,
                'market': market,
                'name': info.get('shortName', info.get('longName', 'Unknown')),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', None)),
                'previous_close': info.get('previousClose', None),
                'open': hist['Open'].iloc[-1] if not hist.empty else None,
                'high': hist['High'].iloc[-1] if not hist.empty else None,
                'low': hist['Low'].iloc[-1] if not hist.empty else None,
                'volume': hist['Volume'].iloc[-1] if not hist.empty else None,
                'change': info.get('regularMarketChange', None),
                'change_percent': info.get('regularMarketChangePercent', None),
                'market_cap': info.get('marketCap', None),
                'timestamp': datetime.now().isoformat(),
                'currency': info.get('currency', 'USD'),
            }
            
            # Cache the data
            self.cache[cache_key] = real_time_data
            self.cache_expiry[cache_key] = current_time + timedelta(seconds=self.cache_duration)
            
            return real_time_data
            
        except Exception as e:
            logger.error(f"Error fetching real-time data for {symbol} ({market}): {str(e)}")
            raise
    
    def get_historical_data(self, symbol, market='NASDAQ', interval='1d', period='1mo'):
        """
        Get historical stock data
        
        Args:
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            pandas.DataFrame: Historical stock data
        """
        cache_key = f"{symbol}_{market}_{interval}_{period}"
        current_time = datetime.now()
        
        # For historical data, we can cache longer
        cache_duration = 3600  # 1 hour for historical data
        
        # Check if we have cached data that's still valid
        if cache_key in self.cache and current_time < self.cache_expiry.get(cache_key, current_time):
            logger.info(f"Returning cached historical data for {symbol} ({market})")
            return self.cache[cache_key]
        
        try:
            # Convert to Yahoo Finance ticker format
            ticker = self._get_yahoo_ticker(symbol, market)
            
            # Fetch data using yfinance
            stock = yf.Ticker(ticker)
            hist_data = stock.history(period=period, interval=interval)
            
            if hist_data.empty:
                raise ValueError(f"No historical data available for {symbol} ({market})")
            
            # Reset index to make date a column
            hist_data = hist_data.reset_index()
            
            # Convert to dict for caching
            hist_dict = hist_data.to_dict('records')
            
            # Cache the data
            self.cache[cache_key] = hist_dict
            self.cache_expiry[cache_key] = current_time + timedelta(seconds=cache_duration)
            
            return hist_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol} ({market}): {str(e)}")
            raise
    
    def search_stocks(self, query, market=None):
        """
        Search for stocks by name or symbol
        
        Args:
            query (str): Search query
            market (str, optional): Filter by market (NASDAQ or BSE)
            
        Returns:
            list: List of matching stocks
        """
        try:
            # Use yfinance search functionality
            tickers = yf.Tickers(query)
            results = []
            
            for ticker_symbol in tickers.tickers:
                try:
                    ticker = tickers.tickers[ticker_symbol]
                    info = ticker.info
                    
                    # Determine market
                    ticker_market = 'BSE' if '.BO' in ticker_symbol else 'NASDAQ'
                    
                    # Skip if market filter is applied and doesn't match
                    if market and market.upper() != ticker_market:
                        continue
                    
                    stock_info = {
                        'symbol': ticker_symbol.replace('.BO', '') if '.BO' in ticker_symbol else ticker_symbol,
                        'name': info.get('shortName', info.get('longName', 'Unknown')),
                        'market': ticker_market,
                        'currency': info.get('currency', 'USD'),
                    }
                    
                    results.append(stock_info)
                except:
                    # Skip tickers that fail to load
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching for stocks with query '{query}': {str(e)}")
            raise
    
    def get_market_summary(self, market='NASDAQ'):
        """
        Get market summary data
        
        Args:
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            dict: Market summary data
        """
        try:
            if market.upper() == 'NASDAQ':
                # Use ^IXIC for NASDAQ Composite
                index_symbol = '^IXIC'
            elif market.upper() == 'BSE':
                # Use ^BSESN for BSE SENSEX
                index_symbol = '^BSESN'
            else:
                raise ValueError(f"Unsupported market: {market}")
            
            # Fetch index data
            index = yf.Ticker(index_symbol)
            info = index.info
            hist = index.history(period="5d")
            
            # Calculate daily changes
            daily_changes = []
            for i in range(1, len(hist)):
                prev_close = hist['Close'].iloc[i-1]
                current_close = hist['Close'].iloc[i]
                change = current_close - prev_close
                change_percent = (change / prev_close) * 100
                
                daily_changes.append({
                    'date': hist.index[i].strftime('%Y-%m-%d'),
                    'close': current_close,
                    'change': change,
                    'change_percent': change_percent
                })
            
            # Create market summary
            market_summary = {
                'market': market,
                'index_name': info.get('shortName', info.get('longName', f"{market} Index")),
                'current_value': info.get('regularMarketPrice', None),
                'change': info.get('regularMarketChange', None),
                'change_percent': info.get('regularMarketChangePercent', None),
                'daily_changes': daily_changes,
                'timestamp': datetime.now().isoformat()
            }
            
            return market_summary
            
        except Exception as e:
            logger.error(f"Error fetching market summary for {market}: {str(e)}")
            raise

    def get_stock_insights(self, symbol, market='NASDAQ'):
        """
        Get stock insights and technical indicators
        
        Args:
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            dict: Stock insights data
        """
        try:
            # Convert to Yahoo Finance ticker format
            ticker = self._get_yahoo_ticker(symbol, market)
            
            # Use Yahoo Finance API directly
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            client = ApiClient()
            
            # Get stock insights
            insights = client.call_api('YahooFinance/get_stock_insights', query={'symbol': ticker})
            
            # Process and return insights
            if insights and 'finance' in insights and 'result' in insights['finance']:
                return insights['finance']['result']
            else:
                raise ValueError(f"No insights data available for {symbol} ({market})")
                
        except Exception as e:
            logger.error(f"Error fetching stock insights for {symbol} ({market}): {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    fetcher = StockDataFetcher()
    
    # Test NASDAQ stock
    nasdaq_data = fetcher.get_real_time_data("AAPL", "NASDAQ")
    print(json.dumps(nasdaq_data, indent=2))
    
    # Test BSE stock
    try:
        bse_data = fetcher.get_real_time_data("RELIANCE", "BSE")
        print(json.dumps(bse_data, indent=2))
    except Exception as e:
        print(f"BSE test failed: {str(e)}")
