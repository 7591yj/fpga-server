import uuid
import sqlite3
import json
import threading
import time
from flask import Blueprint, request, jsonify

jobs_bp = Blueprint("jobs", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# Simulated job runner
def run_job(job_id):
    with db() as conn:
        conn.execute(
            "UPDATE jobs SET status='running', ts_updated=CURRENT_TIMESTAMP WHERE id=?",
            (job_id,),
        )
        conn.commit()

    # mock computation or hardware call
    time.sleep(3)

    with db() as conn:
        conn.execute(
            "UPDATE jobs SET status='completed', result=?, ts_updated=CURRENT_TIMESTAMP WHERE id=?",
            ("done", job_id),
        )
        conn.commit()


@jobs_bp.route("/submit", methods=["POST"])
def submit_job():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid json"}), 400

    job_id = str(uuid.uuid4())
    user = data.get("user", "anonymous")
    spec = json.dumps(data.get("job", {}))

    with db() as conn:
        conn.execute(
            "INSERT INTO jobs (id, user, spec, status) VALUES (?, ?, ?, 'pending')",
            (job_id, user, spec),
        )
        conn.commit()

    threading.Thread(target=run_job, args=(job_id,), daemon=True).start()
    return jsonify({"job_id": job_id, "status": "pending"})


@jobs_bp.route("/status/<job_id>", methods=["GET"])
def job_status(job_id: str):
    with db() as conn:
        cur = conn.execute(
            "SELECT id, status, result, ts_updated FROM jobs WHERE id=?", (job_id,)
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "job not found"}), 404

    return jsonify(
        {
            "job_id": row[0],
            "status": row[1],
            "result": row[2],
            "ts_updated": row[3],
        }
    )
