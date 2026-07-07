import random
from datetime import datetime

from simulator.state_machine import StateMachine
from simulator.alerts import AlertEngine
from simulator.database import Database
from simulator.config import DeviceConfig


class SensorSimulator:

    def __init__(self):
        self.config = DeviceConfig()
        self.flow = 20
        self.pressure = 2.5
        self.salt = 100.0
        self.tds = 120

        self.power = True
        self.regeneration = False
        self.regeneration_failed = False

        # Device Start Time
        self.start_time = datetime.now()

        self.logs = []

        self.state_machine = StateMachine()
        self.alert_engine = AlertEngine()
        self.database = Database()

    def add_log(self, message):

        current_time = datetime.now().strftime("%H:%M:%S")

        log = f"{current_time} - {message}"

        if len(self.logs) == 0 or self.logs[0] != log:

            self.logs.insert(0, log)
            self.database.save_log(message)

        self.logs = self.logs[:15]

    def toggle_power(self):

        self.power = not self.power

        if self.power:
            self.add_log("✅ Power Restored")
        else:
            self.add_log("❌ Power Lost")

    def refill_salt(self):

        self.salt = 100

        self.add_log("🧂 Salt Tank Refilled")

    def update(self):

        if self.power:

            # -------- Pipe Block Simulation --------

            blocked = random.randint(1, 15) == 1

            if blocked:

                self.flow = 0
                self.pressure = round(random.uniform(2.0, 4.5), 2)

                self.add_log("🚰 Pipe Blocked - No Water Flow")

            else:

                self.flow = round(random.uniform(15, 30), 2)
                self.pressure = round(random.uniform(1.5, 4.5), 2)

            # ---------------------------------------

            self.tds = random.randint(100, 450)

            # Slow salt consumption during normal usage
            self.salt = max(0, self.salt - 0.05)

            # Extra salt consumption during regeneration
            if self.regeneration:
                self.salt = max(0, self.salt - 0.5)

        else:

            self.flow = 0
            self.pressure = 0

        # -------- Device Uptime --------

        uptime = datetime.now() - self.start_time

        total_seconds = int(uptime.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # -------------------------------

        sensor = {

            "flow": self.flow,
            "pressure": self.pressure,
            "salt": round(self.salt, 1),
            "tds": self.tds,

            "power": self.power,
            "regeneration": self.regeneration,
            "regeneration_failed": self.regeneration_failed,

            "uptime": f"{hours:02}:{minutes:02}:{seconds:02}",

            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }

        state = self.state_machine.update(sensor)

        alerts = self.alert_engine.check_alerts(sensor)

        health = 100

        if sensor["pressure"] < self.config.get()["min_pressure"]:
            health -= 30

        if sensor["tds"] > self.config.get()["max_tds"]:
            health -= 20

        if sensor["salt"] < self.config.get()["min_salt"]:
            health -= 20

        if sensor["flow"] == 0 and sensor["pressure"] > self.config.get()["min_pressure"]:
            health -= 10
        if sensor["regeneration_failed"]:
            health -= 40

        for alert in alerts:
            self.add_log(alert)

        if self.regeneration:
            self.add_log("♻ Regeneration Running")

        sensor["state"] = state.value
        sensor["alerts"] = alerts
        sensor["health"] = max(0, health)
        sensor["logs"] = self.logs

        self.database.save_sensor(sensor)

        return sensor