from simulator.config import DeviceConfig


class AlertEngine:

    def __init__(self):

        self.config = DeviceConfig()

    def check_alerts(self, sensor):

        alerts = []

        config = self.config.get()

        if not sensor["power"]:
            alerts.append("⚠ Power Failure")

        if sensor["pressure"] < config["min_pressure"]:
            alerts.append("⚠ Low Water Pressure")

        if (
            sensor["power"]
            and sensor["pressure"] > config["min_pressure"]
            and sensor["flow"] == 0
        ):
            alerts.append("⚠ No Water Flow Detected")

        if sensor["salt"] < config["min_salt"]:
            alerts.append("⚠ Low Salt Level")

        elif sensor["salt"] < config["min_salt"] + 10:
            alerts.append("⚠ Salt Refill Recommended Soon")

        elif sensor["salt"] < config["min_salt"] + 30:
            alerts.append("ℹ Salt Level Dropping - Plan Refill")

        if sensor["tds"] > config["max_tds"]:
            alerts.append("⚠ Poor Water Quality (High TDS)")

        if sensor.get("regeneration_failed", False):
            alerts.append("❌ Regeneration Failed")

        return alerts