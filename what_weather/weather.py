import os
from what_weather.app_factory import db
from what_weather.database_models import *
import redis
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from what_weather.auth import login_required
from what_weather.redis_cache import get_redis_client

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bp = Blueprint("weather", __name__, url_prefix="/weather")


def get_weather_data(city):
    """
    Makes the request to the weather API and returns data for a city
    :param city: string
    """
    CACHE_TTL = 3600
    cache_key = f"weather:city:{city.lower()}"

    # API requests
    params_request = {
        "access_key": current_app.config["WEATHERSTACK_API_KEY"],
        "query": city,
    }

    try:
        redis_client = get_redis_client()
        cached_data = redis_client.get(cache_key)

        if cached_data:
            try:
                weather_data = json.loads(cached_data.decode("utf-8"))
                return weather_data, None
            except json.decoder.JSONDecodeError:
                # If it's corrupted, fetch new data
                redis_client.delete(cache_key)

        # If no cache or corrupted cache, make API call
        response = requests.get(
            "https://api.weatherstack.com/current", params=params_request, timeout=10
        )
        # check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        weather_data = response.json()

        if "error" in weather_data:
            return None, weather_data["error"]

        # try to store the results in cache
        try:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(weather_data))
        except redis.RedisError:
            pass

        return weather_data, None

    except redis.RedisError:
        # If redis is down, fallback to direct API call
        try:
            response = requests.get(
                "https://api.weatherstack.com/current",
                params=params_request,
                timeout=10,
            )
            response.raise_for_status()

            weather_data = response.json()

            if "error" in weather_data:
                return None, weather_data["error"]

            return weather_data, None

        except requests.RequestException as e:
            return None, e

    except requests.RequestException as e:
        return None, e


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """
    Displays the form and process the weather queries.
    :return:
    """
    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            error = "City required"
            flash(error)
        else:
            weather_data, error = get_weather_data(city)

            if error:
                flash(error)

            else:
                save_search(g.user.user_id, city)
                return render_template(
                    "weather/index.html",
                    weather_data=weather_data["current"],
                    location=weather_data["location"],
                )

    return render_template("weather/index.html")


def save_search(user_id, city):
    user_id = user_id
    city = city.lower()
    search = SearchHistory(user_id=user_id, city=city, searched_at=datetime.now())
    db.session.add(search)
    db.session.commit()


@bp.route("/history")
@login_required
def view_history():
    search_list = db.session.query(SearchHistory).filter_by(user_id=g.user.user_id).all()
    return render_template("weather/history.html", search_list=search_list)

