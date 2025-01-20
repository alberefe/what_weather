from __future__ import annotations

from datetime import datetime

from what_weather.app_factory import db


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    # relationship with SearchHistory
    searches = db.relationship("SearchHistory", back_populates="user", lazy=True)


class SearchHistory(db.Model):
    __tablename__ = "search_history"

    search_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    city = db.Column(db.String, nullable=False)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationship with User
    user = db.relationship("User", back_populates="searches")
