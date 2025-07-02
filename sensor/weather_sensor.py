import os
import requests

class WeatherSensor:
    def __init__(self):
        print("Weather sensor initialized (OpenWeatherMap API)")
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.city = os.getenv("WEATHER_CITY", "Delhi")
        self.units = "metric"

    def get_weather(self):
        if not self.api_key:
            print("No OpenWeatherMap API key found, using simulated data.")
            import random
            return {
                'temperature': random.uniform(20, 40),
                'humidity': random.uniform(40, 90),
                'wind_speed': random.uniform(0, 10)
            }
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units={self.units}"
            resp = requests.get(url, timeout=3)
            data = resp.json()
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        except Exception as e:
            print(f"Weather API error: {e}, using simulated data.")
            import random
            return {
                'temperature': random.uniform(20, 40),
                'humidity': random.uniform(40, 90),
                'wind_speed': random.uniform(0, 10)
            }

    def get_rainfall_probability(self):
        # Optionally implement using OpenWeatherMap forecast API
        return 0.0

    def get_rain_forecast(self, hours):
        """
        Returns True if rain is predicted in the next 'hours' hours, else False.
        Uses OpenWeatherMap 3-hour forecast API.
        """
        if not self.api_key:
            # Simulate: 20% chance of rain
            import random
            rain = random.random() < 0.2
            print(f"[Simulated] Rain forecast in next {hours}h: {rain}")
            return rain
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units={self.units}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            end_time = now + timedelta(hours=hours)
            for entry in data.get('list', []):
                forecast_time = datetime.utcfromtimestamp(entry['dt'])
                if now < forecast_time <= end_time:
                    rain = entry.get('rain', {}).get('3h', 0)
                    if rain > 0:
                        print(f"Rain predicted at {forecast_time} (amount: {rain}mm)")
                        return True
            print(f"No rain predicted in next {hours} hours.")
            return False
        except Exception as e:
            print(f"Rain forecast API error: {e}, using simulated data.")
            import random
            rain = random.random() < 0.2
            print(f"[Simulated] Rain forecast in next {hours}h: {rain}")
            return rain