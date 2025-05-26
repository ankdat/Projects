"""
Stock Pattern Analysis Module
Provides functionality to analyze stock patterns and generate buy/sell signals
"""

import pandas as pd
import numpy as np
import ta
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """
    Class to analyze stock patterns and generate buy/sell signals
    """
    
    def __init__(self):
        """Initialize the PatternAnalyzer"""
        self.signal_history = {}  # Track signal history for each stock
    
    def add_technical_indicators(self, df):
        """
        Add technical indicators to the dataframe
        
        Args:
            df (pandas.DataFrame): Historical stock data with OHLCV columns
            
        Returns:
            pandas.DataFrame: DataFrame with added technical indicators
        """
        try:
            # Make a copy to avoid modifying the original
            df_with_indicators = df.copy()
            
            # Add Moving Averages
            df_with_indicators['SMA_20'] = ta.trend.sma_indicator(df_with_indicators['Close'], window=20)
            df_with_indicators['SMA_50'] = ta.trend.sma_indicator(df_with_indicators['Close'], window=50)
            df_with_indicators['SMA_200'] = ta.trend.sma_indicator(df_with_indicators['Close'], window=200)
            df_with_indicators['EMA_12'] = ta.trend.ema_indicator(df_with_indicators['Close'], window=12)
            df_with_indicators['EMA_26'] = ta.trend.ema_indicator(df_with_indicators['Close'], window=26)
            
            # Add MACD
            macd = ta.trend.MACD(df_with_indicators['Close'])
            df_with_indicators['MACD_line'] = macd.macd()
            df_with_indicators['MACD_signal'] = macd.macd_signal()
            df_with_indicators['MACD_histogram'] = macd.macd_diff()
            
            # Add RSI
            df_with_indicators['RSI'] = ta.momentum.rsi(df_with_indicators['Close'], window=14)
            
            # Add Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df_with_indicators['Close'])
            df_with_indicators['BB_high'] = bollinger.bollinger_hband()
            df_with_indicators['BB_low'] = bollinger.bollinger_lband()
            df_with_indicators['BB_mid'] = bollinger.bollinger_mavg()
            df_with_indicators['BB_width'] = bollinger.bollinger_wband()
            
            # Add Volume indicators
            df_with_indicators['Volume_SMA_20'] = ta.trend.sma_indicator(df_with_indicators['Volume'], window=20)
            df_with_indicators['OBV'] = ta.volume.on_balance_volume(df_with_indicators['Close'], df_with_indicators['Volume'])
            
            # Add ATR for volatility
            df_with_indicators['ATR'] = ta.volatility.average_true_range(
                df_with_indicators['High'], 
                df_with_indicators['Low'], 
                df_with_indicators['Close']
            )
            
            # Add Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(
                df_with_indicators['High'], 
                df_with_indicators['Low'], 
                df_with_indicators['Close']
            )
            df_with_indicators['Stoch_k'] = stoch.stoch()
            df_with_indicators['Stoch_d'] = stoch.stoch_signal()
            
            return df_with_indicators
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {str(e)}")
            raise
    
    def analyze_patterns(self, df_with_indicators):
        """
        Analyze patterns in the data
        
        Args:
            df_with_indicators (pandas.DataFrame): DataFrame with technical indicators
            
        Returns:
            pandas.DataFrame: DataFrame with pattern analysis columns
        """
        try:
            # Make a copy to avoid modifying the original
            df_analyzed = df_with_indicators.copy()
            
            # Identify trend based on SMA relationships
            df_analyzed['Trend'] = 'Neutral'
            # Uptrend: SMA20 > SMA50 > SMA200
            df_analyzed.loc[(df_analyzed['SMA_20'] > df_analyzed['SMA_50']) & 
                           (df_analyzed['SMA_50'] > df_analyzed['SMA_200']), 'Trend'] = 'Uptrend'
            # Downtrend: SMA20 < SMA50 < SMA200
            df_analyzed.loc[(df_analyzed['SMA_20'] < df_analyzed['SMA_50']) & 
                           (df_analyzed['SMA_50'] < df_analyzed['SMA_200']), 'Trend'] = 'Downtrend'
            
            # Identify support and resistance levels
            # For simplicity, using Bollinger Bands as dynamic support/resistance
            df_analyzed['Support'] = df_analyzed['BB_low']
            df_analyzed['Resistance'] = df_analyzed['BB_high']
            
            # Identify MACD crossovers
            df_analyzed['MACD_Crossover'] = 'None'
            df_analyzed.loc[(df_analyzed['MACD_line'] > df_analyzed['MACD_signal']) & 
                           (df_analyzed['MACD_line'].shift(1) <= df_analyzed['MACD_signal'].shift(1)), 
                           'MACD_Crossover'] = 'Bullish'
            df_analyzed.loc[(df_analyzed['MACD_line'] < df_analyzed['MACD_signal']) & 
                           (df_analyzed['MACD_line'].shift(1) >= df_analyzed['MACD_signal'].shift(1)), 
                           'MACD_Crossover'] = 'Bearish'
            
            # Identify RSI conditions
            df_analyzed['RSI_Condition'] = 'Neutral'
            df_analyzed.loc[df_analyzed['RSI'] < 30, 'RSI_Condition'] = 'Oversold'
            df_analyzed.loc[df_analyzed['RSI'] > 70, 'RSI_Condition'] = 'Overbought'
            
            # Identify volume confirmation
            df_analyzed['Volume_Confirmation'] = 'Normal'
            df_analyzed.loc[df_analyzed['Volume'] > df_analyzed['Volume_SMA_20'] * 1.5, 'Volume_Confirmation'] = 'High'
            df_analyzed.loc[df_analyzed['Volume'] < df_analyzed['Volume_SMA_20'] * 0.5, 'Volume_Confirmation'] = 'Low'
            
            # Identify price breakouts
            df_analyzed['Price_Breakout'] = 'None'
            df_analyzed.loc[df_analyzed['Close'] > df_analyzed['BB_high'], 'Price_Breakout'] = 'Upward'
            df_analyzed.loc[df_analyzed['Close'] < df_analyzed['BB_low'], 'Price_Breakout'] = 'Downward'
            
            # Identify Moving Average Crossovers
            df_analyzed['MA_Crossover'] = 'None'
            # Golden Cross: SMA50 crosses above SMA200
            df_analyzed.loc[(df_analyzed['SMA_50'] > df_analyzed['SMA_200']) & 
                           (df_analyzed['SMA_50'].shift(1) <= df_analyzed['SMA_200'].shift(1)), 
                           'MA_Crossover'] = 'Golden Cross'
            # Death Cross: SMA50 crosses below SMA200
            df_analyzed.loc[(df_analyzed['SMA_50'] < df_analyzed['SMA_200']) & 
                           (df_analyzed['SMA_50'].shift(1) >= df_analyzed['SMA_200'].shift(1)), 
                           'MA_Crossover'] = 'Death Cross'
            
            return df_analyzed
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            raise
    
    def generate_signals(self, df_analyzed, symbol, market):
        """
        Generate buy/sell signals based on pattern analysis
        
        Args:
            df_analyzed (pandas.DataFrame): DataFrame with pattern analysis
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            dict: Signal information
        """
        try:
            # Get the latest data point (most recent)
            latest = df_analyzed.iloc[-1]
            
            # Initialize signal strength scores
            buy_score = 0
            sell_score = 0
            
            # Factor 1: Trend
            if latest['Trend'] == 'Uptrend':
                buy_score += 2
            elif latest['Trend'] == 'Downtrend':
                sell_score += 2
            
            # Factor 2: MACD Crossover
            if latest['MACD_Crossover'] == 'Bullish':
                buy_score += 3
            elif latest['MACD_Crossover'] == 'Bearish':
                sell_score += 3
            
            # Factor 3: RSI Condition
            if latest['RSI_Condition'] == 'Oversold':
                buy_score += 3
            elif latest['RSI_Condition'] == 'Overbought':
                sell_score += 3
            
            # Factor 4: Volume Confirmation
            if latest['Volume_Confirmation'] == 'High':
                if latest['Close'] > latest['Close'].shift(1):
                    buy_score += 1
                else:
                    sell_score += 1
            
            # Factor 5: Price Breakout
            if latest['Price_Breakout'] == 'Upward':
                buy_score += 2
            elif latest['Price_Breakout'] == 'Downward':
                sell_score += 2
            
            # Factor 6: Moving Average Crossover
            if latest['MA_Crossover'] == 'Golden Cross':
                buy_score += 3
            elif latest['MA_Crossover'] == 'Death Cross':
                sell_score += 3
            
            # Determine signal type based on scores
            signal_type = 'Hold'
            if buy_score >= 6 and buy_score > sell_score:
                signal_type = 'Buy'
            elif sell_score >= 6 and sell_score > buy_score:
                signal_type = 'Sell'
            
            # Calculate signal strength (0-100%)
            max_possible_score = 14  # Sum of all positive factors
            if signal_type == 'Buy':
                signal_strength = min(100, int((buy_score / max_possible_score) * 100))
            elif signal_type == 'Sell':
                signal_strength = min(100, int((sell_score / max_possible_score) * 100))
            else:
                signal_strength = 0
            
            # Calculate profit/loss potential
            profit_loss_potential = 0
            if signal_type == 'Buy':
                # Estimate upside potential using ATR and trend
                profit_loss_potential = latest['Close'] * (1 + (latest['ATR'] * 3 / latest['Close']))
            elif signal_type == 'Sell':
                # Estimate downside risk using ATR and trend
                profit_loss_potential = latest['Close'] * (1 - (latest['ATR'] * 3 / latest['Close']))
            
            # Generate reasons for the signal
            reasons = []
            if signal_type == 'Buy':
                if latest['Trend'] == 'Uptrend':
                    reasons.append("Stock is in an uptrend (SMA20 > SMA50 > SMA200)")
                if latest['MACD_Crossover'] == 'Bullish':
                    reasons.append("Bullish MACD crossover detected")
                if latest['RSI_Condition'] == 'Oversold':
                    reasons.append("RSI indicates oversold conditions")
                if latest['Price_Breakout'] == 'Upward':
                    reasons.append("Price broke above upper Bollinger Band")
                if latest['MA_Crossover'] == 'Golden Cross':
                    reasons.append("Golden Cross detected (SMA50 crossed above SMA200)")
                if latest['Volume_Confirmation'] == 'High' and latest['Close'] > latest['Close'].shift(1):
                    reasons.append("Strong volume confirms upward movement")
            elif signal_type == 'Sell':
                if latest['Trend'] == 'Downtrend':
                    reasons.append("Stock is in a downtrend (SMA20 < SMA50 < SMA200)")
                if latest['MACD_Crossover'] == 'Bearish':
                    reasons.append("Bearish MACD crossover detected")
                if latest['RSI_Condition'] == 'Overbought':
                    reasons.append("RSI indicates overbought conditions")
                if latest['Price_Breakout'] == 'Downward':
                    reasons.append("Price broke below lower Bollinger Band")
                if latest['MA_Crossover'] == 'Death Cross':
                    reasons.append("Death Cross detected (SMA50 crossed below SMA200)")
                if latest['Volume_Confirmation'] == 'High' and latest['Close'] < latest['Close'].shift(1):
                    reasons.append("Strong volume confirms downward movement")
            
            # Create signal object
            signal = {
                'symbol': symbol,
                'market': market,
                'signal_type': signal_type,
                'signal_strength': signal_strength,
                'current_price': latest['Close'],
                'profit_loss_potential': profit_loss_potential,
                'timestamp': datetime.now().isoformat(),
                'reasons': reasons,
                'technical_indicators': {
                    'trend': latest['Trend'],
                    'rsi': latest['RSI'],
                    'macd_line': latest['MACD_line'],
                    'macd_signal': latest['MACD_signal'],
                    'macd_histogram': latest['MACD_histogram'],
                    'sma_20': latest['SMA_20'],
                    'sma_50': latest['SMA_50'],
                    'sma_200': latest['SMA_200'],
                }
            }
            
            # Store in signal history
            stock_key = f"{symbol}_{market}"
            if stock_key not in self.signal_history:
                self.signal_history[stock_key] = []
            
            self.signal_history[stock_key].append(signal)
            
            # Keep only the last 10 signals
            if len(self.signal_history[stock_key]) > 10:
                self.signal_history[stock_key] = self.signal_history[stock_key][-10:]
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol} ({market}): {str(e)}")
            raise
    
    def analyze_stock(self, historical_data, symbol, market):
        """
        Complete stock analysis pipeline
        
        Args:
            historical_data (pandas.DataFrame): Historical stock data
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            dict: Analysis results including signals
        """
        try:
            # Ensure DataFrame has required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in historical_data.columns for col in required_columns):
                raise ValueError(f"Historical data missing required columns. Required: {required_columns}")
            
            # Add technical indicators
            df_with_indicators = self.add_technical_indicators(historical_data)
            
            # Analyze patterns
            df_analyzed = self.analyze_patterns(df_with_indicators)
            
            # Generate signals
            signal = self.generate_signals(df_analyzed, symbol, market)
            
            # Create analysis result
            analysis_result = {
                'symbol': symbol,
                'market': market,
                'signal': signal,
                'last_price': historical_data['Close'].iloc[-1],
                'price_change': historical_data['Close'].iloc[-1] - historical_data['Close'].iloc[-2],
                'price_change_percent': ((historical_data['Close'].iloc[-1] - historical_data['Close'].iloc[-2]) / historical_data['Close'].iloc[-2]) * 100,
                'volume': historical_data['Volume'].iloc[-1],
                'timestamp': datetime.now().isoformat(),
                'analyzed_data': df_analyzed.tail(30).to_dict('records')  # Last 30 data points
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol} ({market}): {str(e)}")
            raise
    
    def get_signal_history(self, symbol, market):
        """
        Get signal history for a stock
        
        Args:
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            
        Returns:
            list: Signal history
        """
        stock_key = f"{symbol}_{market}"
        return self.signal_history.get(stock_key, [])

# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Create analyzer
    analyzer = PatternAnalyzer()
    
    # Get sample data
    ticker = yf.Ticker("AAPL")
    hist_data = ticker.history(period="1y")
    
    # Analyze stock
    analysis = analyzer.analyze_stock(hist_data, "AAPL", "NASDAQ")
    
    # Print signal
    print(f"Signal: {analysis['signal']['signal_type']}")
    print(f"Strength: {analysis['signal']['signal_strength']}%")
    print("Reasons:")
    for reason in analysis['signal']['reasons']:
        print(f"- {reason}")
