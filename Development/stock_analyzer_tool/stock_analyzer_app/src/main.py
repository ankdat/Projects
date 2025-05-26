"""
Main Flask application for Stock Analyzer Tool
Provides web interface for stock analysis and portfolio management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Import our custom modules
from src.data.stock_data import StockDataFetcher
from src.data.pattern_analysis import PatternAnalyzer
from src.data.portfolio_analysis import PortfolioAnalyzer

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'stock_analyzer_secret_key'

# Initialize our components
stock_data_fetcher = StockDataFetcher()
pattern_analyzer = PatternAnalyzer()
portfolio_analyzer = PortfolioAnalyzer(stock_data_fetcher, pattern_analyzer)

# Create a demo portfolio
try:
    portfolio_analyzer.create_portfolio("demo", "Demo Portfolio", "Sample portfolio for demonstration")
    portfolio_analyzer.add_holding("demo", "AAPL", "NASDAQ", 10, 150.0)
    portfolio_analyzer.add_holding("demo", "MSFT", "NASDAQ", 5, 250.0)
    portfolio_analyzer.add_holding("demo", "GOOGL", "NASDAQ", 2, 2000.0)
    portfolio_analyzer.update_cash("demo", 5000.0, "deposit", "Initial deposit")
except Exception as e:
    print(f"Error creating demo portfolio: {str(e)}")

# Routes
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html', title="Stock Analyzer Tool")

@app.route('/search')
def search():
    """Search for stocks"""
    query = request.args.get('query', '')
    market = request.args.get('market', 'NASDAQ')
    
    if not query:
        return render_template('search.html', results=[], query='')
    
    try:
        results = stock_data_fetcher.search_stocks(query, market)
        return render_template('search.html', results=results, query=query)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """Show stock details and analysis"""
    market = request.args.get('market', 'NASDAQ')
    
    try:
        # Get real-time data
        stock_data = stock_data_fetcher.get_real_time_data(symbol, market)
        
        # Get historical data
        hist_data = stock_data_fetcher.get_historical_data(symbol, market, interval="1d", period="3mo")
        if not isinstance(hist_data, pd.DataFrame):
            hist_data = pd.DataFrame(hist_data)
        
        # Analyze stock
        analysis = pattern_analyzer.analyze_stock(hist_data, symbol, market)
        
        return render_template(
            'stock_detail.html',
            stock=stock_data,
            analysis=analysis,
            symbol=symbol,
            market=market
        )
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/portfolio')
def portfolio_list():
    """List all portfolios"""
    try:
        portfolios = portfolio_analyzer.list_portfolios()
        return render_template('portfolio_list.html', portfolios=portfolios)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/portfolio/<portfolio_id>')
def portfolio_detail(portfolio_id):
    """Show portfolio details and analysis"""
    try:
        portfolio = portfolio_analyzer.get_portfolio(portfolio_id)
        analysis = portfolio_analyzer.analyze_portfolio(portfolio_id)
        return render_template(
            'portfolio_detail.html',
            portfolio=portfolio,
            analysis=analysis
        )
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/portfolio/create', methods=['GET', 'POST'])
def portfolio_create():
    """Create a new portfolio"""
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        name = request.form.get('name')
        description = request.form.get('description')
        
        try:
            portfolio_analyzer.create_portfolio(portfolio_id, name, description)
            return redirect(url_for('portfolio_detail', portfolio_id=portfolio_id))
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('portfolio_create.html')

@app.route('/portfolio/<portfolio_id>/add_holding', methods=['GET', 'POST'])
def add_holding(portfolio_id):
    """Add a holding to a portfolio"""
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        market = request.form.get('market')
        quantity = float(request.form.get('quantity'))
        purchase_price = float(request.form.get('purchase_price'))
        purchase_date = request.form.get('purchase_date')
        
        try:
            portfolio_analyzer.add_holding(
                portfolio_id, symbol, market, quantity, purchase_price, purchase_date
            )
            return redirect(url_for('portfolio_detail', portfolio_id=portfolio_id))
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template('add_holding.html', portfolio_id=portfolio_id)

# API Routes
@app.route('/api/stock/<symbol>')
def api_stock(symbol):
    """API endpoint for stock data"""
    market = request.args.get('market', 'NASDAQ')
    
    try:
        stock_data = stock_data_fetcher.get_real_time_data(symbol, market)
        return jsonify(stock_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/stock/<symbol>/history')
def api_stock_history(symbol):
    """API endpoint for historical stock data"""
    market = request.args.get('market', 'NASDAQ')
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1mo')
    
    try:
        hist_data = stock_data_fetcher.get_historical_data(symbol, market, interval, period)
        if isinstance(hist_data, pd.DataFrame):
            hist_data = hist_data.to_dict('records')
        return jsonify(hist_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analysis/<symbol>')
def api_analysis(symbol):
    """API endpoint for stock analysis"""
    market = request.args.get('market', 'NASDAQ')
    
    try:
        # Get historical data
        hist_data = stock_data_fetcher.get_historical_data(symbol, market, interval="1d", period="3mo")
        if not isinstance(hist_data, pd.DataFrame):
            hist_data = pd.DataFrame(hist_data)
        
        # Analyze stock
        analysis = pattern_analyzer.analyze_stock(hist_data, symbol, market)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/portfolio/<portfolio_id>')
def api_portfolio(portfolio_id):
    """API endpoint for portfolio data"""
    try:
        portfolio = portfolio_analyzer.get_portfolio(portfolio_id)
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/portfolio/<portfolio_id>/analysis')
def api_portfolio_analysis(portfolio_id):
    """API endpoint for portfolio analysis"""
    try:
        analysis = portfolio_analyzer.analyze_portfolio(portfolio_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('src/templates', exist_ok=True)
    
    # Create a basic index.html template if it doesn't exist
    index_path = os.path.join('src/templates', 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 20px; }
        .card { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Stock Analyzer Tool</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Search Stocks</h5>
                    </div>
                    <div class="card-body">
                        <form action="/search" method="get">
                            <div class="mb-3">
                                <label for="query" class="form-label">Stock Symbol or Name</label>
                                <input type="text" class="form-control" id="query" name="query" required>
                            </div>
                            <div class="mb-3">
                                <label for="market" class="form-label">Market</label>
                                <select class="form-select" id="market" name="market">
                                    <option value="NASDAQ">NASDAQ</option>
                                    <option value="BSE">BSE</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">Search</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Portfolios</h5>
                    </div>
                    <div class="card-body">
                        <p>Manage your stock portfolios and analyze performance.</p>
                        <a href="/portfolio" class="btn btn-primary">View Portfolios</a>
                        <a href="/portfolio/create" class="btn btn-outline-primary">Create New Portfolio</a>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>Demo Portfolio</h5>
                    </div>
                    <div class="card-body">
                        <p>Check out our demo portfolio with sample stocks.</p>
                        <a href="/portfolio/demo" class="btn btn-success">View Demo</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Market Summary</h5>
                    </div>
                    <div class="card-body">
                        <div id="market-summary">Loading market data...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Fetch market summary
        fetch('/api/market/NASDAQ/summary')
            .then(response => response.json())
            .then(data => {
                const summaryDiv = document.getElementById('market-summary');
                summaryDiv.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h4>${data.index_name}</h4>
                            <h3>${data.current_value.toFixed(2)} 
                                <span class="${data.change > 0 ? 'text-success' : 'text-danger'}">
                                    ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)} 
                                    (${data.change_percent.toFixed(2)}%)
                                </span>
                            </h3>
                        </div>
                        <div class="col-md-6">
                            <p>Last updated: ${new Date(data.timestamp).toLocaleString()}</p>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('market-summary').innerHTML = 
                    `<div class="alert alert-warning">Unable to load market data: ${error.message}</div>`;
            });
    </script>
</body>
</html>
            """)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
