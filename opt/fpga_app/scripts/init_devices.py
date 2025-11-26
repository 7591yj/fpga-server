#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime

from queue.cli_wrapper import find_devices


DB_PATH = "/opt/fpga_app/config/jobs.db"

find_devices()
with open("targets.json") as f:
    targets = json.load(f)

conn = sqlite3.connect(DB_PATH)

for target in targets:
    conn.execute(
        """
        INSERT INTO devices (
            device_name, device_id,
            transport_type, product_name,
            serial_number, ts_last_heartbeat
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            target["device_name"],
            target["device_id"],
            target["transport_type"],
            target["product_name"],
            target["serial_number"],
            datetime.now(),
        ),
    )
    print(f"Device {target['device_id']} created.")

conn.commit()
conn.close()

print("Device initialization completed.")
