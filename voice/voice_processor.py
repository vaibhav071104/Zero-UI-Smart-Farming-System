import threading
from config.config import Config

class VoiceCommandProcessor:
    def __init__(self, actuator):
        self.config = Config()
        self.actuator = actuator
        self.timed_irrigation_timer = None
    
    def process_command(self, command_text):
        """Process voice command and return action"""
        if not command_text:
            return None
        
        command_lower = command_text.lower()
        
        # Check each command type
        for phrase in self.config.VOICE_COMMANDS:
            if phrase.lower() in command_lower:
                return self._execute_action("start_irrigation", command_text)  # or the correct action
        
        for action, phrases in Config.LANGUAGE_COMMANDS["hi"].items():  # or loop over all languages if needed
            for phrase in phrases:
                if phrase.lower() in command_lower:
                    return self._execute_action(action, command_text)
        
        return None
    
    def _execute_action(self, action, original_command):
        """Execute the recognized action"""
        try:
            if action == "start_irrigation":
                if self.actuator.turn_on():
                    print(f"✅ Irrigation started via voice: '{original_command}'")
                    return "IRRIGATION_START"
                    
            elif action == "stop_irrigation":
                if self.actuator.turn_off():
                    print(f"✅ Irrigation stopped via voice: '{original_command}'")
                    return "IRRIGATION_STOP"
                    
            elif action == "status_check":
                status = self.actuator.get_status()
                print(f"System Status: {status}")
                return "STATUS_CHECK"
                
            elif action == "timed_irrigation":
                if self.actuator.turn_on():
                    # Start timer for 1 hour (3600 seconds)
                    if self.timed_irrigation_timer:
                        self.timed_irrigation_timer.cancel()
                    
                    self.timed_irrigation_timer = threading.Timer(3600, self.actuator.turn_off)
                    self.timed_irrigation_timer.start()
                    print(f"✅ Timed irrigation started (1 hour): '{original_command}'")
                    return "IRRIGATION_TIMED"
                    
            elif action == "emergency_stop":
                if self.actuator.turn_off():
                    if self.timed_irrigation_timer:
                        self.timed_irrigation_timer.cancel()
                    print(f"��� Emergency stop activated: '{original_command}'")
                    return "EMERGENCY_STOP"
                    
        except Exception as e:
            print(f"❌ Error executing voice action: {e}")
            
        return None
