#!/usr/bin/env python3
import bcrypt
import sqlite3

DB_PATH = "/opt/fpga_app/config/jobs.db"

username = input("username: ").strip()
password = input("password: ").strip()
pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

conn = sqlite3.connect(DB_PATH)
conn.execute(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash)
)
conn.commit()
conn.close()

print(f"User {username} created.")
