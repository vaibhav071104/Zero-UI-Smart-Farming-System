import logging
import os
import json
import sys
from datetime import datetime
from config.config import Config

class UnicodeFormatter(logging.Formatter):
    """Custom formatter that handles Unicode characters properly"""
    def format(self, record):
        # Convert message to ASCII-safe version for console output
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Replace Unicode characters with ASCII equivalents for console
            safe_msg = record.msg
            # Common Hindi/Gujarati/Telugu replacements
            replacements = {
                'पानी': 'pani',
                'बंद': 'band',
                'करो': 'karo',
                'शुरू': 'shuru',
                'नीरू': 'neeru',
                'आप': 'aapu',
                'બંધ': 'bandh',
                'કરો': 'karo',
                'પાણી': 'pani',
                'నీరు': 'neeru',
                'ఆపు': 'aapu',
                'ప్రారంభించు': 'prarambhinchu'
            }
            for unicode_text, ascii_text in replacements.items():
                safe_msg = safe_msg.replace(unicode_text, ascii_text)
            record.msg = safe_msg
        return super().format(record)

class SystemLogger:
    def __init__(self):
        self.config = Config()
        
        os.makedirs('logs', exist_ok=True)
        
        self.logger = logging.getLogger('ZeroUIFarming')
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(self.config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler with Unicode-safe formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Standard formatter for file (preserves Unicode)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Unicode-safe formatter for console
        console_formatter = UnicodeFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        print("System logger initialized with Unicode support")
    
    def log_system_event(self, event_type, message, data=None):
        """Log system events"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'data': data
        }
        
        self.logger.info(f"{event_type}: {message}")
        self._save_json_log(log_data)
    
    def log_command(self, command_type, command_text, action_result):
        """Log user commands"""
        self.log_system_event(
            'COMMAND',
            f"{command_type} command: {command_text}",
            {'action_result': action_result}
        )
    
    def log_irrigation_event(self, event, reason, duration=None):
        """Log irrigation events"""
        data = {'reason': reason}
        if duration:
            data['duration'] = duration
            
        self.log_system_event('IRRIGATION', f"Irrigation {event}", data)
    
    def log_error(self, component, error_message, exception=None):
        """Log errors"""
        data = {'component': component, 'error': error_message}
        if exception:
            data['exception'] = str(exception)
            
        self.logger.error(f"{component} error: {error_message}")
        self._save_json_log({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'ERROR',
            'message': f"{component} error: {error_message}",
            'data': data
        })
    
    def _save_json_log(self, log_data):
        """Save log data to JSON file for analysis"""
        json_log_file = 'logs/system_events.json'
        
        try:
            if os.path.exists(json_log_file):
                with open(json_log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_data)
            
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(json_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save JSON log: {e}")
