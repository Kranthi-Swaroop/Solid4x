"""
MongoDB connection module for Solid4x backend.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "solid4x"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


# Collection accessors
def users_col():
    return get_db()["users"]


def user_profiles_col():
    return get_db()["user_profiles"]


def study_plans_col():
    return get_db()["study_plans"]


def retention_concepts_col():
    return get_db()["retention_concepts"]


def retention_reviews_col():
    return get_db()["retention_reviews"]


def dashboard_cache_col():
    return get_db()["dashboard_cache"]
