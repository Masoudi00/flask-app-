from flask import Blueprint, flash, redirect, request, session
from flask.views import MethodView
from models.watchlist import Watchlist, PriceAlert
from utils.helpers import apology, login_required
from utils.stock_utils import lookup

features_bp = Blueprint('features', __name__)

class FeaturesView(MethodView):
    def __init__(self, db):
        self.watchlist_model = Watchlist(db)
        self.price_alert_model = PriceAlert(db)
        self.db = db

    def post(self, action=None):
        if action == 'add_to_watchlist':
            symbol = request.form.get("symbol").upper()
            if not symbol:
                return apology("must provide symbol", 400)
            quote = lookup(symbol)
            if quote is None:
                return apology("invalid symbol", 400)
            if self.watchlist_model.add_to_watchlist(session["user_id"], symbol):
                flash(f"Added {symbol} to watchlist!")
                return redirect("/")
            else:
                return apology("stock already in watchlist", 400)
        elif action == 'remove_from_watchlist':
            symbol = request.form.get("symbol").upper()
            if not symbol:
                return apology("must provide symbol", 400)
            self.watchlist_model.remove_from_watchlist(session["user_id"], symbol)
            flash(f"Removed {symbol} from watchlist!")
            return redirect("/")
        elif action == 'add_alert':
            symbol = request.form.get("symbol").upper()
            try:
                target_price = float(request.form.get("target_price"))
            except (TypeError, ValueError):
                return apology("invalid target price", 400)
            alert_type = request.form.get("alert_type")
            if not symbol or not target_price or not alert_type:
                return apology("must provide all fields", 400)
            quote = lookup(symbol)
            if quote is None:
                return apology("invalid symbol", 400)
            self.price_alert_model.add_alert(session["user_id"], symbol, target_price, alert_type)
            flash(f"Added price alert for {symbol}!")
            return redirect("/")
        elif action == 'remove_alert':
            alert_id = request.form.get("alert_id")
            if not alert_id:
                return apology("must provide alert ID", 400)
            self.price_alert_model.remove_alert(int(alert_id), session["user_id"])
            flash("Price alert removed!")
            return redirect("/")
        elif action == 'add_note':
            transaction_id = request.form.get("transaction_id")
            note = request.form.get("note")
            if not transaction_id or not note:
                return apology("must provide transaction ID and note", 400)
            self.db.execute(
                "INSERT INTO transaction_notes (transaction_id, note) VALUES (?, ?)",
                transaction_id, note
            )
            flash("Note added to transaction!")
            return redirect("/history")
        return apology("Not found", 404)

def init_features_routes(app, db):
    view = FeaturesView.as_view('features_view', db=db)
    features_bp.add_url_rule('/watchlist/add', view_func=login_required(view), methods=['POST'], defaults={'action': 'add_to_watchlist'}, endpoint='add_to_watchlist')
    features_bp.add_url_rule('/watchlist/remove', view_func=login_required(view), methods=['POST'], defaults={'action': 'remove_from_watchlist'}, endpoint='remove_from_watchlist')
    features_bp.add_url_rule('/alert/add', view_func=login_required(view), methods=['POST'], defaults={'action': 'add_alert'}, endpoint='add_alert')
    features_bp.add_url_rule('/alert/remove', view_func=login_required(view), methods=['POST'], defaults={'action': 'remove_alert'}, endpoint='remove_alert')
    features_bp.add_url_rule('/add_note', view_func=login_required(view), methods=['POST'], defaults={'action': 'add_note'}, endpoint='add_note')
    app.register_blueprint(features_bp) 