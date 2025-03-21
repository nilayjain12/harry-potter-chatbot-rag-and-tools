import os
from pymongo import MongoClient

# Retrieve MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGO_URI, connect=False)
db = client[DATABASE_NAME]

def get_db():
    """Return the database connection."""
    return db
