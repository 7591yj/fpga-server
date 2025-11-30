from functools import wraps
import secrets
import bcrypt
import json
import requests

from flask import (
    Blueprint,
    render_template,
    abort,
    request,
    make_response,
    redirect,
    url_for,
    jsonify,
)
from webui.static.assets import jobs_dummy
from api.auth import db
from auth.session_store import get_session, save_session, delete_session

jobs_raw = json.loads(jobs_dummy.jobs)["jobs"]

jobs = []
for j in jobs_raw:
    spec = json.loads(j["spec"]) if j["spec"] else {}
    jobs.append(
        {
            "id": j["id"],
            "name": spec.get("name"),
            "status": j["status"],
            "user": j["user_id"],
            "time": j["ts_created"],
        }
    )


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
        "stat.html", device=device_data, serial_number=device_sn, jobs=jobs
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

    if not device_data:
        r = requests.get("http://127.0.0.1:8000/api/devices")
        if not r.ok:
            return jsonify({"error": "Device API unreachable"}), 503
        devices = r.json()
        if devices:
            device_data = devices[0]
            device_sn = device_data.get("serial_number")
        else:
            return jsonify({"error": "No devices available"}), 404

    return jsonify({"device": device_data, "jobs": jobs})


@bp.route("/queue/")
@ui_login_required
def queue():
    return render_template("queue.html")


@bp.route("/job/")
@ui_login_required
def job():
    return render_template("job.html", jobs=jobs)


@bp.route("/job/<job_id>")
@ui_login_required
def job_detail(job_id):
    job_data = next((job for job in jobs if job["id"] == job_id), None)

    if job_data is None:
        abort(404)

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
