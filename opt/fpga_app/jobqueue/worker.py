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
    proc = None
    try:
        # Fetch job details, including status to check if it's still queued
        job_details = conn.execute(
            "SELECT device_sn, spec, status FROM jobs WHERE id=?", (job_id,)
        ).fetchone()

        if not job_details:
            raise RuntimeError(f"Job {job_id} not found in database.")

        device_sn, bitfile, status = job_details

        if status != "queued":
            logger.info(f"Job {job_id} status is '{status}', not 'queued'. Skipping.")
            return

        # Attempt to lock the device for this job
        if not lock_device(conn, device_sn, job_id):
            logger.warning(f"Device {device_sn} is busy. Job {job_id} will be retried.")
            return

        # With lock acquired, atomically update status to 'running'
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE jobs
            SET status='running', ts_started=CURRENT_TIMESTAMP, ts_updated=CURRENT_TIMESTAMP
            WHERE id=? AND status='queued'
            """,
            (job_id,),
        )
        if cursor.rowcount == 0:
            logger.info(
                f"Job {job_id} was cancelled just before starting. Releasing device."
            )
            release_device(conn, device_sn)
            conn.commit()
            return
        conn.commit()

        logger.info(
            f"Starting hardware programming for job {job_id} on device {device_sn}."
        )
        cmd = [
            "/tools/Xilinx/Vivado_Lab/2025.2/Vivado_Lab/bin/vivado_lab",
            "-mode",
            "batch",
            "-source",
            "/opt/fpga_app/scripts/program_fpga.tcl",
            "-tclargs",
            bitfile,
            device_sn,
        ]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Monitor subprocess and check for cancellation
        while proc.poll() is None:
            time.sleep(1)  # Check for cancellation every second
            current_status = conn.execute(
                "SELECT status FROM jobs WHERE id=?", (job_id,)
            ).fetchone()[0]
            if current_status == "cancelled":
                logger.info(
                    f"Cancellation request received for job {job_id}. Terminating process."
                )
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(
                        f"Process for job {job_id} did not terminate gracefully, killing."
                    )
                    proc.kill()
                return

        stdout, stderr = proc.communicate()
        result_output = stdout.strip() or stderr.strip()

        if proc.returncode == 0:
            logger.info(f"Job {job_id} completed successfully.")
            conn.execute(
                """
                UPDATE jobs
                SET status='finished', result=?, ts_finished=CURRENT_TIMESTAMP, ts_updated=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (result_output, job_id),
            )
            conn.commit()
        else:
            logger.error(f"Job {job_id} failed with exit code {proc.returncode}.")
            raise RuntimeError(f"FPGA programming failed: {result_output}")

    except Exception as e:
        logger.error(f"An error occurred while processing job {job_id}: {e}")
        # Avoid overwriting a 'cancelled' or 'finished' status with 'error'
        conn.execute(
            """
            UPDATE jobs
            SET status='error', result=?, ts_updated=CURRENT_TIMESTAMP
            WHERE id=? AND status NOT IN ('cancelled', 'finished')
            """,
            (str(e), job_id),
        )
        conn.commit()
    finally:
        # Ensure the device is always released
        if device_sn:
            try:
                release_device(conn, device_sn)
                logger.info(f"Device {device_sn} released after job {job_id}.")
            except Exception as e:
                logger.error(
                    f"Fatal: Failed to release device {device_sn} for job {job_id}: {e}"
                )
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
