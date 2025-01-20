from __future__ import annotations

import redis
from flask import current_app, g


def get_redis_client():
    if "redis" not in g:
        g.redis = redis.from_url(current_app.config["REDIS_URL"])

    return g.redis


def close_redis_client(e=None):
    redis_client = g.pop("redis", None)

    if redis_client is not None:
        redis_client.close()


def init_app(app):
    (app.teardown_appcontext(close_redis_client))
