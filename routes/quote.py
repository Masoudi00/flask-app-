from flask import Blueprint, render_template, request
from utils.helpers import apology, login_required
from utils.stock_utils import lookup

quote_bp = Blueprint('quote', __name__)

def init_quote_routes(app):
    """Initialize quote routes"""
    
    @quote_bp.route("/quote", methods=["GET", "POST"])
    @login_required
    def quote():
        """Get stock quote."""
        if request.method == "POST":
            # Get stock symbol
            symbol = request.form.get("symbol")

            if not symbol:
                return apology("must provide a stock symbol", 400)

            # Look up the stock
            stock = lookup(symbol)

            # If stock is valid
            if stock is None:
                return apology("invalid stock symbol", 400)

            # Render with stock info
            return render_template("quoted.html", stock=stock)
        else:
            # If GET
            return render_template("quote.html")

    app.register_blueprint(quote_bp) 