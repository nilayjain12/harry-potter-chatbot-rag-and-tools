import os
from pymongo import MongoClient

# Retrieve MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def get_db():
    """Return the database connection."""
    return db
