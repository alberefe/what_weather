from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app
)
from werkzeug.exceptions import abort
from what_weather.auth import login_required
import requests
import os

bp = Blueprint("weather", __name__, url_prefix="/weather")


def get_weather_data(city):
    """
    Makes the request to the weather API and returns data for a city
    :param city: string
    """
    # API requests
    params_request = {
        'access_key': current_app.config['WEATHERSTACK_API_KEY'],
        'query': city,
    }

    try:
        response = requests.get(
            'https://api.weatherstack.com/current',
            params=params_request,
            timeout=10
        )
        # check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        weather_data = response.json()

        if 'error' in weather_data:
            return None, weather_data['error']

        return weather_data, None

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
        error = None

        if not city:
            error = "City required"
            flash(error)
        else:
            weather_data, error = get_weather_data(city)

            if error:
                flash(error)

            else:
                return render_template('weather/index.html',
                                       weather_data=weather_data['current'],
                                       location=weather_data['location'])

    return render_template('weather/index.html')
