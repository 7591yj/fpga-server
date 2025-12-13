import uuid
import os
import sqlite3
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from auth.session_store import get_session

fpga_bp = Blueprint("fpga", __name__)

UPLOAD_DIR = os.path.expanduser("~/fpga-server/opt/fpga_app/config/bitfiles")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return filename.lower().endswith(".bit")


@fpga_bp.route("/upload", methods=["POST"])
def upload_bitfile():
    ensure_dir(UPLOAD_DIR)
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "no file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "invalid file type"}), 400

    dest = os.path.join(UPLOAD_DIR, secure_filename(file.filename))
    file.save(dest)

    if os.path.getsize(dest) < 1024:
        os.remove(dest)
        return jsonify({"error": "file too small; invalid bitstream"}), 400

    return jsonify({"status": "uploaded", "path": dest})


@fpga_bp.route("/program", methods=["POST"])
def program_fpga():
    data = request.get_json(force=True)
    bit_path = data.get("path")
    device_sn = data.get("device_sn")

    auth_token = request.cookies.get("auth_token")
    auth_info = get_session(auth_token)

    if auth_info is None:
        return jsonify({"error": "unauthorized", "token": auth_token}), 400

    user_id = auth_info.get("id")

    if not bit_path or not os.path.isfile(bit_path):
        return jsonify({"error": "bitfile not found"}), 400

    abs_path = os.path.abspath(bit_path)
    base = os.path.dirname(abs_path)
    if not abs_path.startswith(UPLOAD_DIR):
        return jsonify({"error": "unauthorized path"}), 403

    job_id = str(uuid.uuid4())

    try:
        conn = sqlite3.connect("/opt/fpga_app/config/jobs.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (id, user_id, spec, device_sn, status, ts_created)
            VALUES (?, ?, ?, ?, 'queued', CURRENT_TIMESTAMP)
            """,
            (job_id, user_id, abs_path, device_sn),
        )
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({"status": "queued", "job_id": job_id})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
