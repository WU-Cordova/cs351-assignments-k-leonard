from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List
from datastructures.avltree import AVLNode, AVLTree
import csv

@dataclass
class StockNode:
    stock_symbol: str
    stock_name: str
    price: float
    max_price: float = 0
    low : float = 0
    height: int = 1
    historical_prices: List[float] = None  # For storing historical prices
    size: int = 1  # For percentile calculations
    left: Optional[StockNode] = None
    right: Optional[StockNode] = None

    def __init__(self, stock_symbol: str, stock_name: str, price: float, low: float):
        self.stock_symbol = stock_symbol
        self.stock_name = stock_name
        self.price = price
        self.max_price = price
        self.low = low
        self.historical_prices = [price]  # Initialize historical prices with the current price

#@dataclass(order=True)

# class Stock:
#     symbol: str
#     name: str
#     low: int
#     high: int

class StockPriceManager:
    def __init__(self):
        self._tree = AVLTree()
        self.correlation_map = {}  # For market basket analysis

    def insert(self, stock_symbol: str, stock_name: str, price: float, low: float):
        node: StockNode = self._tree.search(stock_symbol)

        if node:
            # Update existing stock price and historical prices
            node.historical_prices.append(price)  # Store new price in history
            node.price = price
            node.max_price = max(node.max_price, price)
        else:
            # Insert a new stock
            new_node = StockNode(stock_symbol=stock_symbol, stock_name=stock_name, price=price, low= low)
            self._tree.insert(stock_symbol, new_node)

        self._update_max_price(self._tree._root)

    def _update_max_price(self, node: Optional[StockNode]):
        left_max = 0
        if not node:
            return 0
        if node._left is not None: 
            left_max = self._update_max_price(node._left)
        right_max = self._update_max_price(node._right)
        max_price = max(node._value.price, left_max, right_max)

        node.max_price = max_price
        return node.max_price

    def lookup(self, stock_symbol: str) -> Optional[float]:
        node: StockNode = self._tree.search(stock_symbol)
        if node:
            return node.price
        return None  # Stock not found

    def range_query(self, low: float, high: float) -> List[Tuple[str, float]]:
        results = []
        self._range_query_helper(self._tree._root, low, high, results)
        return results

    def _range_query_helper(self, node: Optional[StockNode], low: float, high: float, results: list):
        if not node:
            return

        if node._value.price >= low:
            self._range_query_helper(node._left, low, high, results)

        if low <= node._value.price <= high:
            results.append((node.stock_symbol, node.price))

        if node._value.price <= high:
            self._range_query_helper(node._right, low, high, results)

    def check_alerts(self) -> List[str]:
        alerts = []
        for stock in self._get_all_stocks(self._tree._root):
            if stock._value.price < 120:  # Example threshold for alert
                alerts.append(f"Alert: {stock.stock_name}'s price has dropped below $120!")
        return alerts

    def _get_all_stocks(self, node: Optional[StockNode]) -> List[StockNode]:
        if not node:
            return []
        return (self._get_all_stocks(node._left) +
                [node] +
                self._get_all_stocks(node._right))

    def find_percentile(self, percentile: float) -> Optional[Tuple[str, float]]:
        target_index = int(percentile / 100 * self._tree._root._value.size)  # Convert to index
        return self._find_percentile_helper(self._tree._root, target_index)

    def _find_percentile_helper(self, node: Optional[StockNode], index: int) -> Optional[Tuple[str, float]]:
        if not node:
            return None
        
        left_size = node._left._value.size if node._left else 0

        if index < left_size:
            return self._find_percentile_helper(node._left, index)
        elif index > left_size:
            return self._find_percentile_helper(node.right, index - left_size - 1)
        else:
            return (node._value.stock_symbol, node._value.price)  # Found the node at the index

    def calculate_moving_average(self, stock_symbol: str, period: int) -> Optional[float]:
        node: StockNode = self._tree.search(stock_symbol)
        if node and len(node.historical_prices) >= period:
            return sum(node.historical_prices[-period:]) / period
        return None  # Not enough data for moving average

    def track_correlation(self, stock_symbol: str, correlated_stock_symbol: str):
        if stock_symbol not in self.correlation_map:
            self.correlation_map[stock_symbol] = []
        self.correlation_map[stock_symbol].append(correlated_stock_symbol)

    def find_correlated_stocks(self, stock_symbol: str) -> List[str]:
        return self.correlation_map.get(stock_symbol, [])

    def add_stock(self, stock: Stock):
        # Add stock to the interval tree
        print("stock.low is {}, stock: {}".format(stock.low, stock))

        self._tree.insert(stock.low,stock)

        self._tree.insert(stock.high, stock) #, stock
        # Add stock to AVL tree for sorted access
        #self._stocks.insert(stock)  # Assuming AVLTree has an insert method

    def load_from_csv(self, filepath):
        with open(filepath, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                symbol, name, low, high = row[0], row[1], int(row[2]), int(row[3])
                stock = StockNode(symbol,name, low, high)
                print(stock)
                self.add_stock(stock)

    def lookup_stock_price(self, symbol: str) -> Stock:
        for stock in self._stocks.inorder():  # Assuming inorder() returns sorted stocks
            if stock.symbol == symbol:
                return stock
        return None

    def get_top_k_stocks(self, k: int):
        return self._stocks.get_top_k(k)  # Assuming get_top_k returns top k stocks based on high price

    def get_bottom_k_stocks(self, k: int):
        return self._stocks.get_bottom_k(k)  # Assuming get_bottom_k returns bottom k stocks based on low price

    def get_stocks_in_price_range(self, low: int, high: int):
        return self._interval_tree.range_query(low, high)

    def display_all_stocks(self):
        stocks = self._stocks.inorder()
        for stock in stocks:
            print(f"{stock.symbol} - {stock.name} - {stock.low}-{stock.high}")


# Example usage:
if __name__ == "__main__":
    manager = StockPriceManager()
    manager.insert("AAPL", "Apple Inc.", 150.0, 0)
    manager.insert("GOOGL", "Alphabet Inc.", 2800.0, 0)
    manager.insert("AMZN", "Amazon.com Inc.", 3400.0, 0)

    print("Current price of AAPL:", manager.lookup("AAPL"))
    print("Stocks in price range 1000 to 2000:", manager.range_query(1000, 2000))
    
    # Check alerts
    print("Alerts:", manager.check_alerts())
    
    # Find 50th percentile stock
    print("Finding 50th percentile stock:", manager.find_percentile(50))
    
    # Moving average
    manager.insert("AAPL", "Apple Inc.", 145.0, 0)
    manager.insert("AAPL", "Apple Inc.", 155.0, 0)
    print("AAPL moving average (last 3 prices):", manager.calculate_moving_average("AAPL", 3))
    
    # Correlation tracking
    manager.track_correlation("AAPL", "GOOGL")
    print("Correlated stocks with AAPL:", manager.find_correlated_stocks("AAPL"))

    manager.load_from_csv('./stocks/sample_stock_prices.csv')  # Load stocks from CSV

    # Display all stocks
    print("All Stocks:")
    stock_manager.display_all_stocks()

    # Lookup stock price
    symbol_to_lookup = 'AAPL'
    stock = stock_manager.lookup_stock_price(symbol_to_lookup)
    if stock:
        print(f"\nStock Price Lookup for {symbol_to_lookup}: {stock.low}-{stock.high}")
    else:
        print(f"\nStock {symbol_to_lookup} not found.")

    # Get top-K stocks
    top_k = stock_manager.get_top_k_stocks(5)
    print("\nTop-K Stocks:")
    for stock in top_k:
        print(f"{stock.symbol} - {stock.name} - {stock.low}-{stock.high}")

    # Get bottom-K stocks
    bottom_k = stock_manager.get_bottom_k_stocks(5)
    print("\nBottom-K Stocks:")
    for stock in bottom_k:
        print(f"{stock.symbol} - {stock.name} - {stock.low}-{stock.high}")

    # Get stocks in price range
    low_price, high_price = 100, 200
    stocks_in_range = stock_manager.get_stocks_in_price_range(low_price, high_price)
    print(f"\nStocks in price range {low_price}-{high_price}:")
    for stock in stocks_in_range:
        print(f"{stock.symbol} - {stock.name} - {stock.low}-{stock.high}")
 