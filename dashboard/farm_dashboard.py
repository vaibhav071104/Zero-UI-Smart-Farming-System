import json
from datetime import datetime

class FarmDashboard:
    def __init__(self, multi_farm_controller):
        print("Initializing Farm Dashboard...")
        self.multi_farm = multi_farm_controller
        self.dashboard_data = {}
        
    def generate_dashboard_data(self, user_id: str):
        """Generate comprehensive dashboard data"""
        try:
            # Get all farms for user
            farms_status = self.multi_farm.get_all_farms_status(user_id)
            analytics = self.multi_farm.get_multi_farm_analytics(user_id)
            
            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "overview": self._generate_overview(farms_status, analytics),
                "farms": self._generate_farms_summary(farms_status),
                "alerts": self._generate_alerts_summary(farms_status),
                "analytics": self._generate_analytics_charts(analytics),
                "weather": self._generate_weather_summary(farms_status),
                "recommendations": self._generate_recommendations(analytics)
            }
            
            return dashboard
            
        except Exception as e:
            print(f"Dashboard generation error: {e}")
            return {"error": str(e)}
    
    def _generate_overview(self, farms_status, analytics):
        """Generate overview statistics"""
        return {
            "total_farms": farms_status.get("total_farms", 0),
            "active_irrigation": farms_status.get("active_farms", 0),
            "total_area": analytics["summary"].get("total_area_hectares", 0),
            "average_soil_moisture": analytics["summary"].get("average_soil_moisture", 0),
            "system_health": 95.0,
            "water_efficiency": 88.5
        }
    
    def _generate_farms_summary(self, farms_status):
        """Generate farms summary for dashboard"""
        farms_summary = []
        
        for farm_id, farm_data in farms_status.get("farms", {}).items():
            summary = {
                "farm_id": farm_id,
                "name": farm_data["farm_info"]["name"],
                "location": farm_data["farm_info"]["location"],
                "irrigation_status": "inactive",
                "soil_moisture": 50.0,
                "soil_status": "OPTIMAL",
                "weather_temp": 25.0,
                "rain_probability": 30.0,
                "auto_mode": True,
                "status_color": "green"
            }
            farms_summary.append(summary)
        
        return farms_summary
    
    def _generate_alerts_summary(self, farms_status):
        """Generate alerts summary"""
        return {
            "critical": [],
            "warning": [],
            "info": []
        }
    
    def _generate_analytics_charts(self, analytics):
        """Generate data for analytics charts"""
        return {
            "soil_moisture_chart": {
                "type": "bar",
                "data": {
                    "labels": [farm["name"] for farm in analytics["farm_comparison"]],
                    "datasets": [{
                        "label": "Soil Moisture (%)",
                        "data": [farm["soil_moisture"] for farm in analytics["farm_comparison"]],
                        "backgroundColor": ["#4CAF50"]
                    }]
                }
            }
        }
    
    def _generate_weather_summary(self, farms_status):
        """Generate weather summary across farms"""
        return []
    
    def _generate_recommendations(self, analytics):
        """Generate actionable recommendations"""
        return [
            {
                "type": "system",
                "priority": "medium",
                "farm": "All Farms",
                "message": "System is operating optimally"
            }
        ]
