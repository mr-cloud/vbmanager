from flask import Flask
from flask import jsonify
from vbmanager import VBManager as vbm
from vbmanager import services

app = Flask(__name__)
app.config["VBMANAGER_URL_PREFIX"] = "/vbmanager"
app.config["VBMANAGER_SITEURL"] = "http://localhost:8000"
app.config["VBMANAGER_SITENAME"] = "My Site"

vb = vbm(services)


@app.route("/")
def list_services():
    return jsonify(vb.list_all())


@app.route("/scale-out")
def scale_out():
    vb.create_config_VM()