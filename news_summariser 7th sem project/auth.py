import json
import os
import streamlit as st
import hashlib

USER_FILE = "users.json"

# Load users from file
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

# Save users to file
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Password hashing for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registration logic
def register_user(email, password):
    users = load_users()
    if email in users:
        return False
    users[email] = hash_password(password)
    save_users(users)
    return True

# Login validation
def authenticate_user(email, password):
    users = load_users()
    hashed = hash_password(password)
    return users.get(email) == hashed
