import time
from datetime import datetime
from config.config import Config

class CommandFusionProcessor:
    def __init__(self, voice_processor, gesture_processor, smart_controller):
        self.config = Config()
        self.voice_processor = voice_processor
        self.gesture_processor = gesture_processor
        self.smart_controller = smart_controller
        
        self.command_history = []
        self.last_voice_command = None
        self.last_gesture_command = None
        self.pending_confirmation = None
        self.confirmation_timeout = 10  # seconds
        
        print("Command fusion processor initialized")
    
    def process_inputs(self, voice_command, gesture_command):
        """Process and fuse voice and gesture inputs"""
        timestamp = datetime.now()
        action_taken = None
        source = None
        confidence = 0.0
        
        # Priority system: Voice > Gesture > Smart Logic
        
        # 1. Process voice command (highest priority)
        if voice_command:
            action_taken = self.voice_processor.process_multilingual_command(voice_command)
            source = "VOICE"
            confidence = 0.9
            self.last_voice_command = voice_command
            
        # 2. Process gesture command (medium priority)
        elif gesture_command:
            action_taken = self.gesture_processor.process_gesture(gesture_command)
            source = "GESTURE"
            confidence = 0.7
            self.last_gesture_command = gesture_command
            
        # 3. Check smart logic (lowest priority)
        else:
            if self.smart_controller.auto_mode:
                if self.smart_controller.start_automatic_irrigation():
                    action_taken = "AUTO_IRRIGATION_START"
                    source = "SMART_LOGIC"
                    confidence = 0.8
        
        # Handle confirmations and conflicts
        if action_taken:
            action_taken = self._handle_confirmations(action_taken, source)
            
        # Log the command
        self._log_command(voice_command, gesture_command, action_taken, source, confidence, timestamp)
        
        return {
            'action': action_taken,
            'source': source,
            'confidence': confidence,
            'timestamp': timestamp,
            'requires_confirmation': self.pending_confirmation is not None
        }
    
    def _handle_confirmations(self, action, source):
        """Handle action confirmations for critical operations"""
        
        # Actions that require confirmation
        critical_actions = ["EMERGENCY_STOP", "OVERRIDE_START"]
        
        if action in critical_actions:
            if self.pending_confirmation == action:
                # Confirmation received
                print(f"Action confirmed: {action}")
                self.pending_confirmation = None
                return action
            else:
                # Request confirmation
                print(f"Action requires confirmation: {action}")
                print("   Say 'confirm' or show thumb up gesture to proceed")
                self.pending_confirmation = action
                self.confirmation_timestamp = time.time()
                return None
                
        elif action == "CONFIRM":
            if self.pending_confirmation:
                # Check timeout
                if time.time() - self.confirmation_timestamp < self.confirmation_timeout:
                    confirmed_action = self.pending_confirmation
                    self.pending_confirmation = None
                    print(f"Confirmed action: {confirmed_action}")
                    
                    # Execute the confirmed action
                    return self._execute_confirmed_action(confirmed_action)
                else:
                    print("Confirmation timeout - action cancelled")
                    self.pending_confirmation = None
            else:
                print("No action pending confirmation")
            return None
        
        # Check for confirmation timeout
        if (self.pending_confirmation and 
            time.time() - self.confirmation_timestamp > self.confirmation_timeout):
            print("Confirmation timeout - action cancelled")
            self.pending_confirmation = None
        
        return action
    
    def _execute_confirmed_action(self, action):
        """Execute a confirmed critical action"""
        if action == "EMERGENCY_STOP":
            self.smart_controller.actuator.emergency_stop()
            self.smart_controller.set_auto_mode(False)
            return "EMERGENCY_STOP_CONFIRMED"
            
        elif action == "OVERRIDE_START":
            self.smart_controller.override_irrigation("start")
            return "OVERRIDE_START_CONFIRMED"
        
        return action
    
    def _log_command(self, voice_cmd, gesture_cmd, action, source, confidence, timestamp):
        """Log all commands and actions"""
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'voice_command': voice_cmd,
            'gesture_command': gesture_cmd,
            'action_taken': action,
            'source': source,
            'confidence': confidence,
            'system_status': self.smart_controller.get_system_status()
        }
        
        self.command_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def get_recent_commands(self, count=10):
        """Get recent command history"""
        return self.command_history[-count:] if self.command_history else []
    
    def get_command_statistics(self):
        """Get command usage statistics"""
        if not self.command_history:
            return {}
        
        sources = {}
        actions = {}
        
        for entry in self.command_history:
            source = entry.get('source', 'UNKNOWN')
            action = entry.get('action_taken', 'NONE')
            
            sources[source] = sources.get(source, 0) + 1
            if action:
                actions[action] = actions.get(action, 0) + 1
        
        return {
            'total_commands': len(self.command_history),
            'sources': sources,
            'actions': actions,
            'success_rate': len([e for e in self.command_history if e.get('action_taken')]) / len(self.command_history)
        }
    
    def reset_pending_confirmation(self):
        """Reset any pending confirmations"""
        self.pending_confirmation = None
        print("Pending confirmations cleared")
