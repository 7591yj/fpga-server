from functools import wraps
import secrets
import bcrypt
import requests

from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    jsonify,
)
from api.auth import db
from auth.session_store import get_session, save_session, delete_session


def ui_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not get_session(token):
            return redirect(url_for("webui.login"))
        return f(*args, **kwargs)

    return wrapper


bp = Blueprint(
    "webui",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/webui/static",
)


@bp.context_processor
def inject_user():
    token = request.cookies.get("auth_token")
    username = None
    if token:
        session_data = get_session(token)
        if session_data:
            username = session_data.get("user")
    return dict(username=username)


@bp.route("/")
@ui_login_required
def index():
    return render_template("index.html")


@bp.route("/stat/")
@ui_login_required
def stat():
    device_sn = request.args.get("device")
    device_data = None
    if device_sn:
        r = requests.get(f"http://127.0.0.1:8000/api/devices/{device_sn}")
        if r.ok:
            device_data = r.json()

    if not device_data:
        all_devices_resp = requests.get("http://127.0.0.1:8000/api/devices")
        if all_devices_resp.ok:
            devices = all_devices_resp.json()
            device_data = devices[0] if devices else None
            if device_data:
                device_sn = device_data.get("serial_number")

    if not device_data:
        device_data = {
            "device_name": "No devices available",
            "device_id": None,
            "transport_type": None,
            "product_name": None,
            "serial_number": None,
            "current_job_id": None,
            "ts_last_heartbeat": None,
            "created_at": None,
        }
        return render_template(
            "stat.html", device=device_data, serial_number=None, jobs=[]
        )

    # request queued jobs for that device
    jobs_data = []
    jobs_resp = requests.get(f"http://127.0.0.1:8000/api/jobs/{device_sn}")
    if jobs_resp.ok:
        jobs_raw = jobs_resp.json()
        # Expect structure: {"device_sn": ..., "jobs": [...]}
        all_jobs = jobs_raw.get("jobs", [])
        jobs_data = [j for j in all_jobs if j.get("status") == "queued"]

    return render_template(
        "stat.html", device=device_data, serial_number=device_sn, jobs=jobs_data
    )


@bp.route("/stat/data")
@ui_login_required
def stat_data():
    device_sn = request.args.get("device")
    device_data = None

    if device_sn:
        r = requests.get(f"http://127.0.0.1:8000/api/devices/{device_sn}")
        if r.ok:
            device_data = r.json()

    # fallback to first available device
    if not device_data:
        r = requests.get("http://127.0.0.1:8000/api/devices")
        if not r.ok:
            return jsonify({"error": "Device API unreachable"}), 503
        devices = r.json()
        if not devices:
            return jsonify({"error": "No devices available"}), 404
        device_data = devices[0]
        device_sn = device_data.get("serial_number")

    # fetch jobs for the selected device
    jobs_data = []
    jobs_resp = requests.get(f"http://127.0.0.1:8000/api/jobs/{device_sn}")
    if jobs_resp.ok:
        jobs_raw = jobs_resp.json()
        # Expect structure: {"device_sn": ..., "jobs": [...]}
        all_jobs = jobs_raw.get("jobs", [])
        jobs_data = [j for j in all_jobs if isinstance(j, dict)]

    return jsonify({"device": device_data, "jobs": jobs_data})


@bp.route("/queue/")
@ui_login_required
def queue():
    return render_template("queue.html")


@bp.route("/job/")
@ui_login_required
def job():
    device_sn = request.args.get("device")
    jobs_data = []

    if device_sn:
        r = requests.get(f"http://127.0.0.1:8000/api/jobs/{device_sn}")
        if not r.ok:
            return jsonify({"error": "Device job API unreachable"}), 503

        jobs_data_raw = r.json()
        # Expect dict: {"device_sn": ..., "jobs": [...], "message": ...}
        jobs_data = jobs_data_raw.get("jobs", [])
    else:
        r = requests.get("http://127.0.0.1:8000/api/jobs")
        if not r.ok:
            return jsonify({"error": "Job API unreachable"}), 503

        # Expect list of all jobs
        jobs_data_raw = r.json()
        if isinstance(jobs_data_raw, list):
            jobs_data = sorted(
                jobs_data_raw, key=lambda x: x["ts_created"], reverse=True
            )

    return render_template("job.html", jobs=jobs_data)


@bp.route("/job/<job_id>")
@ui_login_required
def job_detail(job_id):
    r = requests.get(f"http://127.0.0.1:8000/api/jobs/status/{job_id}")
    if not r.ok:
        return jsonify({"error": "Job API unreachable"}), 503

    job_data_raw = r.json()
    # Expect dict: {"job_id: ..., "status": ..., ...}
    job_data = job_data_raw if isinstance(job_data_raw, dict) else None

    if not job_data:
        return jsonify({"error": f"Job {job_id} not found"}), 404

    return render_template("job_detail.html", job=job_data)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with db() as conn:
            row = conn.execute(
                "SELECT password_hash, id FROM users WHERE username=?", (username,)
            ).fetchone()

        if not row or not bcrypt.checkpw(password.encode(), row[0]):
            return render_template("login.html", error="Invalid username or password")

        token = secrets.token_hex(32)
        user_id = row[1]
        save_session(token, username, user_id)

        # obtain first available device
        default_sn = None
        try:
            r = requests.get("http://127.0.0.1:8000/api/devices", timeout=2)
            if r.ok:
                devices = r.json()
                if devices:
                    default_sn = devices[0].get("serial_number")
        except Exception:
            default_sn = None

        # build redirect URL
        if default_sn:
            redirect_url = url_for("webui.stat", device=default_sn)
        else:
            redirect_url = url_for("webui.stat")

        resp = make_response(redirect(redirect_url))
        resp.set_cookie("auth_token", token, httponly=True, secure=False, path="/")
        return resp

    return render_template("login.html")


@bp.route("/logout")
def logout():
    token = request.cookies.get("auth_token")
    if get_session(token):
        delete_session(token)
    resp = make_response(redirect(url_for("webui.login")))
    resp.delete_cookie("auth_token")
    return resp
