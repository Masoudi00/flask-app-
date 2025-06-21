from flask import Blueprint, flash, redirect, render_template, request, session
import concurrent.futures
from models.portfolio import Portfolio
from models.user import User
from models.watchlist import Watchlist, PriceAlert
from utils.helpers import apology, login_required, usd
from utils.stock_utils import lookup, get_popular_stocks, get_stock_sector, calculate_change_percentage

portfolio_bp = Blueprint('portfolio', __name__)

def init_portfolio_routes(app, db):
    """Initialize portfolio routes"""
    portfolio_model = Portfolio(db)
    user_model = User(db)
    watchlist_model = Watchlist(db)
    price_alert_model = PriceAlert(db)
    
    @portfolio_bp.route("/")
    @login_required
    def index():
        """Show portfolio of stocks"""
        # User id
        user_id = session["user_id"]

        # Query database for the user's portfolio
        rows = portfolio_model.get_holdings(user_id)

        # Initialize variables to hold the total stock value and stock details
        total_stock_value = 0
        holdings = []
        portfolio_performance = {"daily_change": 0, "total_gain_loss": 0}

        # Loop over the user's portfolio to fetch stock prices and calculate total value
        for row in rows:
            symbol = row["symbol"]
            shares = row["shares"]

            # Get the current price of the stock
            stock = lookup(symbol)

            if stock is None:
                return apology("Stock lookup failed", 403)

            current_price = stock["price"]
            total_value = shares * current_price

            # Get historical data for performance calculation
            transactions = portfolio_model.get_transactions_by_symbol(user_id, symbol)
            
            # Calculate average purchase price
            total_cost = sum(t["price"] * t["shares"] for t in transactions if t["shares"] > 0)
            total_shares_bought = sum(t["shares"] for t in transactions if t["shares"] > 0)
            avg_purchase_price = total_cost / total_shares_bought if total_shares_bought > 0 else 0
            
            # Calculate gain/loss
            gain_loss = (current_price - avg_purchase_price) * shares
            gain_loss_percentage = ((current_price - avg_purchase_price) / avg_purchase_price * 100) if avg_purchase_price > 0 else 0

            # Add the current holding details to the list
            holdings.append({
                "symbol": symbol,
                "name": stock["name"],
                "shares": shares,
                "price": usd(current_price),
                "total_value": usd(total_value),
                "avg_purchase_price": usd(avg_purchase_price),
                "gain_loss": usd(gain_loss),
                "gain_loss_percentage": f"{gain_loss_percentage:.2f}%"
            })

            # Add to the total stock value
            total_stock_value += total_value
            portfolio_performance["total_gain_loss"] += gain_loss

        # Query database for user's cash
        cash = user_model.get_cash(user_id)

        # Calculate the grand total (cash + stock value)
        grand_total = cash + total_stock_value

        # Get user's watchlist
        watchlist = watchlist_model.get_watchlist(user_id)

        # Get price alerts
        alerts = price_alert_model.get_alerts(user_id)

        # Render the index page with all the data
        return render_template(
            "index.html",
            holdings=holdings,
            cash=usd(cash),
            grand_total=usd(grand_total),
            portfolio_performance=portfolio_performance,
            watchlist=watchlist,
            alerts=alerts
        )

    @portfolio_bp.route("/buy", methods=["GET", "POST"])
    @login_required
    def buy():
        """Buy shares of stock"""
        if request.method == 'POST':
            # Check if symbol is empty
            symbol = request.form.get("symbol")
            if not symbol:
                return apology("must provide a stock symbol", 400)

            # Check if shares are valid and a positive integer
            try:
                shares = int(request.form.get("shares"))
                if shares <= 0:
                    return apology("shares must be a positive integer", 400)
            except ValueError:
                return apology("shares must be a valid number", 400)

            # Lookup stock and check if it's valid
            stock = lookup(symbol)
            if stock is None:
                return apology("invalid stock symbol", 400)

            # Get user's available cash
            cash = user_model.get_cash(session["user_id"])

            # Calculate total stock cost
            total_cost = stock["price"] * shares

            # Check if user can afford the stock
            if cash < total_cost:
                return apology("can't afford", 400)

            # Deduct the cost of the shares from the user's cash
            user_model.update_cash(session["user_id"], -total_cost)

            # Update the user's portfolio
            portfolio_model.add_shares(session["user_id"], symbol, shares)

            # Record the transaction
            portfolio_model.record_transaction(session["user_id"], symbol, shares, stock["price"])

            # Redirect to the homepage
            return redirect("/")

        else:
            # Get list of popular stocks
            popular_stocks = get_popular_stocks()

            def fetch_stock_data(symbol):
                """Fetch stock data for a single symbol."""
                stock = lookup(symbol)
                if not stock:
                    return None

                # Calculate 24h change
                # This is a simplified calculation. A more accurate one would use historical price data.
                # If the 'previousPrice' is available from the lookup, use it.
                # Otherwise, this example assumes no change if data isn't available.
                change = 0
                if 'previousPrice' in stock and stock['previousPrice'] is not None:
                    change = calculate_change_percentage(stock["price"], stock['previousPrice'])

                return {
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "price": stock["price"],
                    "change": round(change, 2),
                    "sector": get_stock_sector(symbol)
                }

            stocks = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Use map to fetch all stock data in parallel
                results = executor.map(fetch_stock_data, popular_stocks)
                # Filter out None results from failed lookups
                stocks = [stock for stock in results if stock]

            return render_template("buy.html", stocks=stocks)

    @portfolio_bp.route("/sell", methods=["GET", "POST"])
    @login_required
    def sell():
        """Sell shares of stock"""
        if request.method == 'POST':
            # Get symbol and shares from form
            symbol = request.form.get("symbol")
            shares = request.form.get("shares")

            # Validate inputs
            if not symbol:
                return apology("must provide symbol", 400)
            
            try:
                shares = int(shares)
                if shares <= 0:
                    return apology("shares must be positive integer", 400)
            except ValueError:
                return apology("shares must be valid number", 400)

            # Check if user owns enough shares
            current_holding = portfolio_model.get_holding(session["user_id"], symbol)
            if not current_holding or current_holding["shares"] < shares:
                return apology("not enough shares", 400)

            # Get current stock price
            stock = lookup(symbol)
            if not stock:
                return apology("invalid symbol", 400)

            # Calculate sale proceeds
            proceeds = stock["price"] * shares

            # Update user's cash
            user_model.update_cash(session["user_id"], proceeds)

            # Update portfolio
            portfolio_model.remove_shares(session["user_id"], symbol, shares)

            # Record the transaction (negative shares for sell)
            portfolio_model.record_transaction(session["user_id"], symbol, -shares, stock["price"])

            return redirect("/")

        else:
            # Get user's current holdings with details
            holdings = []
            rows = portfolio_model.get_holdings(session["user_id"])

            for row in rows:
                stock = lookup(row["symbol"])
                if stock:
                    # Get historical data for gain/loss calculation
                    transactions = portfolio_model.get_transactions_by_symbol(session["user_id"], row["symbol"])
                    
                    # Calculate average purchase price
                    total_cost = sum(t["price"] * t["shares"] for t in transactions if t["shares"] > 0)
                    total_shares_bought = sum(t["shares"] for t in transactions if t["shares"] > 0)
                    avg_purchase_price = total_cost / total_shares_bought if total_shares_bought > 0 else 0
                    
                    # Calculate gain/loss
                    current_value = stock["price"] * row["shares"]
                    cost_basis = avg_purchase_price * row["shares"]
                    gain_loss = current_value - cost_basis
                    gain_loss_percentage = ((stock["price"] - avg_purchase_price) / avg_purchase_price * 100) if avg_purchase_price > 0 else 0

                    holdings.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "shares": row["shares"],
                        "price": stock["price"],
                        "total_value": current_value,
                        "gain_loss": gain_loss,
                        "gain_loss_percentage": round(gain_loss_percentage, 2)
                    })

            return render_template("sell.html", stocks=holdings)

    @portfolio_bp.route("/history")
    @login_required
    def history():
        """Show history of transactions"""
        # Query the current user's transactions
        transactions = portfolio_model.get_transactions(session["user_id"])

        # Pass transaction into the template
        return render_template("history.html", transactions=transactions)

    app.register_blueprint(portfolio_bp) 