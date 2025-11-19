PRAGMA foreign_keys = ON;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  ts_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- JOBS TABLE
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  spec TEXT,
  status TEXT CHECK (
    status IN ('queued', 'running', 'finished', 'cancelled', 'error')
  ),
  result TEXT,
  queue_position INTEGER,
  ts_created DATETIME DEFAULT CURRENT_TIMESTAMP,
  ts_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
  ts_started DATETIME,
  ts_finished DATETIME,
  ts_cancelled DATETIME,
  cancelled_by INTEGER REFERENCES users(id)
);

-- DEVICES TABLE
CREATE TABLE IF NOT EXISTS devices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  device_name TEXT NOT NULL,
  device_id TEXT NOT NULL UNIQUE,
  transport_type TEXT,
  product_name TEXT,
  serial_number TEXT,
  owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  current_job_id TEXT REFERENCES jobs(id),
  ts_last_heartbeat DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- JOB_SESSIONS TABLE (PTY INTERACTION)
CREATE TABLE IF NOT EXISTS job_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT REFERENCES jobs(id) ON DELETE CASCADE,
  session_token TEXT NOT NULL UNIQUE,
  ts_created DATETIME DEFAULT CURRENT_TIMESTAMP,
  ts_last_activity DATETIME
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_jobs_device_status 
  ON jobs(user_id, status);

CREATE INDEX IF NOT EXISTS idx_jobs_queue_position 
  ON jobs(user_id, queue_position);

CREATE INDEX IF NOT EXISTS idx_jobs_user 
  ON jobs(user_id);

CREATE INDEX IF NOT EXISTS idx_devices_owner 
  ON devices(owner_id);
