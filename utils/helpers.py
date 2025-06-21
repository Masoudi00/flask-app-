from flask import redirect, render_template, session, flash
from functools import wraps

def apology(message: str, code: int = 400):
    """Flash error message to user and redirect to previous page."""
    flash(f"Error: {message}", "error")
    return redirect("/")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value: float) -> str:
    """Format value as USD."""
    return f"${value:,.2f}" 