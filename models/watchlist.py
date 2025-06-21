from cs50 import SQL
from typing import Dict, List, Optional

class Watchlist:
    def __init__(self, db: SQL):
        self.db = db
    
    def get_watchlist(self, user_id: int) -> List[Dict]:
        """Get user's watchlist with current prices"""
        return self.db.execute("""
            SELECT w.symbol, s.name, s.price 
            FROM watchlist w 
            LEFT JOIN (
                SELECT symbol, name, price 
                FROM (
                    SELECT symbol, name, price,
                           ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                    FROM stock_prices
                ) t 
                WHERE rn = 1
            ) s ON w.symbol = s.symbol 
            WHERE w.user_id = ?
        """, user_id)
    
    def add_to_watchlist(self, user_id: int, symbol: str) -> bool:
        """Add a stock to watchlist"""
        try:
            self.db.execute(
                "INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)",
                user_id, symbol
            )
            return True
        except:
            return False
    
    def remove_from_watchlist(self, user_id: int, symbol: str):
        """Remove a stock from watchlist"""
        self.db.execute(
            "DELETE FROM watchlist WHERE user_id = ? AND symbol = ?",
            user_id, symbol
        )
    
    def is_in_watchlist(self, user_id: int, symbol: str) -> bool:
        """Check if stock is in user's watchlist"""
        rows = self.db.execute(
            "SELECT * FROM watchlist WHERE user_id = ? AND symbol = ?",
            user_id, symbol
        )
        return len(rows) > 0

class PriceAlert:
    def __init__(self, db: SQL):
        self.db = db
    
    def get_alerts(self, user_id: int) -> List[Dict]:
        """Get user's price alerts"""
        return self.db.execute(
            "SELECT id, symbol, target_price, alert_type FROM price_alerts WHERE user_id = ?",
            user_id
        )
    
    def add_alert(self, user_id: int, symbol: str, target_price: float, alert_type: str) -> int:
        """Add a price alert"""
        return self.db.execute(
            "INSERT INTO price_alerts (user_id, symbol, target_price, alert_type) VALUES (?, ?, ?, ?)",
            user_id, symbol, target_price, alert_type
        )
    
    def remove_alert(self, alert_id: int, user_id: int):
        """Remove a price alert"""
        self.db.execute(
            "DELETE FROM price_alerts WHERE id = ? AND user_id = ?",
            alert_id, user_id
        )
    
    def get_alert(self, alert_id: int, user_id: int) -> Optional[Dict]:
        """Get specific alert"""
        rows = self.db.execute(
            "SELECT * FROM price_alerts WHERE id = ? AND user_id = ?",
            alert_id, user_id
        )
        return rows[0] if rows else None 