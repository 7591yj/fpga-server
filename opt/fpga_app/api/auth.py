import bcrypt
import sqlite3
from flask import Blueprint, request, jsonify
import secrets
import time
from functools import wraps
from auth.session_store import get_session, save_session, delete_session


auth_bp = Blueprint("auth", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        if not get_session(token):
            return jsonify({"error": "unauthorized"}), 403
        return f(*args, **kwargs)

    return wrapper


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "missing credentials"}), 400

    with db() as conn:
        cur = conn.execute(
            "SELECT password_hash FROM users WHERE username=?", (username,)
        )
        row = cur.fetchone()

    if not row or not bcrypt.checkpw(password.encode(), row[0]):
        return jsonify({"error": "invalid login"}), 401

    token = secrets.token_hex(32)
    save_session(token, username)
    return jsonify({"status": "ok", "token": token})
