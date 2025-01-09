from flask import Flask
import os

from flask.cli import load_dotenv


def create_app(test_config=None):
    load_dotenv()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # the key should be changed in deployment
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        WEATHERSTACK_API_KEY=os.getenv("WEATHERSTACK_API_KEY"),
        DEBUG=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # it forces it to get it from config.py
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import weather

    app.register_blueprint(weather.bp)


    return app