from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List
from datastructures.avltree import AVLNode, AVLTree
import csv
#-------------------------------------
@dataclass
class StockNode: #the class of the node I am using
    stock_symbol: str #stock symbol is the abbreviation
    stock_name: str #Stock name is the company name 
    current_price: float #price is the current price of the stock
    max_price: float = 0 #the maximum price a stock has been
    low : float = 0 #the lowest price a stock has been
    height: int = 1 #height of the tree?
#    historical_prices: List[float] = None  # a list for later to hopefully implement historical prices
    size: int = 1  # size of the tree? (percentile calculations)
    left: Optional[StockNode] = None #left of the node
    right: Optional[StockNode] = None #right of the node

    def __init__(self, stock_symbol: str, stock_name: str, current_price: float, low_price: float): #initalizes the data class
        self.stock_symbol = stock_symbol # a stock will have  symbol (aka abbreveation) associated with it
        self.stock_name = stock_name #a stock will have a name (company name) associated with it
        self.current_price = current_price #a stock will have a current price assocaiated with it
        self.max_price = current_price#a stock will have a maximum price assocaited with it
        self.low_price = low_price #a stock will have a lowest price associated with it
        self.historical_prices = [current_price]  # Initialize historical prices with the current price

#@dataclass(order=True)

# class Stock:
#     symbol: str
#     name: str
#     low: int
#     high: int

class StockPriceManager: #creating a class to manage the stocks
    def __init__(self): #intializes the class 
        self._tree = AVLTree() #the class will have an AVL tree assocaited with it
        self.correlation_map = {}  # For market basket analysis
        self._stock_dictionary = {} #a dictionary to hold all of the stocks in a key value pair, where the key is the low price, and the value is the stock (like the whole node)

    def insert(self, stock_symbol: str, stock_name: str, current_price: float, low_price: float):
        node: StockNode = self._tree.search(low_price)

        if node:
            # Update existing stock price and historical prices
            node.historical_prices.append(current_price)  # Store new price in history
            node.current_price = current_price
            node.max_price = max(node.max_price, current_price)
            
        else:
            # Insert a new stock
            new_node = StockNode(stock_symbol=stock_symbol, stock_name=stock_name, current_price=current_price, low_price= low_price)
            self._tree.insert(low_price, new_node)
            self._stock_dictionary[low_price] = new_node

        self._update_max_price(self._tree._root)
        

    def _update_max_price(self, node: Optional[StockNode]):
        left_max = 0
        if not node:
            return 0
        if node._left is not None: 
            left_max = self._update_max_price(node._left)
        right_max = self._update_max_price(node._right)
        max_price = max(node._value.current_price, left_max, right_max)

        node.max_price = max_price
        return node.max_price

    def lookup(self, price: int) -> Optional[float]:
        node: StockNode = self._tree.search(price)
        if node:
            return node.price
        return None  # Stock not found

    def range_query(self, low_price: float, high: float) -> List[Tuple[str, float]]:
        results = []
        self._range_query_helper(self._tree._root, low_price, high, results)
        return results

    def _range_query_helper(self, node: Optional[StockNode], low_price: float, high: float, results: list):
        if not node:
            return

        if node._value.current_price >= low_price:
            self._range_query_helper(node._left, low_price, high, results)

        if low_price <= node._value.current_price <= high:
            results.append((node.stock_symbol, node.price))

        if node._value.current_price <= high:
            self._range_query_helper(node._right, low_price, high, results)

    def check_alerts(self) -> List[str]:
        alerts = []
        for stock in self._get_all_stocks(self._tree._root):
            if stock._value.current_price < 120:  # Example threshold for alert
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
            return (node._value.stock_symbol, node._value.current_price)  # Found the node at the index

    def calculate_moving_average(self, price: int, period: int) -> Optional[float]:
        node: StockNode = self._tree.search(price)
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

        self._tree.insert(stock.max_price, stock) #, stock
        
        #self._stocks.update(stock) 

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
        for stock in self._tree.inorder():  # Assuming inorder() returns sorted stocks
            if stock.stock_symbol == symbol:
                return stock
        return None

    def get_top_k(self, k: int):
