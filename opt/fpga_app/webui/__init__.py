from flask import Blueprint, render_template, abort
from webui.static.assets import jobs_dummy

jobs = jobs_dummy.jobs

bp = Blueprint(
    "webui",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/webui/static",
)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/stat/")
def stat():
    return render_template("stat.html", jobs=jobs)


@bp.route("/queue/")
def queue():
    return render_template("queue.html")


@bp.route("/job/")
def job():
    return render_template("job.html", jobs=jobs)


@bp.route("/job/<job_id>")
def job_detail(job_id):
    job_data = next((job for job in jobs if job["id"] == job_id), None)

    if job_data is None:
        abort(404)

    return render_template("job_detail.html", job=job_data)
