import random

class SoilMoistureSensor:
    def __init__(self):
        print("Soil moisture sensor initialized (simulated)")

    def get_value(self):
        # Simulate real-time changing value
        return random.uniform(20, 80)

    def get_status(self):
        value = self.get_value()
        if value < 30:
            return "dry"
        elif value > 70:
            return "wet"
        else:
            return "optimal"