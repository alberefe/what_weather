from __future__ import annotations

import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from what_weather.app_factory import db
from what_weather.database_models import *

bp = Blueprint("auth", __name__, url_prefix="/auth")


def register_user(username: str, password: str) -> tuple[bool, str]:
    error = None

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."
    elif db.session.query(User).filter_by(username=username).scalar() is not None:
        error = f"User {username} is already registered."

    if error is None:
        db.session.add(
            User(username=username, password=generate_password_hash(password))
        )
        db.session.commit()
        return (
            True,
            "Registered successfully.",
        )

    return False, error


@bp.route("/register", methods=("GET", "POST"))
def register_view():
    if request.method == "POST":

        username = request.form["username"],
        password = request.form["password"]

        success, message = register_user(
            username,
            password
        )

        if success:
            return redirect(url_for("auth.login_view"))

        flash(message)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        user = db.session.query(User).filter_by(username=username).scalar()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.user_id
            return redirect(url_for("weather.index"))

        flash(error)

    return render_template("auth/login.html")


# registers a function that runs before the view function, no matter what URL
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter_by(user_id=user_id).scalar()


# to log out you need to remove the user id from the session
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("weather.index"))


# creating, updating, and deleting blog posts will require a user to be logged in
# we can use a decorator to check this for each view it's applied to
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


# the name associated with a view is also called the endpoint, and by default it's the same as the name of the view function
