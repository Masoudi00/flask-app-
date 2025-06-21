from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Dict, List, Optional

class User:
    def __init__(self, db: SQL):
        self.db = db
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        rows = self.db.execute("SELECT * FROM users WHERE username = ?", username)
        
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return None
        
        return rows[0]
    
    def create(self, username: str, password: str) -> int:
        """Create a new user"""
        hash = generate_password_hash(password)
        return self.db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username, hash
        )
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        rows = self.db.execute("SELECT * FROM users WHERE id = ?", user_id)
        return rows[0] if rows else None
    
    def get_cash(self, user_id: int) -> float:
        """Get user's cash balance"""
        rows = self.db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        return rows[0]["cash"] if rows else 0.0
    
    def update_cash(self, user_id: int, amount: float):
        """Update user's cash balance"""
        self.db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, user_id)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_by_id(user_id)
        if not user or not check_password_hash(user["hash"], old_password):
            return False
        
        new_hash = generate_password_hash(new_password)
        self.db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
        return True
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        rows = self.db.execute("SELECT * FROM users WHERE username = ?", username)
        return len(rows) > 0 