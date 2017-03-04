from flask import Flask
from flask import jsonify
from vbmanager import VBManager

app = Flask(__name__)

vb = VBManager()


@app.route("/")
def list_services():
    return jsonify(vb.list_all())


@app.route("/scale-out")
def scale_out():
    return jsonify(vb.create_config_VM())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
