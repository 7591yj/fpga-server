import time
import logging
import sqlite3
import multiprocessing
import subprocess

DB_PATH = "/opt/fpga_app/config/jobs.db"
POLL_INTERVAL = 5
MAX_CONCURRENT_JOBS = 4  # TODO: get limit using Vivado

logger = logging.getLogger("fpga-worker")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("/var/log/fpga_app/worker.app.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)


def db():
    return sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)


def program_fpga(serial, bitfile):
    cmd = [
        "/tools/Xilinx/Vivado_Lab/2025.2/Vivado_Lab/bin/vivado_lab",
        "-mode",
        "batch",
        "-source",
        "/opt/fpga_app/scripts/program_fpga.tcl",
        f'-tclargs "{bitfile}" "{serial}"',
    ]
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def lock_device(conn, serial, job_id):
    conn.execute("BEGIN IMMEDIATE")
    conn.execute(
        """
        UPDATE devices
        SET current_job_id = ?
        WHERE serial_number = ? AND current_job_id IS NULL
        """,
        (job_id, serial),
    )
    success = conn.total_changes == 1
    if success:
        conn.commit()
    else:
        conn.rollback()
    return success


def release_device(conn, serial):
    conn.execute(
        "UPDATE devices SET current_job_id=NULL, ts_last_heartbeat=CURRENT_TIMESTAMP WHERE serial_number=?",
        (serial,),
    )
    conn.commit()


def run_job(job_id):
    conn = db()
    device_sn = None
    try:
        job = conn.execute(
            "SELECT device_sn, spec FROM jobs WHERE id=?",
            (job_id,),
        ).fetchone()
        if not job:
            raise RuntimeError(f"Job {job_id} not found.")
        device_sn, bitfile = job

        if not lock_device(conn, device_sn, job_id):
            raise RuntimeError(f"Device {device_sn} is in use.")

        conn.execute(
            """
            UPDATE jobs
            SET status='running',
                ts_started=CURRENT_TIMESTAMP,
                ts_updated=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (job_id,),
        )
        conn.commit()

        result = program_fpga(device_sn, bitfile)

        conn.execute(
            """
            UPDATE jobs
            SET status='finished',
                result=?,
                ts_finished=CURRENT_TIMESTAMP,
                ts_updated=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (result.stdout.strip(), job_id),
        )
        conn.commit()
        logger.info(f"Job {job_id} finished for device {device_sn}")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        conn.execute(
            """
            UPDATE jobs
            SET status='error',
                result=?,
                ts_updated=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (str(e), job_id),
        )
        conn.commit()

    finally:
        if device_sn:  # release only if known
            try:
                release_device(conn, device_sn)
            except Exception:
                pass
        conn.close()


def next_queued_job(conn):
    row = conn.execute(
        """
        SELECT id
        FROM jobs AS j
        WHERE j.status = 'queued'
          AND NOT EXISTS (
            SELECT 1 FROM jobs j2
            WHERE j2.device_sn = j.device_sn AND j2.status = 'running'
          )
        ORDER BY j.ts_created ASC
        LIMIT 1
        """
    ).fetchone()
    return row[0] if row else None


def main():
    logger.info("Worker started")
    procs = []
    while True:
        procs = [p for p in procs if p.is_alive()]
        if len(procs) < MAX_CONCURRENT_JOBS:
            conn = db()
            try:
                job_id = next_queued_job(conn)
                if job_id:
                    logger.info(f"Dispatching job {job_id}")
                    p = multiprocessing.Process(target=run_job, args=(job_id,))
                    p.start()
                    procs.append(p)
            except Exception as e:
                logger.error(f"Dispatcher failure: {e}")
            finally:
                conn.close()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

