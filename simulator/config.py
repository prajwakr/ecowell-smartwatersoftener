class DeviceConfig:

    def __init__(self):

        self.min_pressure = 1.0
        self.max_tds = 400
        self.min_salt = 20

    def get(self):

        return {

            "min_pressure": self.min_pressure,
            "max_tds": self.max_tds,
            "min_salt": self.min_salt

        }

    def update(self, pressure, tds, salt):

        self.min_pressure = pressure
        self.max_tds = tds
        self.min_salt = salt