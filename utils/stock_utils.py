import requests
from typing import Dict, Optional
import time

# Cache storage and expiration time
_cache = {}
_CACHE_EXPIRATION_SECONDS = 300  # 5 minutes

def lookup(symbol: str) -> Optional[Dict]:
    """Look up quote for symbol."""
    # Check cache first
    if symbol in _cache:
        cached_data, timestamp = _cache[symbol]
        if time.time() - timestamp < _CACHE_EXPIRATION_SECONDS:
            return cached_data

    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()

        result = {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }

        # Store in cache
        _cache[symbol] = (result, time.time())

        return result
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

def get_stock_sector(symbol: str) -> str:
    """Get the sector for a given stock symbol"""
    # This is a simplified version. In a real application, you would want to use
    # a proper financial API or database to get this information
    sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Technology",
        "AMZN": "Consumer",
        "META": "Technology",
        "TSLA": "Consumer",
        "NVDA": "Technology",
        "JPM": "Finance",
        "JNJ": "Healthcare",
        "V": "Finance",
        "PG": "Consumer",
        "HD": "Consumer",
        "BAC": "Finance",
        "DIS": "Consumer",
        "NFLX": "Technology",
        "ADBE": "Technology"
    }
    return sectors.get(symbol, "Other")

def get_popular_stocks() -> list:
    """Get list of popular stocks"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM",
        "JNJ", "V", "PG", "HD", "BAC", "DIS", "NFLX", "ADBE"
    ]

def calculate_change_percentage(current_price: float, previous_price: float) -> float:
    """Calculate percentage change between two prices"""
    if previous_price == 0:
        return 0
    return ((current_price - previous_price) / previous_price) * 100 