import json
import os
from urllib import request

import requests

from what_weather import config
from what_weather.config import config
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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

    from what_weather import database_models

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


    # TODO: find a nice place to leave this
    @app.route("/webhook", methods=["POST"])
    def bot_webhook():
        if request.method == "POST":
            req = request.get_json()

            chat_id = req["message"]["chat"]["id"]

            if "message" in req and "text" in req["message"]:
                message = req["message"]["text"].strip()

                # Passes the city name to the thing.
                weather_response = weather.get_weather_data(message)

                telegram_response = {
                    "chat_id": chat_id,
                    "text": weather_response
                }

                # Send response
                response = requests.post(
                    f"{https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage}",
                    json=telegram_response,
                )

                return {"ok": True}

            else:
                # Handle invalid message format
                telegram_response = {
                    "chat_id": chat_id,
                    "text": "What did you mean by that?"
                }

                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json=telegram_response
                )

                return {"ok": True}

    return app
