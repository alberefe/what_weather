from flask import Flask, redirect, url_for
import os
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Create the object to deal with the database
db = SQLAlchemy()


def create_app(test_config=None):
    load_dotenv()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # the key should be changed in deployment
        SECRET_KEY=os.getenv("SECRET_KEY"),
        WEATHERSTACK_API_KEY=os.getenv("WEATHERSTACK_API_KEY"),
        REDIS_URL=os.getenv("REDIS_URL"),
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}".format(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG = True,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # it forces it to get it from config.py
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    db.init_app(app)

    import what_weather.database_models

    # If the tables don't exist, create them
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
