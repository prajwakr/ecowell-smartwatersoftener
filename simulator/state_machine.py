from enum import Enum


class DeviceState(Enum):
    IDLE = "IDLE"
    MONITORING = "MONITORING"
    REGENERATION_REQUIRED = "REGENERATION_REQUIRED"
    REGENERATION_RUNNING = "REGENERATION_RUNNING"
    FAULT = "FAULT"


class StateMachine:

    def __init__(self):
        self.state = DeviceState.IDLE

    def update(self, sensor):

        # Power Off
        if not sensor["power"]:

            self.state = DeviceState.IDLE

        # Regeneration Failure
        elif sensor.get("regeneration_failed", False):

            self.state = DeviceState.FAULT

        # Regeneration Running
        elif sensor["regeneration"]:

            self.state = DeviceState.REGENERATION_RUNNING

        # Low Pressure Fault
        elif sensor["pressure"] < 1:

            self.state = DeviceState.FAULT

        # High TDS
        elif sensor["tds"] > 400:

            self.state = DeviceState.REGENERATION_REQUIRED

        # Normal Monitoring
        else:

            self.state = DeviceState.MONITORING

        return self.state