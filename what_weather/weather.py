from __future__ import annotations

import json
from datetime import datetime

import redis
import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    render_template,
    request,
)

from what_weather.app_factory import db
from what_weather.auth import login_required
from what_weather.database_models import SearchHistory
from what_weather.redis_cache import get_redis_client


class WeatherService:
    """Handles all weather-related business logic."""

    def __init__(self):
        self.cache_ttl = 3600  # 1 hour cache duration

    def get_weather_data(self, city: str) -> tuple[dict | None, str | None]:
        """Gets weather data for a city.

        The method first checks if the data is in Redis cache. If not, it makes
        an API call to WeatherStack and caches the result for future use.

        Args:
            city: Name of the city to get weather data for

        Returns:
            A tuple of (weather_data, error_message). If successful, error_message
            will be None. If there's an error, weather_data will be None.
        """
        # Define API parameters at the start so they're available throughout the method
        params = {
            "access_key": current_app.config["WEATHERSTACK_API_KEY"],
            "query": city,
        }

        # First try to get from cache
        try:
            redis_client = get_redis_client()
            cache_key = f"weather:city:{city.lower()}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                try:
                    return json.loads(cached_data.decode("utf-8")), None
                except json.JSONDecodeError:
                    # If cache is corrupted, delete it
                    redis_client.delete(cache_key)
        except redis.RedisError:
            # Log Redis error but continue to API call
            pass

        # If we get here, either cache failed or data wasn't in cache
        # Make the API call
        try:
            response = requests.get(
                "https://api.weatherstack.com/current",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            weather_data = response.json()

            if "error" in weather_data:
                return None, weather_data["error"]["info"]

            # Try to cache the successful response
            try:
                redis_client = get_redis_client()
                cache_key = f"weather:city:{city.lower()}"
                redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(weather_data)
                )
            except redis.RedisError:
                # TODO: log cache error
                # Log cache error but continue since we have the data
                pass

            return weather_data, None

        except requests.RequestException as e:
            return None, str(e)

    def save_search_history(self, user_id: int, city: str) -> None:
        """Saves a user's search to the database.

        Args:
            user_id: The ID of the user making the search
            city: The name of the city that was searched
        """
        search = SearchHistory(
            user_id=user_id,
            city=city.lower(),
            searched_at=datetime.now()
        )
        db.session.add(search)
        db.session.commit()

    def get_user_search_history(self, user_id: int) -> list[SearchHistory]:
        """Retrieves a user's search history from the database.

        Args:
            user_id: The ID of the user whose history to retrieve

        Returns:
            A list of SearchHistory objects for the user
        """
        return db.session.query(SearchHistory).filter_by(user_id=user_id).all()


# Create Blueprint and service instance
bp = Blueprint("weather", __name__, url_prefix="/weather")
weather_service = WeatherService()


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """Handles weather queries and display the weather dashboard."""
    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            flash("City required")
            return render_template("weather/index.html")

        weather_data, error = weather_service.get_weather_data(city)

        if error:
            flash(error)
            return render_template("weather/index.html")

        # Only save to history if we got valid weather data
        weather_service.save_search_history(g.user.user_id, city)

        return render_template(
            "weather/index.html",
            weather_data=weather_data["current"],
            location=weather_data["location"]
        )

    return render_template("weather/index.html")


@bp.route("/history")
@login_required
def view_history():
    """Display the user's weather search history."""
    search_list = weather_service.get_user_search_history(g.user.user_id)
    return render_template("weather/history.html", search_list=search_list)
