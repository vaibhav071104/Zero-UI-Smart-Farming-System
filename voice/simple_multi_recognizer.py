# -*- coding: utf-8 -*-
import json
import queue
import threading
import time
import os
import pyaudio
import vosk
from config.config import Config

class SimpleMultiLanguageRecognizer:
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.recognizers = {}
        self.audio_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None
        self.microphone = None
        
        # Use round-robin approach
        self.languages = []
        self.current_index = 0
        
        self._initialize_models()
        self._initialize_audio()
    
    def _initialize_models(self):
        """Initialize available models"""
        print("Initializing simple multi-language recognition...")
        
        for lang in Config.SUPPORTED_LANGUAGES:
            model_path = Config.VOICE_MODEL_PATHS[lang]
            if os.path.exists(model_path):
                try:
                    print(f"📊 Loading {lang.title()} model...")
                    self.models[lang] = vosk.Model(model_path)
                    self.recognizers[lang] = vosk.KaldiRecognizer(
                        self.models[lang], 
                        Config.VOICE_SAMPLE_RATE
                    )
                    self.languages.append(lang)
                    print(f"✅ {lang.title()} model loaded")
                except Exception as e:
                    print(f"❌ Failed to load {lang}: {e}")
        print(f" Will cycle through: {' → '.join([l.title() for l in self.languages])}")
    
    def _initialize_audio(self):
        """Initialize audio"""
        try:
            self.audio = pyaudio.PyAudio()
            self.microphone = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.VOICE_SAMPLE_RATE,
                input=True,
                frames_per_buffer=Config.VOICE_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            print("✅ Simple multi-language microphone ready")
        except Exception as e:
            print(f"❌ Audio init failed: {e}")
            raise
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def start_listening(self):
        """Start listening"""
        if self.is_listening:
            return
        self.is_listening = True
        if self.microphone is not None:
            self.microphone.start_stream()
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("Simple multi-language listening started")
    
    def _listen_loop(self):
        """Simple listening loop"""
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    
                    # Try current language
                    current_lang = self.languages[self.current_index]
                    recognizer = self.recognizers[current_lang]
                    
                    if recognizer.AcceptWaveform(audio_data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            print(f"DEBUG: Recognized text: '{text}' (language: {current_lang})")
                            # Check if it matches commands for this language
                            if self._matches_language_commands(text, current_lang):
                                print(f"Heard ({current_lang}): '{text}'")
                                self.command_queue.put({
                                    'text': text,
                                    'language': current_lang,
                                    'timestamp': time.time()
                                })
                            else:
                                # Try next language
                                self.current_index = (self.current_index + 1) % len(self.languages)
                                print(f"🔄 Switching to {self.languages[self.current_index].title()}")
                    else:
                        partial_result = recognizer.PartialResult()
                        partial_text = json.loads(partial_result).get('partial', '')
                        if partial_text:
                            print(f"DEBUG: Partial: '{partial_text}' (language: {current_lang})")
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"❌ Listen error: {e}")
                time.sleep(0.1)
    
    def _matches_language_commands(self, text, language):
        """Check if text matches language commands"""
        commands = Config.LANGUAGE_COMMANDS.get(language, {})
        
        text_lower = text.lower()
        for command_type, phrases in commands.items():
            for phrase in phrases:
                if phrase.lower() in text_lower:
                    return True
        
        # Also accept if contains common words
        common_words = ['pani', 'paani', 'water', 'neeru', 'jal']
        for word in common_words:
            if word in text_lower:
                return True
                
        return False
    
    def get_command(self):
        """Get command"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if self.microphone:
            self.microphone.stop_stream()
        print("Simple recognition stopped")
    
    def get_available_languages(self):
        return self.languages
