from flask import Blueprint, render_template

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
    return render_template("stat.html")


@bp.route("/queue/")
def queue():
    return render_template("queue.html")


@bp.route("/job/")
def result():
    return render_template("job.html")


@bp.route("/job/<job_id>")
def result_job(job_id):
    # TODO: remove job data and get actual data retrieval
    # pretend data retrieval
    job_data = {"id": job_id, "status": "completed", "score": 92}
    return render_template("job_detail.html", job=job_data)