#put this into a list, need to pull out the key (not the value) into a list, order by decending, return top 5
       list_of_stocks = list(self._stock_dictionary.keys()) #inorder() returns a list
       list_of_stocks.sort(reverse = True)

       return list_of_stocks[:k]

    def get_top_k_stocks(self, k: int) -> List[StockNode]:
        if not self._stock_dictionary:
            print("No stocks available.")
            return []
        
        # Retrieve top k from the _tree directly
        return self.get_top_k(k)  # Call the get_top_k method directly

       

    
    def get_bottom_k_stocks(self, k: int):
        return self._stocks.get_bottom_k(k)  

    def get_bottom_k(self, k: int):
        list_of_stocks = stocks._value ## put this into a list, need to pull out the key (not the value) into a list, order by decending, return top 5
        list_of_stocks.sort(key = lambda s: s.max_price)
        bottom_k = list_of_stocks[:k]
        return bottom_k

    def get_stocks_in_price_range(self, low: int, high: int):
        return self._interval_tree.range_query(low, high)

    def display_all_stocks(self):
        stocks = self._tree.inorder()
        for stock in stocks:
            print(f"{stock.stock_symbol} - {stock.stock_name} - {stock.low}-{stock.max_price}")


# Example usage:
if __name__ == "__main__":
    manager = StockPriceManager()
    manager.insert("AAPL", "Apple Inc.", 150.0, 0)
    manager.insert("GOOGL", "Alphabet Inc.", 2800.0, 0)
    manager.insert("AMZN", "Amazon.com Inc.", 3400.0, 0)

    print("Current price of AAPL:", manager.lookup(150))
    print("Stocks in price range 1000 to 2000:", manager.range_query(1000, 2000))
    
    # Check alerts
    print("Alerts:", manager.check_alerts())
    
    # Find 50th percentile stock
    print("Finding 50th percentile stock:", manager.find_percentile(50))
    
    # Moving average
    manager.insert("AAPL", "Apple Inc.", 145.0, 0)
    manager.insert("AAPL", "Apple Inc.", 155.0, 0)
    print("AAPL moving average (last 3 prices):", manager.calculate_moving_average(150, 3))
    
    # Correlation tracking
    manager.track_correlation("AAPL", "GOOGL")
    print("Correlated stocks with AAPL:", manager.find_correlated_stocks("AAPL"))

    manager.load_from_csv('./stocks/sample_stock_prices.csv')  # Load stocks from CSV

    # Display all stocks
    #print("All Stocks:")
    #manager.display_all_stocks()

    # Lookup stock price
    symbol_to_lookup = 'AAPL'
    stock = manager.lookup_stock_price(symbol_to_lookup)
    if stock:
        print(f"\nStock Price Lookup for {symbol_to_lookup}: {stock.low}-{stock.max_price}")
    else:
        print(f"\nStock {symbol_to_lookup} not found.")

    # Get top-K stocks
    top_k = manager.get_top_k_stocks(5)
    print("\nTop-K Stocks:")
    for stock in top_k:
        print(f"{stock.symbol} - {stock.name} - {stock.low_price}-{stock.high}")

    # Get bottom-K stocks
    bottom_k = stock_manager.get_bottom_k_stocks(5)
    print("\nBottom-K Stocks:")
    for stock in bottom_k:
        print(f"{stock.symbol} - {stock.name} - {stock.low_price}-{stock.high}")

    # Get stocks in price range
    low_price, high_price = 100, 200
    stocks_in_range = stock_manager.get_stocks_in_price_range(low_price, high_price)
    print(f"\nStocks in price range {low_price}-{high_price}:")
    for stock in stocks_in_range:
        print(f"{stock.symbol} - {stock.name} - {stock.low_price}-{stock.high_price}")
 