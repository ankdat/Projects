# Stock Analyzer Tool - User Guide

## Overview

The Stock Analyzer Tool is a Python-based web application designed to help you make informed trading decisions by analyzing stock patterns, determining buy/sell signals, and managing your portfolio performance. The application focuses on day trading for NASDAQ and BSE markets.

## Features

1. **Real-time Stock Data Fetching**
   - Retrieves current stock prices and information from NASDAQ and BSE
   - Provides historical data for technical analysis
   - Includes market summaries and stock insights

2. **Pattern Analysis and Signal Generation**
   - Calculates technical indicators (Moving Averages, RSI, MACD, Bollinger Bands, etc.)
   - Identifies trends, support/resistance levels, and chart patterns
   - Generates buy/sell signals with confidence levels and reasoning
   - Predicts potential profit/loss based on pattern analysis

3. **Portfolio Management**
   - Tracks your stock holdings and performance
   - Analyzes portfolio diversification and risk metrics
   - Provides recommendations based on current holdings and market conditions
   - Supports importing portfolio data from broker APIs

## Installation and Setup

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository or extract the provided files
```bash
git clone <repository-url>
cd stock_analyzer_app
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python src/main.py
```

5. Access the web interface
Open your browser and navigate to: http://localhost:5000

## Usage Guide

### Analyzing Stocks

1. **Search for a Stock**
   - Enter the stock symbol in the search box
   - Select the market (NASDAQ or BSE)
   - Click "Search" to retrieve real-time data

2. **View Technical Analysis**
   - The main dashboard displays current price, change, and key metrics
   - Technical indicators are shown in charts with interpretations
   - Buy/sell signals are highlighted with confidence levels

3. **Understand Signal Reasoning**
   - Each buy/sell recommendation includes detailed reasoning
   - Technical factors contributing to the signal are explained
   - Potential profit/loss projections are provided

### Managing Your Portfolio

1. **Create a Portfolio**
   - Click "Create Portfolio" and provide a name
   - Add cash deposits as needed

2. **Add Holdings**
   - Search for stocks to add to your portfolio
   - Enter quantity and purchase price
   - Optionally specify purchase date

3. **Import from Broker**
   - Use the broker API integration to import your holdings
   - Follow the format specified in the documentation

4. **Analyze Portfolio Performance**
   - View total value, gain/loss, and performance metrics
   - Check diversification score and risk assessment
   - Review recommendations for portfolio optimization

### Setting Up Alerts

1. **Configure Alert Preferences**
   - Set minimum signal strength threshold
   - Choose notification methods
   - Specify stocks to monitor

2. **Receive Notifications**
   - Get alerts when buy/sell signals are triggered
   - Receive portfolio performance updates
   - Be notified of significant market movements

## API Reference

The application provides several internal APIs for data access:

### Stock Data API
- `GET /api/stock/{symbol}?market={market}` - Get real-time stock data
- `GET /api/stock/{symbol}/history?market={market}&interval={interval}&period={period}` - Get historical data
- `GET /api/market/{market}/summary` - Get market summary

### Analysis API
- `GET /api/analysis/{symbol}?market={market}` - Get complete stock analysis
- `GET /api/signals/{symbol}?market={market}` - Get buy/sell signals

### Portfolio API
- `GET /api/portfolio/{id}` - Get portfolio details
- `POST /api/portfolio` - Create new portfolio
- `PUT /api/portfolio/{id}/holdings` - Add/update holdings
- `GET /api/portfolio/{id}/analysis` - Get portfolio analysis

## Troubleshooting

### Common Issues

1. **Data Not Loading**
   - Check your internet connection
   - Verify the stock symbol is correct
   - Ensure the market is open during trading hours

2. **Incorrect Analysis**
   - Ensure you have sufficient historical data
   - Check for corporate actions that might affect analysis
   - Verify technical indicator settings

3. **Portfolio Import Failures**
   - Check the format of your broker data
   - Ensure all required fields are present
   - Verify API credentials if applicable

### Getting Help

For additional assistance, please refer to the detailed documentation in the `docs` directory or contact support.

## Future Enhancements

- Mobile application integration
- Automated trading capabilities
- Advanced machine learning models for prediction
- Social features for sharing insights
- Additional market integrations

## License

This software is provided for personal use only. All rights reserved.
