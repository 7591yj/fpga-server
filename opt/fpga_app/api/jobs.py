import sqlite3
from flask import Blueprint, request, jsonify

from api.auth import require_auth
from auth.session_store import get_session

jobs_bp = Blueprint("jobs", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@jobs_bp.route("/status/<job_id>", methods=["GET"])
def job_status(job_id: str):
    with db() as conn:
        conn.row_factory = sqlite3.Row  # enable name-based column access
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
                j.device_sn,
                u.username,
                d.device_name,
                d.device_id
            FROM jobs j
            LEFT JOIN users u ON j.user_id = u.id
            LEFT JOIN devices d ON j.device_sn = d.serial_number
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
            "serial_number": row["device_sn"],
        }
    )


@jobs_bp.route("/<path:device_sn>", methods=["GET"])
def jobs_status(device_sn):
    status_filter = request.args.get("status")

    with db() as conn:
        conn.row_factory = sqlite3.Row

        if status_filter:
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
                    j.device_sn,
                    u.username,
                    d.device_name,
                    d.device_id
                FROM jobs j
                LEFT JOIN users u ON j.user_id = u.id
                LEFT JOIN devices d ON j.device_sn = d.serial_number
                WHERE j.device_sn = ? AND j.status = ?
                ORDER BY j.ts_created DESC
                """,
                (device_sn, status_filter),
            )
        else:
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
                    j.device_sn,
                    u.username,
                    d.device_name,
                    d.device_id
                FROM jobs j
                LEFT JOIN users u ON j.user_id = u.id
                LEFT JOIN devices d ON j.device_sn = d.serial_number
                WHERE j.device_sn = ?
                ORDER BY j.ts_created DESC
                """,
                (device_sn,),
            )

        rows = cur.fetchall()

    return jsonify(
        {
            "device_sn": device_sn,
            "status_filter": status_filter,
            "jobs": [
                {
                    "job_id": r["id"],
                    "status": r["status"],
                    "result": r["result"],
                    "ts_updated": r["ts_updated"],
                    "ts_created": r["ts_created"],
                    "ts_started": r["ts_started"],
                    "ts_finished": r["ts_finished"],
                    "ts_cancelled": r["ts_cancelled"],
                    "user_id": r["user_id"],
                    "username": r["username"],
                    "device_id": r["device_id"],
                    "device_name": r["device_name"],
                    "serial_number": r["device_sn"],
                }
                for r in rows
            ],
        }
    )


@jobs_bp.route("/cancel/<job_id>", methods=["POST"])
@require_auth
def job_cancel(job_id: str):
    token = request.cookies.get("auth_token") or request.headers.get("X-Auth-Token")
    session_data = get_session(token)
    if not session_data:
        # This should be caught by @require_auth, but as a safeguard:
        return jsonify({"error": "unauthorized"}), 403

    user_id = session_data.get("id")

    with db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()

        if not job:
            return jsonify({"error": "Job not found"}), 404

        job_user_id = job[0]
        if job_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        # Update job status to 'cancelled' and set ts_cancelled
        cursor.execute(
            "UPDATE jobs SET status = ?, ts_cancelled = CURRENT_TIMESTAMP, ts_updated = CURRENT_TIMESTAMP WHERE id = ?",
            ("cancelled", job_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            # case might happen in a race condition if the job is deleted
            # or modified between the SELECT and UPDATE.
            return jsonify({"error": "Failed to cancel job"}), 500

    return jsonify({"message": f"Job {job_id} cancelled successfully"}), 200
