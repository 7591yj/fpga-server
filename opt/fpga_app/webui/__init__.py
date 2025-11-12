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


@bp.route("/result/")
def result():
    return render_template("result.html")
