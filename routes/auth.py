from flask import Blueprint, flash, redirect, render_template, request, session
from models.user import User
from utils.helpers import apology, login_required

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(app, db):
    """Initialize authentication routes"""
    user_model = User(db)
    
    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""
        # Forget any user_id
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 403)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 403)

            # Authenticate user
            user = user_model.authenticate(
                request.form.get("username"),
                request.form.get("password")
            )

            if not user:
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = user["id"]

            # Redirect user to home page
            return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")

    @auth_bp.route("/logout")
    def logout():
        """Log user out"""
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    @auth_bp.route("/register", methods=["GET", "POST"])
    def register():
        """Register user"""
        if request.method == "POST":
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)

            # Ensure password confirmation was submitted
            elif not request.form.get("confirmation"):
                return apology("must confirm password", 400)

            # Check if password and confirmation match
            elif request.form.get("password") != request.form.get("confirmation"):
                return apology("password must match", 400)

            # Check if username already exists
            if user_model.username_exists(request.form.get("username")):
                return apology("username already taken", 400)

            # Insert new user into database
            try:
                user_id = user_model.create(
                    request.form.get("username"),
                    request.form.get("password")
                )

                # Auto log-in
                session["user_id"] = user_id

                # Redirect user to homepage
                return redirect("/")

            except:
                return apology("registration failed", 500)

        else:
            return render_template("register.html")

    @auth_bp.route("/change_password", methods=["GET", "POST"])
    @login_required
    def change_password():
        """Change user password"""
        if request.method == "POST":
            # Get old password and new password from the form
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirmation")

            # Ensure old password, new password, and confirmation were submitted
            if not old_password or not new_password or not confirm_password:
                return apology("must provide all fields", 403)

            # Ensure new passwords match
            if new_password != confirm_password:
                return apology("new passwords must match", 403)

            # Change password
            if not user_model.change_password(session["user_id"], old_password, new_password):
                return apology("incorrect old password", 403)

            # Redirect to home page
            return redirect("/")

        else:
            return render_template("change_password.html")

    app.register_blueprint(auth_bp) 