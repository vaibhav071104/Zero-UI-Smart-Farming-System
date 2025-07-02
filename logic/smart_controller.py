import time
from datetime import datetime, timedelta, time as dtime
from config.config import Config
import threading

class SmartIrrigationController:
    def __init__(self, soil_sensor, weather_sensor, actuator, flow_sensor=None, pressure_sensor=None):
        self.config = Config()
        self.soil_sensor = soil_sensor
        self.weather_sensor = weather_sensor
        self.actuator = actuator
        self.flow_sensor = flow_sensor  # Optional, for future hardware
        self.pressure_sensor = pressure_sensor  # Optional, for future hardware
        
        self.last_irrigation = None
        self.irrigation_history = []
        self.override_active = False
        self.auto_mode = True
        self.irrigation_timer = None
        
        print("Smart irrigation controller initialized")
    
    def _get_season(self):
        """Determine current season (simple: May-Sep=summer, Nov-Feb=winter, else default)"""
        month = datetime.now().month
        if 5 <= month <= 9:
            return 'summer'
        elif 11 <= month or month <= 2:
            return 'winter'
        return 'default'

    def _within_time_window(self):
        now = datetime.now()
        for start, end in self.config.IRRIGATION_TIME_WINDOWS:
            if dtime(start,0) <= now.time() <= dtime(end,0):
                return True
        return False

    def _is_day_allowed(self):
        return datetime.now().weekday() in self.config.IRRIGATION_DAYS_ALLOWED

    def _seasonal_adjust(self, key, default):
        season = self._get_season()
        return self.config.SEASONAL_ADJUSTMENT.get(season, {}).get(key, default)

    def _check_flow_rate(self):
        # Stub: Replace with real sensor reading
        if self.flow_sensor:
            flow = self.flow_sensor.get_flow_rate()
        else:
            flow = 3.0  # Simulated normal
        return flow

    def _check_pressure(self):
        # Stub: Replace with real sensor reading
        if self.pressure_sensor:
            pressure = self.pressure_sensor.get_pressure()
        else:
            pressure = 2.0  # Simulated normal
        return pressure

    def should_irrigate_automatically(self):
        """Determine if automatic irrigation should start"""
        try:
            soil_moisture = self.soil_sensor.get_value()
            weather = self.weather_sensor.get_weather()
            rainfall_prob = self.weather_sensor.get_rainfall_probability()
            temp = weather['temperature']
            humidity = weather['humidity']
            wind_speed = weather.get('wind_speed', 0)
            pressure = self._check_pressure()
            flow = self._check_flow_rate()
            # --- Safety: Flow/Pressure ---
            if flow < self.config.MIN_FLOW_RATE_LPM:
                return False, f"Flow too low ({flow} L/min): possible blockage"
            if not (self.config.PRESSURE_MIN_BAR <= pressure <= self.config.PRESSURE_MAX_BAR):
                return False, f"Pressure out of range ({pressure} bar)"
            # --- Time/Day/Seasonal ---
            if not self._within_time_window():
                return False, "Not within allowed irrigation time window"
            if not self._is_day_allowed():
                return False, "Irrigation not allowed today (schedule)"
            # --- Seasonal adjustment ---
            moisture_low = self._seasonal_adjust('MOISTURE_LOW_THRESHOLD', self.config.MOISTURE_LOW_THRESHOLD)
            # --- Weather/Env ---
            if rainfall_prob > 70:
                return False, f"Rain expected ({rainfall_prob:.0f}% probability)"
            if soil_moisture >= moisture_low:
                return False, f"Soil moisture adequate ({soil_moisture}%)"
            if temp < 5:
                return False, f"Too cold for irrigation ({temp}C)"
            if temp > 40:
                return False, f"Too hot for irrigation ({temp}C)"
            if temp > self.config.TEMP_TRIGGER_C:
                return True, f"High temp trigger: {temp}C"
            if humidity > self.config.HUMIDITY_COMPENSATION:
                return False, f"Humidity too high ({humidity}%), reduce irrigation"
            if wind_speed > self.config.WIND_SPEED_MAX_MPS:
                return False, f"Wind too high ({wind_speed} m/s), pause to reduce evaporation"
            # --- Min interval ---
            if self.last_irrigation:
                time_since_last = datetime.now() - self.last_irrigation
                min_interval = timedelta(seconds=self.config.MIN_IRRIGATION_INTERVAL)
                if time_since_last < min_interval:
                    remaining = min_interval - time_since_last
                    return False, f"Too soon (wait {remaining.seconds//60} minutes)"
            if self.actuator.is_on():
                return False, "Irrigation already active"
            if not self.auto_mode:
                return False, "Auto mode disabled"
            return True, f"Soil dry ({soil_moisture}%), good weather conditions"
            
        except Exception as e:
            print(f"Error in irrigation logic: {e}")
            return False, "System error"
    
    def start_automatic_irrigation(self):
        """Start automatic irrigation if conditions are met"""
        # Block auto irrigation if manual override is active
        if self.override_active:
            print("Auto irrigation blocked: manual override is active.")
            return False

        should_irrigate, reason = self.should_irrigate_automatically()
        if should_irrigate:
            if self.actuator.turn_on():
                self.last_irrigation = datetime.now()
                self._log_irrigation_event("AUTO_START", reason)
                print(f"Auto irrigation started: {reason}")
                # --- Max duration safety timer ---
                max_duration = self._seasonal_adjust('MAX_IRRIGATION_DURATION_MIN', self.config.MAX_IRRIGATION_DURATION_MIN)
                if not isinstance(max_duration, (int, float)) or max_duration is None:
                    max_duration = int(self.config.MAX_IRRIGATION_DURATION_MIN)
                if self.irrigation_timer:
                    self.irrigation_timer.cancel()
                self.irrigation_timer = threading.Timer(max_duration*60, self._auto_stop_due_to_timeout)
                self.irrigation_timer.start()
                return True
        else:
            print(f"Auto irrigation skipped: {reason}")
        return False
    
    def stop_irrigation(self, reason="Manual stop"):
        """Stop irrigation"""
        if self.actuator.turn_off():
            self._log_irrigation_event("STOP", reason)
            return True
        return False
    
    def _log_irrigation_event(self, event_type, reason):
        """Log irrigation events"""
        event = {
            'timestamp': datetime.now(),
            'event': event_type,
            'reason': reason,
            'soil_moisture': self.soil_sensor.get_value(),
            'weather': self.weather_sensor.get_weather()
        }
        
        self.irrigation_history.append(event)
        
        if len(self.irrigation_history) > 100:
            self.irrigation_history = self.irrigation_history[-100:]
    
    def get_system_status(self):
        """Get comprehensive system status"""
        return {
            'irrigation_active': self.actuator.is_on(),
            'auto_mode': self.auto_mode,
            'override_active': self.override_active,
            'soil_moisture': self.soil_sensor.get_value(),
            'soil_status': self.soil_sensor.get_status(),
            'weather': self.weather_sensor.get_weather(),
            'rainfall_probability': self.weather_sensor.get_rainfall_probability(),
            'last_irrigation': self.last_irrigation.isoformat() if self.last_irrigation else None,
            'actuator_status': self.actuator.get_status(),
            'recent_events': self.irrigation_history[-5:] if self.irrigation_history else []
        }
    
    def set_auto_mode(self, enabled):
        """Enable or disable automatic mode"""
        self.auto_mode = enabled
        print(f"Auto mode: {'enabled' if enabled else 'disabled'}")

    def _auto_stop_due_to_timeout(self):
        if self.actuator.is_on():
            self.actuator.turn_off()
            self._log_irrigation_event("TIMEOUT_STOP", "Max irrigation duration reached (safety timeout)")
            print("Irrigation stopped: max duration safety timeout")

    def manual_start_irrigation(self, reason="Manual start override"):
        """Unconditionally start irrigation (manual override, idempotent)"""
        if not self.actuator.is_on():
            self.actuator.turn_on()
            self.last_irrigation = datetime.now()
            self._log_irrigation_event("MANUAL_START", reason)
            print(f"Manual irrigation started: {reason}")
        else:
            # Still log and print for clarity
            self._log_irrigation_event("MANUAL_START", reason + " (already running)")
            print(f"Manual irrigation started: {reason} (already running)")
        # Start max duration safety timer
        max_duration = self._seasonal_adjust('MAX_IRRIGATION_DURATION_MIN', self.config.MAX_IRRIGATION_DURATION_MIN)
        if not isinstance(max_duration, (int, float)) or max_duration is None:
            max_duration = int(self.config.MAX_IRRIGATION_DURATION_MIN)
        if self.irrigation_timer:
            self.irrigation_timer.cancel()
        self.irrigation_timer = threading.Timer(max_duration*60, self._auto_stop_due_to_timeout)
        self.irrigation_timer.start()
        return True

    def manual_stop_irrigation(self, reason="Manual stop override"):
        """Unconditionally stop irrigation (manual override, idempotent)"""
        if self.actuator.is_on():
            self.actuator.turn_off()
            self._log_irrigation_event("MANUAL_STOP", reason)
            print(f"Manual irrigation stopped: {reason}")
        else:
            # Still log and print for clarity
            self._log_irrigation_event("MANUAL_STOP", reason + " (already stopped)")
            print(f"Manual irrigation stopped: {reason} (already stopped)")
        if self.irrigation_timer:
            self.irrigation_timer.cancel()
        return True