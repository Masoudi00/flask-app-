# Finance App - Project Structure & Database Overview

## Directory & File Overview

### Root Directory

- **app.py**  
  Main Flask application entry point. Initializes the app, configures blueprints, and sets up the database and session.

- **requirements.txt**  
  Lists all Python dependencies required to run the project.

- **test_refactored.py**  
  Script for testing utility functions and basic app features.

- **README.md / README_REFACTORED.md**  
  Project documentation and structure overview.

- **finance.db**  
  SQLite database file storing all user, portfolio, transaction, and feature data.

- **database_schema.txt**  
  Text file describing the database schema and table structure.

- **video.mp4**  
  Demo or instructional video for the project.

---

### `/config/`  
**Purpose:** Application configuration and database/session setup.

- **database.py**  
  Handles database initialization, table creation (including watchlist, price alerts, transaction notes), and session configuration.

---

### `/models/`  
**Purpose:** Data models and business logic.

- **user.py**  
  User authentication, registration, password management, and cash balance logic.

- **portfolio.py**  
  Portfolio management: holdings, transactions, buying/selling shares, and performance calculations.

- **watchlist.py**  
  Watchlist and price alert management for users.

---

### `/routes/`  
**Purpose:** Flask route handlers (controllers).

- **auth.py**  
  Authentication routes: login, logout, register, change password.

- **portfolio.py**  
  Portfolio routes: dashboard, buy, sell, transaction history.

- **quote.py**  
  Stock quote lookup route.

- **features.py**  
  Watchlist management, price alerts, and transaction notes.

---

### `/utils/`  
**Purpose:** Utility and helper functions.

- **helpers.py**  
  Common utilities: error handling, login-required decorator, USD formatting.

- **stock_utils.py**  
  Stock-related utilities: symbol lookup, sector info, popular stocks, price change calculations.

---

### `/templates/`  
**Purpose:** Jinja2 HTML templates for all web pages.

- **layout.html**  
  Base template for all pages.

- **index.html**  
  Main dashboard after login.

- **buy.html, sell.html**  
  Pages for buying and selling stocks.

- **history.html**  
  Transaction history page.

- **login.html, register.html, change_password.html**  
  Authentication and user management pages.

- **quote.html, quoted.html**  
  Stock quote lookup and result display.

---

### `/static/`  
**Purpose:** Static assets (CSS, images, icons).

- **css/**  
  Custom stylesheets.

- **src/**  
  Source CSS for Tailwind or other preprocessors.

- **favicon.ico, I_heart_validator.png**  
  Icons and images.

---

### `/website_pages/`  
**Purpose:** Screenshots of the website for documentation or demo purposes.

---

## Database Tables (`finance.db`)

The following tables are used in the application:

### 1. **users**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
- `username`: TEXT NOT NULL (UNIQUE)
- `hash`: TEXT NOT NULL (password hash)
- `cash`: NUMERIC NOT NULL DEFAULT 10000.00

### 2. **transactions**
- `user_id`: FOREIGN KEY REFERENCES users(id)
- `symbol`: TEXT
- `shares`: INTEGER (positive for buy, negative for sell)
- `price`: NUMERIC
- `timestamp`: DATETIME

### 3. **portfolio**
- `user_id`: INTEGER
- `symbol`: TEXT
- `shares`: INTEGER

### 4. **watchlist**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER NOT NULL
- `symbol`: TEXT NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### 5. **price_alerts**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER NOT NULL
- `symbol`: TEXT NOT NULL
- `target_price`: NUMERIC NOT NULL
- `alert_type`: TEXT NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### 6. **transaction_notes**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `transaction_id`: INTEGER NOT NULL
- `note`: TEXT NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**Indexes and Constraints:**
- Unique index on `users.username`
- Unique index on `(user_id, symbol)` in `portfolio`
- Foreign key constraints for data integrity

---

## How to Run

```bash
pip install -r requirements.txt
flask run
```

---

## Summary

This project is a modular, maintainable, and extensible finance web application.  
- **Models** encapsulate business logic and database access.
- **Routes** handle HTTP requests and responses.
- **Templates** provide a modern, responsive UI.
- **Database** is normalized and supports all core features (portfolio, watchlist, alerts, notes).

---

**This README provides a clear, up-to-date project overview for new developers.** 