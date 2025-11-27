import sqlite3
from flask import Blueprint, request, jsonify

stat_bp = Blueprint("stats", __name__)

DB_PATH = "/opt/fpga_app/config/jobs.db"


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@stat_bp.route("/devices", methods=["POST"])
def renew_devices():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid json"}), 400

    device_name = data.get("device_name", "unknown")
    device_id = data.get("device_id", "unknown")
    transport_type = data.get("transport_type", "unknown")
    product_name = data.get("product_name", "unknown")
    owner_id = data.get("owner_id", "anonymous")
    serial_number = data.get("serial_number", "unknown")

    with db() as conn:
        conn.execute(
            """
            INSERT INTO devices 
                (device_name, device_id, transport_type, product_name, owner_id, serial_number) 
            VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (
                device_name,
                device_id,
                transport_type,
                product_name,
                owner_id,
                serial_number,
            ),
        )
        conn.commit()

    return jsonify({"device_name": device_name, "serial": serial_number})


@stat_bp.route("/devices/<path:serial_number>", methods=["GET"])
def job_status(serial_number: str):
    with db() as conn:
        cur = conn.execute(
            """
            SELECT device_name, device_id, transport_type, product_name, owner_id, serial_number 
            FROM devices WHERE serial_number=?
            """,
            (serial_number,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "device not found"}), 404

    return jsonify(
        {
            "device_name": row[0],
            "device_id": row[1],
            "transport_type": row[2],
            "product_name": row[3],
            "owner_id": row[4],
            "serial_number": row[5],
        }
    )
