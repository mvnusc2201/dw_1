import os
from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """Reutiliza una conexión a MongoDB."""

    uri = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/"
    )

    return MongoClient(
        uri,
        serverSelectionTimeoutMS=3000
    )


def get_users_collection() -> Collection:
    """Obtiene la colección de identidades."""

    client = get_mongo_client()
    db = client["dbIdentity"]

    return db["usuarios"]