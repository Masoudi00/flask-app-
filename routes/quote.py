from flask import Blueprint, render_template, request
from flask.views import MethodView
from utils.helpers import apology, login_required
from utils.stock_utils import lookup

quote_bp = Blueprint('quote', __name__)

class QuoteView(MethodView):
    def get(self):
        return render_template("quote.html")

    def post(self):
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide a stock symbol", 400)
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)
        return render_template("quoted.html", stock=stock)

def init_quote_routes(app):
    view = QuoteView.as_view('quote_view')
    quote_bp.add_url_rule('/quote', view_func=login_required(view), methods=['GET', 'POST'])
    app.register_blueprint(quote_bp) 