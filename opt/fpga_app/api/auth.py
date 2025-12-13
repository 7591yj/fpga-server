from typing import TypeVar, Callable, Any
import bcrypt
import sqlite3
from flask import Blueprint, request, jsonify
import secrets
from functools import wraps
from auth.session_store import get_session, save_session


auth_bp = Blueprint("auth", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


F = TypeVar("F", bound=Callable[..., Any])


def require_auth(f: F) -> F:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        token = request.cookies.get("auth_token") or request.headers.get("X-Auth-Token")
        if not token or not get_session(token):
            return jsonify({"error": "unauthorized"}), 403
        return f(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "missing credentials"}), 400

    with db() as conn:
        cur = conn.execute(
            "SELECT password_hash, id FROM users WHERE username=?", (username,)
        )
        row = cur.fetchone()

    if not row or not bcrypt.checkpw(password.encode(), row[0]):
        return jsonify({"error": "invalid login"}), 401

    token = secrets.token_hex(32)
    id = row[1]
    save_session(token, username, id)
    return jsonify({"status": "ok", "token": token, "id": id})
