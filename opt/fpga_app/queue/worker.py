import sqlite3
import time
import multiprocessing
import logging

logger = logging.getLogger("fpga-server_logger")
logger.setLevel(logging.DEBUG)

log_file_path = "/var/log/fpga_app/api.out.log"
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

DB_PATH = "/opt/fpga_app/config/jobs.db"
MAX_CONCURRENT_JOBS = 4  # TODO: get limit using djtgcfg
POLL_INTERVAL = 5  # seconds


def db():
    return sqlite3.connect(DB_PATH)


def run_job(job_id):
    """
    This function is run in a separate process
    """
    logging.info(f"Starting job: {job_id}")
    conn = db()
    try:
        conn.execute(
            "UPDATE jobs SET status='running', ts_updated=CURRENT_TIMESTAMP WHERE id=?",
            (job_id,),
        )
        conn.commit()

        # TODO: remove mock job

        # --- Start of Mock Job ---
        logging.info(f"Processing job: {job_id}")
        time.sleep(10)  # Simulate a 10-second job
        result = "done"
        # --- End of Mock Job ---

        conn.execute(
            "UPDATE jobs SET status='completed', result=?, ts_updated=CURRENT_TIMESTAMP WHERE id=?",
            (result, job_id),
        )
        conn.commit()
        logging.info(f"Finished job: {job_id}")

    except Exception as e:
        logging.error(f"Error processing job {job_id}: {e}")
        # Update job status to 'failed'
        conn.execute(
            "UPDATE jobs SET status='failed', result=?, ts_updated=CURRENT_TIMESTAMP WHERE id=?",
            (str(e), job_id),
        )
        conn.commit()
    finally:
        conn.close()


def main():
    """
    Polls the database for pending jobs and dispatches them to worker processes
    """
    logging.info("Starting worker process...")
    active_processes = []

    while True:
        conn = db()
        try:
            # Clean up finished processes from the active list
            active_processes = [p for p in active_processes if p.is_alive()]

            # Get the number of currently running jobs
            running_jobs_count = len(active_processes)
            logging.info(f"{running_jobs_count} jobs currently running.")

            if running_jobs_count < MAX_CONCURRENT_JOBS:
                # Fetch the oldest pending job (FIFO)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM jobs WHERE status='pending' ORDER BY ts_created ASC LIMIT 1"
                )
                job = cursor.fetchone()

                if job:
                    job_id = job[0]
                    logging.info(f"Found pending job: {job_id}. Dispatching...")

                    # Spawn a new process to run the job
                    process = multiprocessing.Process(target=run_job, args=(job_id,))
                    process.start()
                    active_processes.append(process)

            else:
                logging.info("Max concurrent jobs reached. Waiting...")

        except Exception as e:
            logging.error(f"An error occurred in the main worker loop: {e}")
        finally:
            conn.close()

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
