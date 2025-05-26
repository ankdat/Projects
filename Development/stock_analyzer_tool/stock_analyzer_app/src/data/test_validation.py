"""
Validation Test Script for Stock Analyzer Tool
Tests all major components: data fetching, pattern analysis, and portfolio functionality
"""

import sys
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from data.stock_data import StockDataFetcher
from data.pattern_analysis import PatternAnalyzer
from data.portfolio_analysis import PortfolioAnalyzer

def test_stock_data_fetcher():
    """Test the StockDataFetcher module"""
    print("\n=== Testing Stock Data Fetcher ===")
    
    try:
        # Create fetcher
        fetcher = StockDataFetcher()
        
        # Test NASDAQ stock real-time data
        print("\nTesting NASDAQ real-time data:")
        nasdaq_data = fetcher.get_real_time_data("AAPL", "NASDAQ")
        print(f"Symbol: {nasdaq_data['symbol']}")
        print(f"Name: {nasdaq_data['name']}")
        print(f"Current Price: {nasdaq_data['current_price']}")
        print(f"Change: {nasdaq_data['change']}")
        print(f"Change %: {nasdaq_data['change_percent']}")
        
        # Test BSE stock real-time data
        print("\nTesting BSE real-time data:")
        try:
            bse_data = fetcher.get_real_time_data("RELIANCE", "BSE")
            print(f"Symbol: {bse_data['symbol']}")
            print(f"Name: {bse_data['name']}")
            print(f"Current Price: {bse_data['current_price']}")
            print(f"Change: {bse_data['change']}")
            print(f"Change %: {bse_data['change_percent']}")
        except Exception as e:
            print(f"BSE test failed: {str(e)}")
        
        # Test historical data
        print("\nTesting historical data:")
        hist_data = fetcher.get_historical_data("AAPL", "NASDAQ", interval="1d", period="1mo")
        if isinstance(hist_data, pd.DataFrame):
            print(f"Historical data shape: {hist_data.shape}")
            print(f"Date range: {hist_data['Date'].min()} to {hist_data['Date'].max()}")
        else:
            print(f"Historical data entries: {len(hist_data)}")
        
        # Test market summary
        print("\nTesting market summary:")
        market_summary = fetcher.get_market_summary("NASDAQ")
        print(f"Market: {market_summary['market']}")
        print(f"Index: {market_summary['index_name']}")
        print(f"Current Value: {market_summary['current_value']}")
        print(f"Change: {market_summary['change']}")
        print(f"Change %: {market_summary['change_percent']}")
        
        print("\nStock Data Fetcher tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Stock Data Fetcher test failed: {str(e)}")
        return False

def test_pattern_analyzer():
    """Test the PatternAnalyzer module"""
    print("\n=== Testing Pattern Analyzer ===")
    
    try:
        # Create fetcher and analyzer
        fetcher = StockDataFetcher()
        analyzer = PatternAnalyzer()
        
        # Get historical data
        print("\nFetching historical data for analysis...")
        hist_data = fetcher.get_historical_data("AAPL", "NASDAQ", interval="1d", period="3mo")
        
        if not isinstance(hist_data, pd.DataFrame):
            hist_data = pd.DataFrame(hist_data)
        
        # Add technical indicators
        print("\nAdding technical indicators...")
        df_with_indicators = analyzer.add_technical_indicators(hist_data)
        print(f"Added indicators. New shape: {df_with_indicators.shape}")
        print(f"Indicators added: {[col for col in df_with_indicators.columns if col not in hist_data.columns][:5]}...")
        
        # Analyze patterns
        print("\nAnalyzing patterns...")
        df_analyzed = analyzer.analyze_patterns(df_with_indicators)
        print(f"Pattern columns added: {[col for col in df_analyzed.columns if col not in df_with_indicators.columns]}")
        
        # Generate signals
        print("\nGenerating signals...")
        signal = analyzer.generate_signals(df_analyzed, "AAPL", "NASDAQ")
        print(f"Signal type: {signal['signal_type']}")
        print(f"Signal strength: {signal['signal_strength']}%")
        print("Reasons:")
        for reason in signal['reasons']:
            print(f"- {reason}")
        
        # Complete analysis
        print("\nPerforming complete stock analysis...")
        analysis = analyzer.analyze_stock(hist_data, "AAPL", "NASDAQ")
        print(f"Analysis completed for {analysis['symbol']}")
        print(f"Signal: {analysis['signal']['signal_type']} ({analysis['signal']['signal_strength']}%)")
        print(f"Last price: {analysis['last_price']}")
        print(f"Price change: {analysis['price_change']} ({analysis['price_change_percent']:.2f}%)")
        
        print("\nPattern Analyzer tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Pattern Analyzer test failed: {str(e)}")
        return False

