# -*- coding: utf-8 -*-
# test_multilingual_voice.py

from voice.multi_language_recognizer import FixedMultiLanguageRecognizer
from voice.multi_language_processor import MultiLanguageVoiceProcessor
from actuator.relay_actuator import RelayActuator
import time

def test_multilingual_voice():
    print("🌍 Testing Multi-Language Voice Recognition...")
    
    # Initialize components
    relay = RelayActuator()
    voice_recognizer = FixedMultiLanguageRecognizer()
    voice_processor = MultiLanguageVoiceProcessor(relay)
    
    # Show available languages
    available_langs = voice_recognizer.get_available_languages()
    print(f"🌍 Available languages: {', '.join([lang.title() for lang in available_langs])}")
    
    # Show sample commands
    supported_commands = voice_processor.get_supported_languages()
    print("\n📝 Sample commands:")
    for lang, commands in supported_commands.items():
        if lang in available_langs:
            print(f"  {lang.title()}: '{commands['start_command']}' / '{commands['stop_command']}'")
    
    try:
        # Start recognition
        voice_recognizer.start_listening()
        print("\n✅ Multi-language voice recognition active!")
        print("🗣️ Try speaking in any supported Indian language")
        print("⏹️ Press Ctrl+C to stop")
        
        # Main loop
        for i in range(300):  # Run for 5 minutes max
            command_data = voice_recognizer.get_command()
            if command_data:
                action = voice_processor.process_multilingual_command(command_data)
                if action:
                    print(f"🎯 Action: {action} (Language: {command_data['language'].title()})")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping multilingual test...")
    finally:
        voice_recognizer.stop_listening()
        print("✅ Test completed!")

if __name__ == '__main__':
    test_multilingual_voice()
