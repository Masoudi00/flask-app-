from flask import Blueprint, flash, redirect, render_template, request, session
from flask.views import MethodView
from models.user import User
from utils.helpers import apology, login_required

auth_bp = Blueprint('auth', __name__)

class AuthView(MethodView):
    def __init__(self, db):
        self.user_model = User(db)

    def get(self, action=None):
        if action == 'login':
            return render_template("login.html")
        elif action == 'register':
            return render_template("register.html")
        elif action == 'change_password':
            return render_template("change_password.html")
        elif action == 'logout':
            session.clear()
            return redirect("/login")
        return apology("Not found", 404)

    def post(self, action=None):
        if action == 'login':
            session.clear()
            if not request.form.get("username"):
                return apology("must provide username", 403)
            elif not request.form.get("password"):
                return apology("must provide password", 403)
            user = self.user_model.authenticate(
                request.form.get("username"),
                request.form.get("password")
            )
            if not user:
                return apology("invalid username and/or password", 403)
            session["user_id"] = user["id"]
            return redirect("/")
        elif action == 'register':
            if not request.form.get("username"):
                return apology("must provide username", 400)
            elif not request.form.get("password"):
                return apology("must provide password", 400)
            elif not request.form.get("confirmation"):
                return apology("must confirm password", 400)
            elif request.form.get("password") != request.form.get("confirmation"):
                return apology("password must match", 400)
            if self.user_model.username_exists(request.form.get("username")):
                return apology("username already taken", 400)
            try:
                user_id = self.user_model.create(
                    request.form.get("username"),
                    request.form.get("password")
                )
                session["user_id"] = user_id
                return redirect("/")
            except:
                return apology("registration failed", 500)
        elif action == 'change_password':
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirmation")
            if not old_password or not new_password or not confirm_password:
                return apology("must provide all fields", 403)
            if new_password != confirm_password:
                return apology("new passwords must match", 403)
            if not self.user_model.change_password(session["user_id"], old_password, new_password):
                return apology("incorrect old password", 403)
            return redirect("/")
        return apology("Not found", 404)

def init_auth_routes(app, db):
    view = AuthView.as_view('auth_view', db=db)
    # Login
    auth_bp.add_url_rule('/login', view_func=view, methods=['GET', 'POST'], defaults={'action': 'login'}, endpoint='login')
    # Logout (GET only)
    auth_bp.add_url_rule('/logout', view_func=view, methods=['GET'], defaults={'action': 'logout'}, endpoint='logout')
    # Register
    auth_bp.add_url_rule('/register', view_func=view, methods=['GET', 'POST'], defaults={'action': 'register'}, endpoint='register')
    # Change password
    auth_bp.add_url_rule('/change_password', view_func=login_required(view), methods=['GET', 'POST'], defaults={'action': 'change_password'}, endpoint='change_password')
    app.register_blueprint(auth_bp) 