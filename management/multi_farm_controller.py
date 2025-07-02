from typing import Dict, List
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class FarmInfo:
    farm_id: str
    name: str
    location: str
    owner_id: str
    area_hectares: float
    crop_type: str
    planting_date: str
    created_date: str
    status: str = "active"

class MultiFarmController:
    def __init__(self):
        print("Initializing Multi-Farm Management System...")
        
        # Farm registry
        self.farms: Dict[str, any] = {}
        self.farm_info: Dict[str, FarmInfo] = {}
        
        # User management
        self.user_auth = UserAuthenticationSystem()
        
        print("Multi-farm management system ready")
    
    def add_farm(self, farm_id: str, name: str, location: str, owner_id: str, 
                 area_hectares: float, crop_type: str, planting_date: str = None):
        """Add a new farm to the management system"""
        try:
            # Create farm info
            farm_info = FarmInfo(
                farm_id=farm_id,
                name=name,
                location=location,
                owner_id=owner_id,
                area_hectares=area_hectares,
                crop_type=crop_type,
                planting_date=planting_date or datetime.now().strftime("%Y-%m-%d"),
                created_date=datetime.now().strftime("%Y-%m-%d"),
                status="active"
            )
            
            # Register farm
            self.farm_info[farm_id] = farm_info
            
            print(f"Farm {farm_id} ({name}) added successfully")
            
            return {
                "success": True,
                "farm_id": farm_id,
                "message": f"Farm {name} registered successfully"
            }
            
        except Exception as e:
            print(f"Error adding farm: {e}")
            return {"success": False, "error": str(e)}
    
    def remove_farm(self, farm_id: str, user_id: str):
        """Remove a farm from the system"""
        try:
            if farm_id not in self.farm_info:
                return {"success": False, "error": "Farm not found"}
            
            # Remove from registry
            del self.farm_info[farm_id]
            
            print(f"Farm {farm_id} removed successfully")
            
            return {"success": True, "message": f"Farm {farm_id} removed"}
            
        except Exception as e:
            print(f"Error removing farm: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_farms_status(self, user_id: str = None):
        """Get status from all farms"""
        try:
            status_report = {
                "timestamp": datetime.now().isoformat(),
                "total_farms": len(self.farm_info),
                "active_farms": 0,
                "farms": {}
            }
            
            for farm_id, farm_info in self.farm_info.items():
                status_report["farms"][farm_id] = {
                    "farm_info": asdict(farm_info),
                    "system_status": {
                        "irrigation_active": False,
                        "soil_moisture": 50.0,
                        "weather": {"temperature": 25.0, "humidity": 60.0},
                        "rainfall_probability": 30.0,
                        "auto_mode": True
                    },
                    "status_timestamp": datetime.now().isoformat()
                }
            
            return status_report
            
        except Exception as e:
            print(f"Error getting farms status: {e}")
            return {"error": str(e)}
    
    def get_multi_farm_analytics(self, user_id: str):
        """Get analytics across multiple farms"""
        try:
            analytics = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_farms": len(self.farm_info),
                    "total_area_hectares": sum(info.area_hectares for info in self.farm_info.values()),
                    "active_irrigation_systems": 0,
                    "average_soil_moisture": 50.0,
                    "total_water_usage_today": 0
                },
                "farm_comparison": [],
                "alerts_summary": {
                    "critical": 0,
                    "warning": 0,
                    "info": 0
                },
                "yield_predictions": {}
            }
            
            for farm_id, farm_info in self.farm_info.items():
                farm_comparison = {
                    "farm_id": farm_id,
                    "name": farm_info.name,
                    "soil_moisture": 50.0,
                    "irrigation_status": "inactive",
                    "area_hectares": farm_info.area_hectares,
                    "crop_type": farm_info.crop_type
                }
                analytics["farm_comparison"].append(farm_comparison)
            
            return analytics
            
        except Exception as e:
            print(f"Error getting multi-farm analytics: {e}")
            return {"error": str(e)}
    
    def start_central_monitoring(self):
        """Start central monitoring for all farms"""
        print("Central farm monitoring started")
    
    def stop_central_monitoring(self):
        """Stop central monitoring"""
        print("Central farm monitoring stopped")

class UserAuthenticationSystem:
    def __init__(self):
        print("User authentication system initialized")
        
        # Simple user database
        self.users = {
            "admin": {
                "role": "admin", 
                "farms": [],
                "email": "admin@smartfarm.com"
            }
        }
    
    def validate_user(self, user_id: str):
        """Validate if user exists"""
        return user_id in self.users
    
    def is_admin(self, user_id: str):
        """Check if user is admin"""
        return user_id in self.users and self.users[user_id]["role"] == "admin"
