from cs50 import SQL
from typing import Dict, List, Optional
from datetime import datetime

class Portfolio:
    def __init__(self, db: SQL):
        self.db = db
    
    def get_holdings(self, user_id: int) -> List[Dict]:
        """Get user's current portfolio holdings"""
        return self.db.execute(
            "SELECT symbol, shares FROM portfolio WHERE user_id = ?", 
            user_id
        )
    
    def get_holding(self, user_id: int, symbol: str) -> Optional[Dict]:
        """Get specific holding for user and symbol"""
        rows = self.db.execute(
            "SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?",
            user_id, symbol
        )
        return rows[0] if rows else None
    
    def add_shares(self, user_id: int, symbol: str, shares: int):
        """Add shares to portfolio (buy)"""
        self.db.execute("""
            INSERT INTO portfolio (user_id, symbol, shares)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, symbol)
            DO UPDATE SET shares = shares + excluded.shares
        """, user_id, symbol, shares)
    
    def remove_shares(self, user_id: int, symbol: str, shares: int):
        """Remove shares from portfolio (sell)"""
        current_holding = self.get_holding(user_id, symbol)
        if not current_holding:
            raise ValueError("No shares to sell")
        
        current_shares = current_holding["shares"]
        if current_shares < shares:
            raise ValueError("Not enough shares")
        
        if current_shares == shares:
            # Remove entire holding
            self.db.execute("""
                DELETE FROM portfolio 
                WHERE user_id = ? AND symbol = ?
            """, user_id, symbol)
        else:
            # Update shares
            self.db.execute("""
                UPDATE portfolio 
                SET shares = shares - ? 
                WHERE user_id = ? AND symbol = ?
            """, shares, user_id, symbol)
    
    def record_transaction(self, user_id: int, symbol: str, shares: int, price: float):
        """Record a transaction"""
        self.db.execute("""
            INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (?, ?, ?, ?)
        """, user_id, symbol, shares, price)
    
    def get_transactions(self, user_id: int) -> List[Dict]:
        """Get user's transaction history"""
        return self.db.execute("""
            SELECT t.id, t.symbol, t.shares, t.price, t.timestamp, n.note
            FROM transactions t
            LEFT JOIN transaction_notes n ON t.id = n.transaction_id
            WHERE t.user_id = ?
            ORDER BY t.timestamp DESC
        """, user_id)
    
    def get_transactions_by_symbol(self, user_id: int, symbol: str) -> List[Dict]:
        """Get transactions for a specific symbol"""
        return self.db.execute("""
            SELECT price, shares 
            FROM transactions 
            WHERE user_id = ? AND symbol = ? 
            ORDER BY timestamp
        """, user_id, symbol)
    
    def calculate_average_price(self, user_id: int, symbol: str) -> float:
        """Calculate average purchase price for a symbol"""
        transactions = self.get_transactions_by_symbol(user_id, symbol)
        total_cost = sum(t["price"] * t["shares"] for t in transactions if t["shares"] > 0)
        total_shares_bought = sum(t["shares"] for t in transactions if t["shares"] > 0)
        return total_cost / total_shares_bought if total_shares_bought > 0 else 0 