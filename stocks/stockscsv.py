import csv
from dataclasses import dataclass
from datastructures.avltree import AVLTree  # Ensure you have this module
from datastructures.intervaltree import IntervalTree  # Ensure you have this module

@dataclass(order=True)
class Stock:
    symbol: str
    name: str
    low: int
    high: int

class StockManager:
    def __init__(self):
        self._interval_tree = IntervalTree()
        self._stocks = AVLTree()  # Assuming AVLTree is used to keep stocks sorted

    def add_stock(self, stock: Stock):
        # Add stock to the interval tree
        self._interval_tree.insert(stock.low, stock.high, stock)
        # Add stock to AVL tree for sorted access
        self._stocks.insert(stock)  # Assuming AVLTree has an insert method

    def load_from_csv(self, filepath):
        with open(filepath, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                symbol, name, low, high = row[0], row[1], int(row[2]), int(row[3])
                stock = Stock(symbol, name, low, high)
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

def main():
    stock_manager = StockManager()
    stock_manager.load_from_csv('./stocks/sample_stock_prices.csv')  # Load stocks from CSV

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

if __name__ == "__main__":
    main()
