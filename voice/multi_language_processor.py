# -*- coding: utf-8 -*-
import threading
from config.config import Config

class MultiLanguageVoiceProcessor:
    def __init__(self, actuator):
        self.config = Config()
        self.actuator = actuator
        self.timed_irrigation_timer = None
    
    def process_multilingual_command(self, command_data):
        """Process voice command in any supported language"""
        if not command_data:
            return None
        
        text = command_data['text']
        language = command_data['language']
        
        # Get language-specific commands
        commands = Config.LANGUAGE_COMMANDS.get(language, {})
        
        # Check each command type
        for action, phrases in commands.items():
            for phrase in phrases:
                if phrase.lower() in text.lower():
                    return self._execute_action(action, text, language)
        
        return None
    
    def _execute_action(self, action, original_command, language):
        """Execute the recognized action"""
        try:
            if action == "start_irrigation":
                if self.actuator.turn_on():
                    print(f"Irrigation started via {language} voice: '{original_command}'")
                    return "IRRIGATION_START"
                    
            elif action == "stop_irrigation":
                if self.actuator.turn_off():
                    print(f"Irrigation stopped via {language} voice: '{original_command}'")
                    return "IRRIGATION_STOP"
                    
            elif action == "status_check":
                status = self.actuator.get_status()
                print(f"System Status ({language}): {status}")
                return "STATUS_CHECK"
                
            elif action == "timed_irrigation":
                if self.actuator.turn_on():
                    # Cancel existing timer
                    if self.timed_irrigation_timer:
                        self.timed_irrigation_timer.cancel()
                    
                    # Start new timer for 1 hour
                    self.timed_irrigation_timer = threading.Timer(3600, self.actuator.turn_off)
                    self.timed_irrigation_timer.start()
                    print(f"Timed irrigation started (1 hour) via {language}: '{original_command}'")
                    return "IRRIGATION_TIMED"
                    
            elif action == "emergency_stop":
                if self.actuator.turn_off():
                    if self.timed_irrigation_timer:
                        self.timed_irrigation_timer.cancel()
                    print(f"Emergency stop activated via {language}: '{original_command}'")
                    return "EMERGENCY_STOP"
                    
        except Exception as e:
            print(f"Error executing {language} voice action: {e}")
            
        return None
    
    def get_supported_languages(self):
        """Get list of supported languages with sample commands"""
        languages_info = {}
        for lang in Config.LANGUAGE_COMMANDS:
            languages_info[lang] = {
                'start_command': Config.LANGUAGE_COMMANDS[lang]['start'][0],
                'stop_command': Config.LANGUAGE_COMMANDS[lang]['stop'][0]
            }
        return languages_info
