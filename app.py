from flask import Flask, jsonify, render_template, send_file

from simulator.sensor_simulator import SensorSimulator
from simulator.regeneration import Regeneration
from simulator.export_csv import CSVExporter
from simulator.config import DeviceConfig

app = Flask(__name__)

simulator = SensorSimulator()
regeneration = Regeneration(simulator)

db = simulator.database
csv_exporter = CSVExporter(db)
config = DeviceConfig()
@app.route("/config")
def get_config():

    return jsonify(config.get())


@app.route("/config", methods=["POST"])
def update_config():

    from flask import request

    data = request.json

    config.update(

        float(data["min_pressure"]),
        int(data["max_tds"]),
        int(data["min_salt"])

    )

    return jsonify({

        "message": "Configuration Updated"

    })

@app.route("/")
def home():
    return "Smart Water Softener API Running"


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/sensor-data")
def sensor_data():
    return jsonify(simulator.update())


@app.route("/history")
def history():
    return jsonify(db.get_recent_sensor_logs())


@app.route("/activity")
def activity():
    return jsonify(db.get_activity_logs())


@app.route("/clear-history", methods=["POST"])
def clear_history():

    db.clear_sensor_logs()

    return jsonify({
        "message": "Sensor History Cleared"
    })


@app.route("/clear-activity", methods=["POST"])
def clear_activity():

    db.clear_activity_logs()

    simulator.logs.clear()

    return jsonify({
        "message": "Activity Logs Cleared"
    })


@app.route("/start-regeneration", methods=["POST"])
def start_regeneration():

    if simulator.regeneration:
        return jsonify({
            "message": "Regeneration already running."
        })

    if simulator.pressure < 1:
        return jsonify({
            "message": "Cannot start. Low Pressure."
        })

    if simulator.salt < 20:
        return jsonify({
            "message": "Cannot start. Low Salt Level."
        })

    regeneration.start()

    simulator.add_log("Regeneration Started")

    return jsonify({
        "message": "Regeneration Started Successfully."
    })


@app.route("/toggle-power", methods=["POST"])
def toggle_power():

    simulator.toggle_power()

    return jsonify({
        "message": "Power Toggled",
        "power": simulator.power
    })


@app.route("/refill-salt", methods=["POST"])
def refill_salt():

    simulator.refill_salt()

    return jsonify({
        "message": "Salt Tank Refilled Successfully."
    })


@app.route("/export-csv")
def export_csv():

    filename = csv_exporter.export_sensor_logs()

    return send_file(
        filename,
        as_attachment=True
    )
@app.route("/reset-fault", methods=["POST"])
def reset_fault():

    simulator.regeneration_failed = False
    simulator.regeneration = False

    simulator.add_log("🔧 Fault Reset By Operator")

    return jsonify({
        "message": "Fault Reset Successfully"
    })
@app.route("/stats")
def stats():

    return jsonify(

        db.get_dashboard_stats()

    )

if __name__ == "__main__":

    app.run(
        debug=True,
        threaded=True,
        use_reloader=False
    )