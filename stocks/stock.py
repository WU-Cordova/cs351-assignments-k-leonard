""" from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List
from avltree import AVLNode, AVLTree


@dataclass
class StockNode:
    stock_symbol: str
    stock_name: str
    price: float
    max_price: float = 0
    height: int = 1
    historical_prices: List[float] = None  # For storing historical prices
    size: int = 1  # For percentile calculations
    left: Optional[StockNode] = None
    right: Optional[StockNode] = None

    def __init__(self, stock_symbol: str, stock_name: str, price: float):
        self.stock_symbol = stock_symbol
        self.stock_name = stock_name
        self.price = price
        self.max_price = price
        self.historical_prices = [price]  # Initialize historical prices with the current price


class StockPriceManager:
    def __init__(self):
        self._tree = AVLTree()
        self.correlation_map = {}  # For market basket analysis

    def insert(self, stock_symbol: str, stock_name: str, price: float):
        node: StockNode = self._tree.search(stock_symbol)

        if node:
            # Update existing stock price and historical prices
            node.historical_prices.append(price)  # Store new price in history
            node.price = price
            node.max_price = max(node.max_price, price)
        else:
            # Insert a new stock
            new_node = StockNode(stock_symbol=stock_symbol, stock_name=stock_name, price=price)
            self._tree.insert(stock_symbol, new_node)

        self._update_max_price(self._tree._root)

    def _update_max_price(self, node: Optional[StockNode]):
        if not node:
            return 0

        left_max = self._update_max_price(node.left)
        right_max = self._update_max_price(node.right)
        max_price = max(node.price, left_max, right_max)

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

        if node.price >= low:
            self._range_query_helper(node.left, low, high, results)

        if low <= node.price <= high:
            results.append((node.stock_symbol, node.price))

        if node.price <= high:
            self._range_query_helper(node.right, low, high, results)

    def check_alerts(self) -> List[str]:
        alerts = []
        for stock in self._get_all_stocks(self._tree._root):
            if stock.price < 120:  # Example threshold for alert
                alerts.append(f"Alert: {stock.stock_name}'s price has dropped below $120!")
        return alerts

    def _get_all_stocks(self, node: Optional[StockNode]) -> List[StockNode]:
        if not node:
            return []
        return (self._get_all_stocks(node.left) +
                [node] +
                self._get_all_stocks(node.right))

    def find_percentile(self, percentile: float) -> Optional[Tuple[str, float]]:
        target_index = int(percentile / 100 * self._tree._root.size)  # Convert to index
        return self._find_percentile_helper(self._tree._root, target_index)

    def _find_percentile_helper(self, node: Optional[StockNode], index: int) -> Optional[Tuple[str, float]]:
        if not node:
            return None
        
        left_size = node.left.size if node.left else 0

        if index < left_size:
            return self._find_percentile_helper(node.left, index)
        elif index > left_size:
            return self._find_percentile_helper(node.right, index - left_size - 1)
        else:
            return (node.stock_symbol, node.price)  # Found the node at the index

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


# Example usage:
if __name__ == "__main__":
    manager = StockPriceManager()
    manager.insert("AAPL", "Apple Inc.", 150.0)
    manager.insert("GOOGL", "Alphabet Inc.", 2800.0)
    manager.insert("AMZN", "Amazon.com Inc.", 3400.0)

    print("Current price of AAPL:", manager.lookup("AAPL"))
    print("Stocks in price range 1000 to 2000:", manager.range_query(1000, 2000))
    
    # Check alerts
    print("Alerts:", manager.check_alerts())
    
    # Find 50th percentile stock
    print("Finding 50th percentile stock:", manager.find_percentile(50))
    
    # Moving average
    manager.insert("AAPL", "Apple Inc.", 145.0)
    manager.insert("AAPL", "Apple Inc.", 155.0)
    print("AAPL moving average (last 3 prices):", manager.calculate_moving_average("AAPL", 3))
    
    # Correlation tracking
    manager.track_correlation("AAPL", "GOOGL")
    print("Correlated stocks with AAPL:", manager.find_correlated_stocks("AAPL"))
 """

