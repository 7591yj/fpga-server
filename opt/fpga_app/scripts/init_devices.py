#!/usr/bin/env python3
import sqlite3
from datetime import datetime

from jobqueue.cli_wrapper import find_devices

DB_PATH = "/opt/fpga_app/config/jobs.db"

devices = find_devices()

conn = sqlite3.connect(DB_PATH)
for dev in devices:
    # UPSERT instead of blind insert
    conn.execute(
        """
        INSERT INTO devices(
            device_name, device_id, transport_type,
            product_name, serial_number, ts_last_heartbeat
        )
        VALUES(:device_name, :device_id, :transport_type,
               :product_name, :serial_number, :ts_last_heartbeat)
        ON CONFLICT(serial_number) DO UPDATE SET
          ts_last_heartbeat = excluded.ts_last_heartbeat
        """,
        {**dev, "ts_last_heartbeat": datetime.now()},
    )
conn.commit()
conn.close()
