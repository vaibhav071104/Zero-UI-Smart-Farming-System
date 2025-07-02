import json
import queue
import threading
import time
import pyaudio
import vosk
from config.config import Config

class VoiceRecognizer:
    def __init__(self):
        self.config = Config()
        self.model = None
        self.recognizer = None
        self.microphone = None
        self.audio_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None
        
        self._initialize_model()
        self._initialize_audio()
    
    def _initialize_model(self):
        """Initialize Vosk speech recognition model"""
        try:
            print("Initializing voice recognition model...")
            self.model = vosk.Model(self.config.VOICE_MODEL_PATH)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.config.VOICE_SAMPLE_RATE)
            print("✅ Voice model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load voice model: {e}")
            raise
    
    def _initialize_audio(self):
        """Initialize PyAudio for microphone input"""
        try:
            self.audio = pyaudio.PyAudio()
            self.microphone = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.config.VOICE_SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.config.VOICE_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            print("✅ Microphone initialized")
        except Exception as e:
            print(f"❌ Failed to initialize microphone: {e}")
            raise
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def start_listening(self):
        """Start voice recognition in background thread"""
        if self.is_listening:
            return
            
        self.is_listening = True
        if self.microphone is not None:
            self.microphone.start_stream()
        else:
            print("❌ Microphone is not initialized.")
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print(" Voice recognition started")
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                # Get audio data
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    
                    # Process with Vosk
                    if self.recognizer is not None and self.recognizer.AcceptWaveform(audio_data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            print(f"DEBUG: Recognized text: '{text}'")
                            self.command_queue.put(text)
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
            except Exception as e:
                print(f"❌ Voice recognition error: {e}")
                time.sleep(0.1)
    
    def get_command(self):
        """Get the latest voice command"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        if self.microphone:
            self.microphone.stop_stream()
        print(" Voice recognition stopped")
    
    def __del__(self):
        """Cleanup resources"""
        self.stop_listening()
        if self.microphone:
            self.microphone.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
