"""
Portfolio Analysis Module
Provides functionality to analyze stock portfolios and generate insights
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """
    Class to analyze stock portfolios and generate insights
    """
    
    def __init__(self, stock_data_fetcher=None, pattern_analyzer=None):
        """
        Initialize the PortfolioAnalyzer
        
        Args:
            stock_data_fetcher: Instance of StockDataFetcher for getting stock data
            pattern_analyzer: Instance of PatternAnalyzer for analyzing patterns
        """
        self.stock_data_fetcher = stock_data_fetcher
        self.pattern_analyzer = pattern_analyzer
        self.portfolios = {}  # Store user portfolios
    
    def create_portfolio(self, portfolio_id, name, description=None):
        """
        Create a new portfolio
        
        Args:
            portfolio_id (str): Unique identifier for the portfolio
            name (str): Portfolio name
            description (str, optional): Portfolio description
            
        Returns:
            dict: Created portfolio
        """
        try:
            if portfolio_id in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} already exists")
            
            portfolio = {
                'id': portfolio_id,
                'name': name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'holdings': [],
                'cash': 0.0,
                'transactions': []
            }
            
            self.portfolios[portfolio_id] = portfolio
            return portfolio
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    def add_holding(self, portfolio_id, symbol, market, quantity, purchase_price, purchase_date=None):
        """
        Add a holding to a portfolio
        
        Args:
            portfolio_id (str): Portfolio ID
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            quantity (float): Number of shares
            purchase_price (float): Price per share at purchase
            purchase_date (str, optional): Purchase date in ISO format
            
        Returns:
            dict: Updated portfolio
        """
        try:
            if portfolio_id not in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
            
            portfolio = self.portfolios[portfolio_id]
            
            # Check if holding already exists
            for holding in portfolio['holdings']:
                if holding['symbol'] == symbol and holding['market'] == market:
                    # Update existing holding (average down/up)
                    total_shares = holding['quantity'] + quantity
                    total_cost = (holding['quantity'] * holding['average_price']) + (quantity * purchase_price)
                    holding['average_price'] = total_cost / total_shares
                    holding['quantity'] = total_shares
                    holding['updated_at'] = datetime.now().isoformat()
                    
                    # Add transaction
                    transaction = {
                        'type': 'buy',
                        'symbol': symbol,
                        'market': market,
                        'quantity': quantity,
                        'price': purchase_price,
                        'date': purchase_date or datetime.now().isoformat(),
                        'total': quantity * purchase_price
                    }
                    portfolio['transactions'].append(transaction)
                    
                    portfolio['updated_at'] = datetime.now().isoformat()
                    return portfolio
            
            # Add new holding
            holding = {
                'symbol': symbol,
                'market': market,
                'quantity': quantity,
                'average_price': purchase_price,
                'purchase_date': purchase_date or datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            portfolio['holdings'].append(holding)
            
            # Add transaction
            transaction = {
                'type': 'buy',
                'symbol': symbol,
                'market': market,
                'quantity': quantity,
                'price': purchase_price,
                'date': purchase_date or datetime.now().isoformat(),
                'total': quantity * purchase_price
            }
            portfolio['transactions'].append(transaction)
            
            portfolio['updated_at'] = datetime.now().isoformat()
            return portfolio
            
        except Exception as e:
            logger.error(f"Error adding holding to portfolio: {str(e)}")
            raise
    
    def remove_holding(self, portfolio_id, symbol, market, quantity, sell_price, sell_date=None):
        """
        Remove a holding from a portfolio (sell)
        
        Args:
            portfolio_id (str): Portfolio ID
            symbol (str): Stock symbol
            market (str): Market (NASDAQ or BSE)
            quantity (float): Number of shares to sell
            sell_price (float): Price per share at sale
            sell_date (str, optional): Sale date in ISO format
            
        Returns:
            dict: Updated portfolio
        """
        try:
            if portfolio_id not in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
            
            portfolio = self.portfolios[portfolio_id]
            
            # Find the holding
            holding_index = None
            for i, holding in enumerate(portfolio['holdings']):
                if holding['symbol'] == symbol and holding['market'] == market:
                    holding_index = i
                    break
            
            if holding_index is None:
                raise ValueError(f"Holding {symbol} ({market}) not found in portfolio")
            
            holding = portfolio['holdings'][holding_index]
            
            if quantity > holding['quantity']:
                raise ValueError(f"Cannot sell {quantity} shares, only {holding['quantity']} available")
            
            # Calculate profit/loss
            profit_loss = (sell_price - holding['average_price']) * quantity
            
            # Update or remove holding
            if quantity < holding['quantity']:
                # Partial sell
                holding['quantity'] -= quantity
                holding['updated_at'] = datetime.now().isoformat()
            else:
                # Full sell
                portfolio['holdings'].pop(holding_index)
            
            # Add transaction
            transaction = {
                'type': 'sell',
                'symbol': symbol,
                'market': market,
                'quantity': quantity,
                'price': sell_price,
                'date': sell_date or datetime.now().isoformat(),
                'total': quantity * sell_price,
                'profit_loss': profit_loss
            }
            portfolio['transactions'].append(transaction)
            
            # Update cash balance
            portfolio['cash'] += quantity * sell_price
            
            portfolio['updated_at'] = datetime.now().isoformat()
            return portfolio
            
        except Exception as e:
            logger.error(f"Error removing holding from portfolio: {str(e)}")
            raise
    
    def update_cash(self, portfolio_id, amount, transaction_type, description=None):
        """
        Update cash balance in portfolio
        
        Args:
            portfolio_id (str): Portfolio ID
            amount (float): Amount to add/withdraw
            transaction_type (str): 'deposit' or 'withdraw'
            description (str, optional): Transaction description
            
        Returns:
            dict: Updated portfolio
        """
        try:
            if portfolio_id not in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
            
            portfolio = self.portfolios[portfolio_id]
            
            if transaction_type == 'withdraw' and amount > portfolio['cash']:
                raise ValueError(f"Cannot withdraw {amount}, only {portfolio['cash']} available")
            
            if transaction_type == 'deposit':
                portfolio['cash'] += amount
            elif transaction_type == 'withdraw':
                portfolio['cash'] -= amount
            else:
                raise ValueError(f"Invalid transaction type: {transaction_type}")
            
            # Add transaction
            transaction = {
                'type': transaction_type,
                'amount': amount,
                'date': datetime.now().isoformat(),
                'description': description
            }
            portfolio['transactions'].append(transaction)
            
            portfolio['updated_at'] = datetime.now().isoformat()
            return portfolio
            
        except Exception as e:
            logger.error(f"Error updating cash balance: {str(e)}")
            raise
    
    def get_portfolio(self, portfolio_id):
        """
        Get a portfolio by ID
        
        Args:
            portfolio_id (str): Portfolio ID
            
        Returns:
            dict: Portfolio
        """
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
        
        return self.portfolios[portfolio_id]
    
    def list_portfolios(self):
        """
        List all portfolios
        
        Returns:
            list: List of portfolios
        """
        return list(self.portfolios.values())
    
    def analyze_portfolio(self, portfolio_id):
        """
        Analyze a portfolio and generate insights
        
        Args:
            portfolio_id (str): Portfolio ID
            
        Returns:
            dict: Portfolio analysis
        """
        try:
            if portfolio_id not in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
            
            if not self.stock_data_fetcher:
                raise ValueError("Stock data fetcher not provided")
            
            portfolio = self.portfolios[portfolio_id]
            holdings = portfolio['holdings']
            
            # Initialize analysis result
            analysis = {
                'portfolio_id': portfolio_id,
                'portfolio_name': portfolio['name'],
                'analysis_date': datetime.now().isoformat(),
                'total_value': portfolio['cash'],
                'total_cost': 0,
                'total_gain_loss': 0,
                'total_gain_loss_percent': 0,
                'holdings_analysis': [],
                'risk_metrics': {},
                'diversification': {},
                'recommendations': []
            }
            
            # Analyze each holding
            for holding in holdings:
                symbol = holding['symbol']
                market = holding['market']
                quantity = holding['quantity']
                average_price = holding['average_price']
                
                try:
                    # Get current price
                    stock_data = self.stock_data_fetcher.get_real_time_data(symbol, market)
                    current_price = stock_data['current_price']
                    
                    # Calculate values
                    current_value = current_price * quantity
                    cost_basis = average_price * quantity
                    gain_loss = current_value - cost_basis
                    gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    # Get historical data for volatility calculation
                    hist_data = self.stock_data_fetcher.get_historical_data(symbol, market, interval='1d', period='1mo')
                    
                    # Calculate volatility (standard deviation of daily returns)
                    if isinstance(hist_data, pd.DataFrame) and len(hist_data) > 1:
                        hist_data['daily_return'] = hist_data['Close'].pct_change()
                        volatility = hist_data['daily_return'].std() * 100  # Convert to percentage
                    else:
                        volatility = 0
                    
                    # Get buy/sell signal if pattern analyzer is available
                    signal = None
                    if self.pattern_analyzer and isinstance(hist_data, pd.DataFrame) and len(hist_data) > 20:
                        analysis_result = self.pattern_analyzer.analyze_stock(hist_data, symbol, market)
                        signal = analysis_result['signal']
                    
                    # Add to holdings analysis
                    holding_analysis = {
                        'symbol': symbol,
                        'market': market,
                        'quantity': quantity,
                        'average_price': average_price,
                        'current_price': current_price,
                        'current_value': current_value,
                        'cost_basis': cost_basis,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_percent,
                        'volatility': volatility,
                        'signal': signal
                    }
                    
                    analysis['holdings_analysis'].append(holding_analysis)
                    
                    # Update totals
                    analysis['total_value'] += current_value
                    analysis['total_cost'] += cost_basis
                    analysis['total_gain_loss'] += gain_loss
                    
                except Exception as e:
                    logger.warning(f"Error analyzing holding {symbol} ({market}): {str(e)}")
                    # Add holding with limited data
                    holding_analysis = {
                        'symbol': symbol,
                        'market': market,
                        'quantity': quantity,
                        'average_price': average_price,
                        'cost_basis': average_price * quantity,
                        'error': str(e)
                    }
                    analysis['holdings_analysis'].append(holding_analysis)
                    analysis['total_cost'] += average_price * quantity
            
            # Calculate overall gain/loss percentage
            if analysis['total_cost'] > 0:
                analysis['total_gain_loss_percent'] = (analysis['total_gain_loss'] / analysis['total_cost']) * 100
            
            # Calculate risk metrics
            if len(analysis['holdings_analysis']) > 0:
                # Portfolio volatility (weighted average of individual volatilities)
                total_weight = sum(h['current_value'] for h in analysis['holdings_analysis'] if 'current_value' in h)
                if total_weight > 0:
                    weighted_volatility = sum(
                        (h['volatility'] * h['current_value'] / total_weight) 
                        for h in analysis['holdings_analysis'] 
                        if 'volatility' in h and 'current_value' in h
                    )
                else:
                    weighted_volatility = 0
                
                analysis['risk_metrics'] = {
                    'portfolio_volatility': weighted_volatility,
                    'risk_level': self._categorize_risk(weighted_volatility)
                }
            
            # Calculate diversification metrics
            market_allocation = {}
            symbol_allocation = {}
            
            for holding in analysis['holdings_analysis']:
                if 'current_value' not in holding:
                    continue
                
                # Market allocation
                market = holding['market']
                if market not in market_allocation:
                    market_allocation[market] = 0
                market_allocation[market] += holding['current_value']
                
                # Symbol allocation
                symbol = holding['symbol']
                symbol_allocation[symbol] = holding['current_value']
            
            # Convert to percentages
            total_value = analysis['total_value']
            if total_value > 0:
                market_allocation = {k: (v / total_value) * 100 for k, v in market_allocation.items()}
                symbol_allocation = {k: (v / total_value) * 100 for k, v in symbol_allocation.items()}
            
            analysis['diversification'] = {
                'market_allocation': market_allocation,
                'symbol_allocation': symbol_allocation,
                'diversification_score': self._calculate_diversification_score(symbol_allocation)
            }
            
            # Generate recommendations
            recommendations = []
            
            # Check for overconcentration
            for symbol, allocation in symbol_allocation.items():
                if allocation > 20:  # More than 20% in a single stock
                    recommendations.append({
                        'type': 'diversification',
                        'severity': 'warning',
                        'message': f"Overconcentration: {symbol} represents {allocation:.1f}% of your portfolio"
                    })
            
            # Check for buy/sell signals
            for holding in analysis['holdings_analysis']:
                if 'signal' not in holding or not holding['signal']:
                    continue
                
                signal = holding['signal']
                if signal['signal_type'] == 'Buy' and signal['signal_strength'] >= 70:
                    recommendations.append({
                        'type': 'buy',
                        'severity': 'opportunity',
                        'message': f"Strong buy signal for {holding['symbol']} with {signal['signal_strength']}% confidence",
                        'reasons': signal['reasons']
                    })
                elif signal['signal_type'] == 'Sell' and signal['signal_strength'] >= 70:
                    recommendations.append({
                        'type': 'sell',
                        'severity': 'warning',
                        'message': f"Strong sell signal for {holding['symbol']} with {signal['signal_strength']}% confidence",
                        'reasons': signal['reasons']
                    })
            
            # Check for poor performers
            for holding in analysis['holdings_analysis']:
                if 'gain_loss_percent' not in holding:
                    continue
                
                if holding['gain_loss_percent'] < -10:  # More than 10% loss
                    recommendations.append({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f"{holding['symbol']} is down {abs(holding['gain_loss_percent']):.1f}% from your purchase price"
                    })
            
            analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            raise
    
    def _categorize_risk(self, volatility):
        """
        Categorize risk level based on volatility
        
        Args:
            volatility (float): Portfolio volatility
            
        Returns:
            str: Risk level
        """
        if volatility < 10:
            return 'Low'
        elif volatility < 20:
            return 'Medium'
        else:
            return 'High'
    
    def _calculate_diversification_score(self, allocations):
        """
        Calculate diversification score (0-100)
        Higher is better diversified
        
        Args:
            allocations (dict): Symbol allocations
            
        Returns:
            float: Diversification score
        """
        if not allocations:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        # HHI is sum of squared percentages
        hhi = sum(allocation ** 2 for allocation in allocations.values())
        
        # Normalize to 0-100 scale (inverted so higher is better)
        # Perfect diversification would be 1/n for each holding
        # Worst diversification would be 100% in one holding (HHI = 10000)
        score = max(0, min(100, 100 - (hhi / 100)))
        
        return score
    
    def import_portfolio_from_broker(self, portfolio_id, broker_data):
        """
        Import portfolio data from a broker API
        
        Args:
            portfolio_id (str): Portfolio ID
            broker_data (dict): Broker API data
            
        Returns:
            dict: Updated portfolio
        """
        try:
            # Create portfolio if it doesn't exist
            if portfolio_id not in self.portfolios:
                self.create_portfolio(portfolio_id, f"Portfolio {portfolio_id}")
            
            portfolio = self.portfolios[portfolio_id]
            
            # Clear existing holdings
            portfolio['holdings'] = []
            
            # Process broker data
            # This is a simplified example - actual implementation would depend on broker API format
            if 'holdings' in broker_data:
                for holding_data in broker_data['holdings']:
                    symbol = holding_data.get('symbol')
                    market = holding_data.get('market', 'NASDAQ')  # Default to NASDAQ if not specified
                    quantity = holding_data.get('quantity', 0)
                    average_price = holding_data.get('average_price', 0)
                    purchase_date = holding_data.get('purchase_date')
                    
                    if symbol and quantity > 0:
                        self.add_holding(
                            portfolio_id, 
                            symbol, 
                            market, 
                            quantity, 
                            average_price, 
                            purchase_date
                        )
            
            # Update cash balance if provided
            if 'cash' in broker_data:
                portfolio['cash'] = broker_data['cash']
            
            portfolio['updated_at'] = datetime.now().isoformat()
            return portfolio
            
        except Exception as e:
            logger.error(f"Error importing portfolio from broker: {str(e)}")
            raise
    
    def export_portfolio(self, portfolio_id, format='json'):
        """
        Export portfolio data
        
        Args:
            portfolio_id (str): Portfolio ID
            format (str): Export format ('json' or 'csv')
            
        Returns:
            str: Exported portfolio data
        """
        try:
            if portfolio_id not in self.portfolios:
                raise ValueError(f"Portfolio with ID {portfolio_id} does not exist")
            
            portfolio = self.portfolios[portfolio_id]
            
            if format.lower() == 'json':
                return json.dumps(portfolio, indent=2)
            elif format.lower() == 'csv':
                # Create CSV for holdings
                holdings_df = pd.DataFrame(portfolio['holdings'])
                return holdings_df.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting portfolio: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create portfolio analyzer
    analyzer = PortfolioAnalyzer()
    
    # Create a portfolio
    analyzer.create_portfolio("demo", "Demo Portfolio")
    
    # Add holdings
    analyzer.add_holding("demo", "AAPL", "NASDAQ", 10, 150.0)
    analyzer.add_holding("demo", "MSFT", "NASDAQ", 5, 250.0)
    analyzer.add_holding("demo", "RELIANCE", "BSE", 20, 2500.0)
    
    # Update cash
    analyzer.update_cash("demo", 5000.0, "deposit", "Initial deposit")
    
    # Print portfolio
    portfolio = analyzer.get_portfolio("demo")
    print(json.dumps(portfolio, indent=2))
