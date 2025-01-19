import os
from flask.cli import load_dotenv

load_dotenv()


class Config:
    """Base config class"""

    SECRET_KEY = os.getenv("SECRET_KEY")
    WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

    REDIS_URL = os.getenv("REDIS_URL")

    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}".format(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False


# Dictionary to select the appropriate configuration
config = {
    "development_config": DevelopmentConfig,
    "production_config": ProductionConfig,
    "default_config": DevelopmentConfig,
}