from dataclasses import dataclass
from typing import List, Optional
from datastructures.intervaltree import IntervalTree
#from datastructures.avltree import AVLTree

@dataclass(order=True)
class Stock:
    symbol: str
    name: str
    low: int
    high: int
    current_price: float

class StockManager:
    def __init__(self):
        self._interval_tree = IntervalTree()
        self._price_history = {}

    def add_stock(self, stock: Stock):
        self._interval_tree.insert(stock.low, stock.high, stock)

    def update_stock(self, symbol: str, new_low: int, new_high: int):
        stock = self.find_stock_by_symbol(symbol)
        if stock:
            self._interval_tree.delete(stock.low, stock.high)
            stock.low = new_low
            stock.high = new_high
            self._interval_tree.insert(new_low, new_high, stock)

    def delete_stock(self, symbol: str):
        stock = self.find_stock_by_symbol(symbol)
        if stock:
            self._interval_tree.delete(stock.low, stock.high)

    def lookup_stock_price(self, symbol: str) -> Optional[float]:
        stock = self.find_stock_by_symbol(symbol)
        return stock.current_price if stock else None

    # def get_top_k_stocks(self, k: int) -> List[Stock]:
    #     stocks = self._interval_tree.inorder()
    #     return sorted(stocks, key=lambda x: x.value.high, reverse=True)[:k]

    def get_top_k_stocks(self, k: int):
        stock_keys = self._interval_tree.inorder()  # This gets the interval tree keys (low values)
        
        stocks = []
        for key in stock_keys:
            stock_node = self._interval_tree._tree.search(key)  # Search for the IntervalNode using the key
            if stock_node:
                stocks.append(stock_node.value)  # Append the Stock object from the IntervalNode's value

        # Sort the stocks by their high value and return the top k stocks
        return sorted(stocks, key=lambda stock: stock.high, reverse=True)[:k]


    def get_bottom_k_stocks(self, k: int) -> List[Stock]:
        stocks = self._interval_tree.inorder()
        return sorted(stocks, key=lambda x: x.value.low)[:k]

    def get_stocks_in_price_range(self, low: int, high: int) -> List[Stock]:
        return self._interval_tree.range_query(low, high)

    def track_price(self, symbol: str, price: float):
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        self._price_history[symbol].append(price)

    def generate_alert(self, symbol: str, threshold: float):
        stock = self.find_stock_by_symbol(symbol)
        if stock and stock.current_price >= threshold:
            print(f"Alert: {stock.symbol} has crossed the price threshold of {threshold}.")

    # def find_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
    #     stocks = self._interval_tree.inorder()
    #     for stock in stocks:
    #         if stock.value.symbol == symbol:
    #             return stock.value
    #     return None
    
    def find_stock_by_symbol(self, symbol: str):
        stock_keys = self._interval_tree.inorder()  # Get the keys (price intervals)

        for key in stock_keys:
            stock_node = self._interval_tree._tree.search(key)  # Get the IntervalNode object
            if stock_node and stock_node.value.symbol == symbol:
                return stock_node.value  # Return the Stock object
        return None


def main():
    stock_manager = StockManager()
    stock_manager.add_stock(Stock('AAPL', 'Apple Inc.', 120, 150, 135))
    stock_manager.add_stock(Stock('GOOGL', 'Alphabet Inc.', 173, 213, 190))

    print(stock_manager.lookup_stock_price('AAPL'))  # Output: 135

    stock_manager.update_stock('AAPL', 130, 160)
    print(stock_manager.lookup_stock_price('AAPL'))  # Updated price

    top_stock = stock_manager.get_top_k_stocks(1)
    print(f"Top Stock: {top_stock}")

    stocks_in_range = stock_manager.get_stocks_in_price_range(100, 200)
    print(f"Stocks in Range: {stocks_in_range}")

    stock_manager.track_price('GOOGL', 215)
    stock_manager.generate_alert('GOOGL', 210)

if __name__ == "__main__":
    main()