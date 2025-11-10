import os
import subprocess
from flask import Blueprint, request, jsonify

fpga_bp = Blueprint("fpga", __name__)

UPLOAD_DIR = "/opt/fpga_app/config/bitfiles"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return filename.lower().endswith(".bit")


@fpga_bp.route("/upload", methods=["POST"])
def upload_bitfile():
    ensure_dir(UPLOAD_DIR)
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "no file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "invalid file type"}), 400

    dest = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
    file.save(dest)

    if os.path.getsize(dest) < 1024:
        return jsonify({"error": "file too small; invalid bitstream"}), 400

    return jsonify({"status": "uploaded", "path": dest})


@fpga_bp.route("/program", methods=["POST"])
def program_fpga():
    data = request.get_json(force=True)
    bit_path = data.get("path")

    if not bit_path or not os.path.isfile(bit_path):
        return jsonify({"error": "bitfile not found"}), 400

    abs_path = os.path.abspath(bit_path)
    base = os.path.dirname(abs_path)
    if not abs_path.startswith(UPLOAD_DIR):
        return jsonify({"error": "unauthorized path"}), 403

    try:
        result = subprocess.run(
            [
                "/opt/fpga_app/scripts/program_fpga.sh",
                abs_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=120,
        )
        return jsonify({"status": "success", "output": result.stdout.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "error": e.stderr.strip()}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "error": "programming timeout"}), 504
