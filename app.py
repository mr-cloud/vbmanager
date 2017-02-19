from flask import Flask
from flask import jsonify
from vbmanager import VBManager as vbm
from vbmanager import services

app = Flask(__name__)
app.config["VBMANAGER_URL_PREFIX"] = "/vbmanager"
app.config["VBMANAGER_SITEURL"] = "http://localhost:8000"
app.config["VBMANAGER_SITENAME"] = "My Site"

vb = vbm()


@app.route("/")
def list_services():
    return jsonify(vb.list_all())


@app.route("/scale-out")
def scale_out():
    return jsonify(vb.create_config_VM())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=True)
