from flask import Flask
from auth import auth_bp
from jobs import jobs_bp
from fpga import fpga_bp
from utils import utils_bp

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(jobs_bp, url_prefix="/jobs")
app.register_blueprint(fpga_bp, url_prefix="/fpga")
app.register_blueprint(utils_bp)
