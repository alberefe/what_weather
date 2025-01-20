from __future__ import annotations

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from what_weather import config
from what_weather.config import config

# Create the object to deal with the database
db = SQLAlchemy()


def create_app(config_name=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if config_name is None:
        config_name = "development_config"

    app.config.from_object(config[config_name])

    # Connect the database to the flask app
    db.init_app(app)


    # Create tables of the database
    with app.app_context():
        db.create_all()

    from what_weather import redis_cache

    redis_cache.init_app(app)

    @app.route("/")
    def index():
        return redirect(url_for("weather.index"))

    from what_weather import auth

    app.register_blueprint(auth.bp)

    from what_weather import weather

    app.register_blueprint(weather.bp)

    return app
