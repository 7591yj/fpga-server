from functools import wraps
import secrets
import bcrypt

from flask import (
    Blueprint,
    render_template,
    abort,
    request,
    make_response,
    redirect,
    url_for,
)
from webui.static.assets import jobs_dummy
from api.auth import db
from auth.session_store import get_session, save_session, delete_session


jobs = jobs_dummy.jobs


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


@bp.route("/")
@ui_login_required
def index():
    return render_template("index.html")


@bp.route("/stat/")
@ui_login_required
def stat():
    return render_template("stat.html", jobs=jobs)


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
                "SELECT password_hash FROM users WHERE username=?", (username,)
            ).fetchone()

        if not row or not bcrypt.checkpw(password.encode(), row[0]):
            return render_template("login.html", error="Invalid username or password")

        token = secrets.token_hex(32)
        save_session(token, username)

        resp = make_response(redirect(url_for("webui.index")))
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
