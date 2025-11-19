import uuid
import sqlite3
import json
from flask import Blueprint, request, jsonify

jobs_bp = Blueprint("jobs", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@jobs_bp.route("/submit", methods=["POST"])
def submit_job():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid json"}), 400

    job_id = str(uuid.uuid4())
    user_id = data.get("user_id")
    device_id = data.get("device_id")
    spec = json.dumps(data.get("job", {}))

    if not user_id or not device_id:
        return jsonify({"error": "user_id and device_id are required"}), 400

    with db() as conn:
        # Validate foreign keys
        user_exists = conn.execute(
            "SELECT id FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        device_exists = conn.execute(
            "SELECT device_id FROM devices WHERE device_id = ?", (device_id,)
        ).fetchone()

        if not user_exists or not device_exists:
            return jsonify({"error": "invalid user_id or device_id"}), 400

        conn.execute(
            """
            INSERT INTO jobs (
                id, user_id, device_id, spec, status, queue_position
            )
            VALUES (?, ?, ?, ?, 'queued',
                    COALESCE((SELECT MAX(queue_position) + 1 FROM jobs WHERE device_id = ?), 1))
            """,
            (job_id, user_id, device_id, spec, device_id),
        )

        conn.commit()

    return jsonify({"job_id": job_id, "status": "queued"})


@jobs_bp.route("/status/<job_id>", methods=["GET"])
def job_status(job_id: str):
    with db() as conn:
        cur = conn.execute(
            """
            SELECT 
                j.id,
                j.status,
                j.result,
                j.ts_updated,
                j.ts_created,
                j.ts_started,
                j.ts_finished,
                j.ts_cancelled,
                j.user_id,
                j.device_id,
                u.username,
                d.device_name,
                d.serial_number
            FROM jobs j
            LEFT JOIN users u ON j.user_id = u.id
            LEFT JOIN devices d ON j.device_id = d.device_id
            WHERE j.id = ?
            """,
            (job_id,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "job not found"}), 404

    return jsonify(
        {
            "job_id": row["id"],
            "status": row["status"],
            "result": row["result"],
            "ts_updated": row["ts_updated"],
            "ts_created": row["ts_created"],
            "ts_started": row["ts_started"],
            "ts_finished": row["ts_finished"],
            "ts_cancelled": row["ts_cancelled"],
            "user_id": row["user_id"],
            "username": row["username"],
            "device_id": row["device_id"],
            "device_name": row["device_name"],
            "serial_number": row["serial_number"],
        }
    )
