# -*- coding: utf-8 -*-
from config.config import Config
import time

class GestureCommandProcessor:
    def __init__(self, actuator):
        self.config = Config()
        self.actuator = actuator
        self.last_action_time = 0
        self.action_cooldown = 2.0  # 2 seconds between actions
    
    def process_gesture(self, gesture):
        """Process gesture with improved reliability"""
        if not gesture:
            return None
        
        current_time = time.time()
        
        # Prevent rapid-fire actions
        if current_time - self.last_action_time < self.action_cooldown:
            return None
        
        try:
            action = None
            
            if gesture == "swipe_right":
                if self.actuator.turn_on():
                    print(f"✅ Irrigation started via gesture: swipe right")
                    action = "IRRIGATION_START"
                    
            elif gesture == "swipe_left":
                if self.actuator.turn_off():
                    print(f"✅ Irrigation stopped via gesture: swipe left")
                    action = "IRRIGATION_STOP"
                    
            elif gesture == "palm_up" or gesture == "open_hand":
                status = self.actuator.get_status()
                print(f"📊 Status check via gesture: {status}")
                action = "STATUS_CHECK"
                
            elif gesture == "thumb_up":
                print("✅ Confirmation gesture received")
                action = "CONFIRM"
                
            elif gesture == "peace_sign":
                if self.actuator.turn_off():
                    print("🚨 Emergency stop via gesture: peace sign")
                    action = "EMERGENCY_STOP"
                    
            elif gesture == "fist":
                print("✊ Standby gesture detected")
                action = "STANDBY"
                
            elif gesture == "point":
                print("👉 Pointing gesture detected")
                action = "POINT"
            
            if action:
                self.last_action_time = current_time
                
            return action
                
        except Exception as e:
            print(f"❌ Error processing gesture: {e}")
            
        return None
