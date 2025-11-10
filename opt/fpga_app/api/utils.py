from flask import Blueprint

utils_bp = Blueprint("utils", __name__)


@utils_bp.route("/health")
def index():
    return {"status": "ok", "message": "fpga-server.api is running."}
