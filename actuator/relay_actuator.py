class RelayActuator:
    def __init__(self):
        self.state = False
        print("Relay actuator initialized (simulated)")

    def turn_on(self):
        self.state = True
        print("Relay actuator turned ON (simulated)")
        return True

    def turn_off(self):
        self.state = False
        print("Relay actuator turned OFF (simulated)")
        return True

    def is_on(self):
        return self.state

    def get_status(self):
        return "ON" if self.state else "OFF"