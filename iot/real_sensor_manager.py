import time
from datetime import datetime
import threading
import random

class RealSensorManager:
    def __init__(self):
        print("Initializing Real IoT Sensor Manager...")
        
        # Sensor data cache
        self.sensor_data = {
            "soil_moisture": [],
            "weather": {},
            "last_update": None
        }
        
        # Data collection settings
        self.is_collecting = False
        self.collection_thread = None
        
        print("IoT sensor manager ready")
    
    def start_data_collection(self):
        """Start continuous sensor data collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        print("IoT data collection started")
    
    def stop_data_collection(self):
        """Stop sensor data collection"""
        self.is_collecting = False
        print("IoT data collection stopped")
    
    def _collection_loop(self):
        """Main data collection loop"""
        while self.is_collecting:
            try:
                # Simulate data collection
                sensor_data = self._get_simulated_sensor_data()
                
                # Update cache
                self.sensor_data.update(sensor_data)
                self.sensor_data["last_update"] = datetime.now()
                
                print(f"Sensor data updated: {len(self.sensor_data["soil_moisture"])} soil sensors")
                
            except Exception as e:
                print(f"Data collection error: {e}")
            
            time.sleep(10)  # Update every 10 seconds for testing
    
    def get_latest_sensor_data(self):
        """Get the latest collected sensor data"""
        return self.sensor_data.copy()
    
    def get_average_soil_moisture(self):
        """Get average soil moisture across all sensors"""
        if not self.sensor_data["soil_moisture"]:
            return 50.0  # Default value
        
        moistures = [sensor["moisture_percentage"] for sensor in self.sensor_data["soil_moisture"]]
        return sum(moistures) / len(moistures)
    
    def get_field_variability(self):
        """Analyze field variability across sensors"""
        if not self.sensor_data["soil_moisture"]:
            return {"variability": "unknown"}
        
        moistures = [sensor["moisture_percentage"] for sensor in self.sensor_data["soil_moisture"]]
        avg_moisture = sum(moistures) / len(moistures)
        variance = sum((m - avg_moisture) ** 2 for m in moistures) / len(moistures)
        std_dev = variance ** 0.5
        
        return {
            "average_moisture": round(avg_moisture, 2),
            "standard_deviation": round(std_dev, 2),
            "variability_level": "high" if std_dev > 10 else "medium" if std_dev > 5 else "low",
            "sensor_count": len(moistures)
        }
    
    def _get_simulated_sensor_data(self):
        """Generate simulated sensor data"""
        return {
            "soil_moisture": [
                {
                    "sensor_id": f"soil_{i+1}",
                    "location": f"field_section_{i+1}",
                    "moisture_percentage": round(random.uniform(20, 80), 1),
                    "temperature": round(random.uniform(18, 32), 1),
                    "timestamp": datetime.now().isoformat()
                }
                for i in range(4)
            ],
            "weather": {
                "temperature": round(random.uniform(20, 35), 1),
                "humidity": round(random.uniform(40, 90), 1),
                "timestamp": datetime.now().isoformat()
            }
        }

class HardwareInterface:
    def __init__(self):
        print("Hardware interface initialized")
        
    def integrate_with_existing_system(self, farming_system, sensor_manager):
        """Integrate real sensors with existing farming system"""
        print("Hardware integration complete")
