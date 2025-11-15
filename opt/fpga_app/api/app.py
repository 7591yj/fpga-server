from flask import Flask
from api.auth import auth_bp
from api.jobs import jobs_bp
from api.fpga import fpga_bp
from api.utils import utils_bp
from webui import bp as webui_bp
from auth.session_store import init_sessions_table

app = Flask(__name__)
init_sessions_table()

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
app.register_blueprint(fpga_bp, url_prefix="/api/fpga")
app.register_blueprint(utils_bp, url_prefix="/api")

app.register_blueprint(webui_bp, url_prefix="/")
