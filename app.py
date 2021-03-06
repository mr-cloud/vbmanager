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


@app.route('/scale-in')
def scale_in():
    return jsonify(vb.shrink_VM())

@app.route('/machines-stats')
def machines_stats():
    return jsonify(vb.machines_stats())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
