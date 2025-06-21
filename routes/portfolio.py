from flask import Blueprint, flash, redirect, render_template, request, session
from flask.views import MethodView
import concurrent.futures
from models.portfolio import Portfolio
from models.user import User
from models.watchlist import Watchlist, PriceAlert
from utils.helpers import apology, login_required, usd
from utils.stock_utils import lookup, get_popular_stocks, get_stock_sector, calculate_change_percentage

portfolio_bp = Blueprint('portfolio', __name__)

class PortfolioView(MethodView):
    def __init__(self, db):
        self.portfolio_model = Portfolio(db)
        self.user_model = User(db)
        self.watchlist_model = Watchlist(db)
        self.price_alert_model = PriceAlert(db)

    def get(self, action=None):
        user_id = session["user_id"]
        if action == 'index':
            # Show portfolio of stocks
            rows = self.portfolio_model.get_holdings(user_id)
            total_stock_value = 0
            holdings = []
            portfolio_performance = {"daily_change": 0, "total_gain_loss": 0}
            for row in rows:
                symbol = row["symbol"]
                shares = row["shares"]
                stock = lookup(symbol)
                if stock is None:
                    return apology("Stock lookup failed", 403)
                current_price = stock["price"]
                total_value = shares * current_price
                transactions = self.portfolio_model.get_transactions_by_symbol(user_id, symbol)
                total_cost = sum(t["price"] * t["shares"] for t in transactions if t["shares"] > 0)
                total_shares_bought = sum(t["shares"] for t in transactions if t["shares"] > 0)
                avg_purchase_price = total_cost / total_shares_bought if total_shares_bought > 0 else 0
                gain_loss = (current_price - avg_purchase_price) * shares
                gain_loss_percentage = ((current_price - avg_purchase_price) / avg_purchase_price * 100) if avg_purchase_price > 0 else 0
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
                total_stock_value += total_value
                portfolio_performance["total_gain_loss"] += gain_loss
            cash = self.user_model.get_cash(user_id)
            grand_total = cash + total_stock_value
            watchlist = self.watchlist_model.get_watchlist(user_id)
            alerts = self.price_alert_model.get_alerts(user_id)
            return render_template(
                "index.html",
                holdings=holdings,
                cash=usd(cash),
                grand_total=usd(grand_total),
                portfolio_performance=portfolio_performance,
                watchlist=watchlist,
                alerts=alerts
            )
        elif action == 'buy':
            popular_stocks = get_popular_stocks()
            def fetch_stock_data(symbol):
                stock = lookup(symbol)
                if not stock:
                    return None
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
                results = executor.map(fetch_stock_data, popular_stocks)
                stocks = [stock for stock in results if stock]
            return render_template("buy.html", stocks=stocks)
        elif action == 'sell':
            rows = self.portfolio_model.get_holdings(user_id)
            stocks = []
            for row in rows:
                symbol = row["symbol"]
                shares = row["shares"]
                stock = lookup(symbol)
                if not stock:
                    continue
                transactions = self.portfolio_model.get_transactions_by_symbol(user_id, symbol)
                total_cost = sum(t["price"] * t["shares"] for t in transactions if t["shares"] > 0)
                total_shares_bought = sum(t["shares"] for t in transactions if t["shares"] > 0)
                avg_purchase_price = total_cost / total_shares_bought if total_shares_bought > 0 else 0
                gain_loss = (stock["price"] - avg_purchase_price) * shares
                gain_loss_percentage = ((stock["price"] - avg_purchase_price) / avg_purchase_price * 100) if avg_purchase_price > 0 else 0
                stocks.append({
                    "symbol": symbol,
                    "name": stock["name"],
                    "shares": shares,
                    "price": stock["price"],
                    "total_value": stock["price"] * shares,
                    "gain_loss": gain_loss,
                    "gain_loss_percentage": f"{gain_loss_percentage:.2f}"
                })
            return render_template("sell.html", stocks=stocks)
        elif action == 'history':
            transactions = self.portfolio_model.get_transactions(user_id)
            return render_template("history.html", transactions=transactions)
        return apology("Not found", 404)

    def post(self, action=None):
        user_id = session["user_id"]
        if action == 'buy':
            symbol = request.form.get("symbol")
            if not symbol:
                return apology("must provide a stock symbol", 400)
            try:
                shares = int(request.form.get("shares"))
                if shares <= 0:
                    return apology("shares must be a positive integer", 400)
            except ValueError:
                return apology("shares must be a valid number", 400)
            stock = lookup(symbol)
            if stock is None:
                return apology("invalid stock symbol", 400)
            cash = self.user_model.get_cash(user_id)
            total_cost = stock["price"] * shares
            if cash < total_cost:
                return apology("can't afford", 400)
            self.user_model.update_cash(user_id, -total_cost)
            self.portfolio_model.add_shares(user_id, symbol, shares)
            self.portfolio_model.record_transaction(user_id, symbol, shares, stock["price"])
            return redirect("/")
        elif action == 'sell':
            symbol = request.form.get("symbol")
            shares = request.form.get("shares")
            if not symbol:
                return apology("must provide symbol", 400)
            try:
                shares = int(shares)
                if shares <= 0:
                    return apology("shares must be positive integer", 400)
            except ValueError:
                return apology("shares must be valid number", 400)
            current_holding = self.portfolio_model.get_holding(user_id, symbol)
            if not current_holding or current_holding["shares"] < shares:
                return apology("not enough shares", 400)
            stock = lookup(symbol)
            if not stock:
                return apology("invalid symbol", 400)
            proceeds = stock["price"] * shares
            self.user_model.update_cash(user_id, proceeds)
            self.portfolio_model.remove_shares(user_id, symbol, shares)
            self.portfolio_model.record_transaction(user_id, symbol, -shares, stock["price"])
            return redirect("/")
        return apology("Not found", 404)

def init_portfolio_routes(app, db):
    view = PortfolioView.as_view('portfolio_view', db=db)
    portfolio_bp.add_url_rule('/', view_func=login_required(view), methods=['GET'], defaults={'action': 'index'}, endpoint='index')
    portfolio_bp.add_url_rule('/buy', view_func=login_required(view), methods=['GET', 'POST'], defaults={'action': 'buy'}, endpoint='buy')
    portfolio_bp.add_url_rule('/sell', view_func=login_required(view), methods=['GET', 'POST'], defaults={'action': 'sell'}, endpoint='sell')
    portfolio_bp.add_url_rule('/history', view_func=login_required(view), methods=['GET'], defaults={'action': 'history'}, endpoint='history')
    app.register_blueprint(portfolio_bp) 