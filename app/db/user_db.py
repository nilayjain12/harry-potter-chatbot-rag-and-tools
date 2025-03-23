from pymongo.errors import DuplicateKeyError
from db.mongo_connector import get_db

db = get_db()
users_collection = db["users"]
chat_history_collection = db["chat_history"]

# Create a unique index for username
users_collection.create_index("username", unique=True)

def register_user(username, password):
    """
    Register a new user.
    In production, use proper password hashing.
    """
    try:
        user = {"username": username, "password": password}
        users_collection.insert_one(user)
        return True, "Registration successful."
    except DuplicateKeyError:
        return False, "Username already exists."

def login_user(username, password):
    """Attempt to login a user."""
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return True, user["username"]  # Return only username instead of full user object
    return False, "Invalid username or password."

def get_chat_history(user_id):
    """Retrieve chat history for the given user_id (here, username)."""
    session = chat_history_collection.find_one({"user_id": user_id})
    if session and "history" in session:
        return session["history"]
    return []

def save_chat_message(user_id, user_message, bot_message):
    """Append a new chat message for the user."""
    chat_history_collection.update_one(
        {"user_id": user_id},
        {"$push": {"history": {"user": user_message, "bot": bot_message}}},
        upsert=True
    )

def clear_chat_history(user_id):
    """Clear the entire chat history for the user."""
    chat_history_collection.update_one(
        {"user_id": user_id},
        {"$set": {"history": []}},
        upsert=True
    )

def delete_chat_message(user_id, index):
    """Delete a single chat message pair at the given index for the user."""
    session = chat_history_collection.find_one({"user_id": user_id})
    if session and "history" in session:
        history = session["history"]
        if 0 <= index < len(history):
            # Remove the specific message pair from the history
            del history[index]
            chat_history_collection.update_one(
                {"user_id": user_id},
                {"$set": {"history": history}}
            )

def is_username_taken(username):
    """Check if the username already exists in the database."""
    return users_collection.count_documents({"username": username}) > 0