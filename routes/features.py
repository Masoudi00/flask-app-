from flask import Blueprint, flash, redirect, request, session
from models.watchlist import Watchlist, PriceAlert
from utils.helpers import apology, login_required
from utils.stock_utils import lookup

features_bp = Blueprint('features', __name__)

def init_features_routes(app, db):
    """Initialize feature routes"""
    watchlist_model = Watchlist(db)
    price_alert_model = PriceAlert(db)
    
    @features_bp.route("/watchlist/add", methods=["POST"])
    @login_required
    def add_to_watchlist():
        """Add a stock to watchlist"""
        
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("must provide symbol", 400)

        # Verify the symbol exists
        quote = lookup(symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        if watchlist_model.add_to_watchlist(session["user_id"], symbol):
            flash(f"Added {symbol} to watchlist!")
            return redirect("/")
        else:
            return apology("stock already in watchlist", 400)

    @features_bp.route("/watchlist/remove", methods=["POST"])
    @login_required
    def remove_from_watchlist():
        """Remove a stock from watchlist"""
        
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("must provide symbol", 400)

        watchlist_model.remove_from_watchlist(session["user_id"], symbol)
        flash(f"Removed {symbol} from watchlist!")
        return redirect("/")

    @features_bp.route("/alert/add", methods=["POST"])
    @login_required
    def add_alert():
        """Add a price alert"""
        
        symbol = request.form.get("symbol").upper()
        target_price = float(request.form.get("target_price"))
        alert_type = request.form.get("alert_type")  # 'above' or 'below'

        if not symbol or not target_price or not alert_type:
            return apology("must provide all fields", 400)

        # Verify the symbol exists
        quote = lookup(symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        price_alert_model.add_alert(session["user_id"], symbol, target_price, alert_type)
        flash(f"Added price alert for {symbol}!")
        return redirect("/")

    @features_bp.route("/alert/remove", methods=["POST"])
    @login_required
    def remove_alert():
        """Remove a price alert"""
        
        alert_id = request.form.get("alert_id")
        if not alert_id:
            return apology("must provide alert ID", 400)

        price_alert_model.remove_alert(int(alert_id), session["user_id"])
        flash("Price alert removed!")
        return redirect("/")

    @features_bp.route("/add_note", methods=["POST"])
    @login_required
    def add_note():
        """Add a note to a transaction"""
        
        transaction_id = request.form.get("transaction_id")
        note = request.form.get("note")

        if not transaction_id or not note:
            return apology("must provide transaction ID and note", 400)

        db.execute(
            "INSERT INTO transaction_notes (transaction_id, note) VALUES (?, ?)",
            transaction_id, note
        )
        flash("Note added to transaction!")
        return redirect("/history")

    app.register_blueprint(features_bp) 