def test_portfolio_analyzer():
    """Test the PortfolioAnalyzer module"""
    print("\n=== Testing Portfolio Analyzer ===")
    
    try:
        # Create all components
        fetcher = StockDataFetcher()
        pattern_analyzer = PatternAnalyzer()
        portfolio_analyzer = PortfolioAnalyzer(fetcher, pattern_analyzer)
        
        # Create a test portfolio
        print("\nCreating test portfolio...")
        portfolio_analyzer.create_portfolio("test", "Test Portfolio", "Portfolio for testing")
        
        # Add holdings
        print("\nAdding holdings...")
        portfolio_analyzer.add_holding("test", "AAPL", "NASDAQ", 10, 150.0)
        portfolio_analyzer.add_holding("test", "MSFT", "NASDAQ", 5, 250.0)
        try:
            portfolio_analyzer.add_holding("test", "RELIANCE", "BSE", 20, 2500.0)
        except Exception as e:
            print(f"Note: Could not add BSE stock: {str(e)}")
        
        # Add cash
        print("\nAdding cash...")
        portfolio_analyzer.update_cash("test", 5000.0, "deposit", "Initial deposit")
        
        # Get portfolio
        print("\nRetrieving portfolio...")
        portfolio = portfolio_analyzer.get_portfolio("test")
        print(f"Portfolio: {portfolio['name']}")
        print(f"Cash: {portfolio['cash']}")
        print(f"Holdings: {len(portfolio['holdings'])}")
        
        # Analyze portfolio
        print("\nAnalyzing portfolio...")
        analysis = portfolio_analyzer.analyze_portfolio("test")
        print(f"Total value: {analysis['total_value']}")
        print(f"Total gain/loss: {analysis['total_gain_loss']} ({analysis['total_gain_loss_percent']:.2f}%)")
        print(f"Risk level: {analysis['risk_metrics'].get('risk_level', 'Unknown')}")
        print(f"Diversification score: {analysis['diversification'].get('diversification_score', 0):.2f}")
        
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"- [{rec['severity']}] {rec['message']}")
        
        # Export portfolio
        print("\nExporting portfolio...")
        exported = portfolio_analyzer.export_portfolio("test", "json")
        print(f"Exported portfolio (first 100 chars): {exported[:100]}...")
        
        print("\nPortfolio Analyzer tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Portfolio Analyzer test failed: {str(e)}")
        return False

def test_integration():
    """Test integration between all components"""
    print("\n=== Testing Integration Between Components ===")
    
    try:
        # Create all components
        fetcher = StockDataFetcher()
        pattern_analyzer = PatternAnalyzer()
        portfolio_analyzer = PortfolioAnalyzer(fetcher, pattern_analyzer)
        
        # Create a test portfolio
        portfolio_analyzer.create_portfolio("integration", "Integration Test Portfolio")
        
        # Add some holdings
        stocks = [
            ("AAPL", "NASDAQ", 10, 150.0),
            ("MSFT", "NASDAQ", 5, 250.0),
            ("GOOGL", "NASDAQ", 2, 2000.0)
        ]
        
        for symbol, market, quantity, price in stocks:
            portfolio_analyzer.add_holding("integration", symbol, market, quantity, price)
        
        # Analyze portfolio with real-time data and pattern analysis
        print("\nPerforming integrated portfolio analysis...")
        analysis = portfolio_analyzer.analyze_portfolio("integration")
        
        print(f"\nPortfolio value: {analysis['total_value']:.2f}")
        print(f"Gain/Loss: {analysis['total_gain_loss']:.2f} ({analysis['total_gain_loss_percent']:.2f}%)")
        
        print("\nHoldings analysis:")
        for holding in analysis['holdings_analysis']:
            print(f"\n{holding['symbol']} ({holding['market']}):")
            print(f"  Quantity: {holding['quantity']}")
            print(f"  Current price: {holding.get('current_price', 'N/A')}")
            print(f"  Gain/Loss: {holding.get('gain_loss', 'N/A')} ({holding.get('gain_loss_percent', 'N/A'):.2f}%)")
            
            if 'signal' in holding and holding['signal']:
                signal = holding['signal']
                print(f"  Signal: {signal['signal_type']} ({signal['signal_strength']}%)")
                if signal['reasons']:
                    print(f"  Signal reasons: {signal['reasons'][0]}")
        
        print("\nIntegration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=== Starting Validation Tests ===")
    print(f"Date/Time: {datetime.now().isoformat()}")
    
    results = {
        "stock_data_fetcher": test_stock_data_fetcher(),
        "pattern_analyzer": test_pattern_analyzer(),
        "portfolio_analyzer": test_portfolio_analyzer(),
        "integration": test_integration()
    }
    
    print("\n=== Validation Test Results ===")
    for test, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall validation: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
