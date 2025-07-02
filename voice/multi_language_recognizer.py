import json
import queue
import threading
import time
import os
import pyaudio
import vosk
from config.config import Config

class FixedMultiLanguageRecognizer:
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.recognizers = {}
        self.audio_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None
        self.microphone = None

        self.languages = []
        self.current_language = 'hi'
        self.last_successful_language = 'hi'
        self.silence_counter = 0
        self.switch_threshold = 3

        self._initialize_models()
        self._initialize_audio()

    def _initialize_models(self):
        print("🌍 Initializing FIXED multi-language recognition...")
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
        print(f"🎯 Languages available: {', '.join([l.title() for l in self.languages])}")
        print(f"🔊 Starting with: {self.current_language.title()}")

    def _initialize_audio(self):
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
            print("✅ Fixed multi-language microphone ready")
        except Exception as e:
            print(f"❌ Audio init failed: {e}")
            raise

    def _audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        if self.microphone is not None:
            self.microphone.start_stream()
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("🎤 Fixed multi-language listening started")
        print("💡 System will stick to detected language and only switch when needed")

    def _listen_loop(self):
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    results = []
                    for lang, recognizer in self.recognizers.items():
                        rec = recognizer
                        if rec.AcceptWaveform(audio_data):
                            result = json.loads(rec.Result())
                            text = result.get('text', '').strip()
                            confidence = result.get('confidence', 1.0)
                            if text:
                                is_valid = self._is_valid_command(text, lang)
                                results.append({
                                    'text': text,
                                    'language': lang,
                                    'confidence': confidence,
                                    'is_valid': is_valid
                                })
                                print(f"DEBUG: Recognized text: '{text}' (language: {lang})")
                        else:
                            partial_result = rec.PartialResult()
                            partial_text = json.loads(partial_result).get('partial', '')
                            if partial_text:
                                print(f"DEBUG: Partial: '{partial_text}' (language: {lang})")
                    best = None
                    for r in results:
                        if r['language'] == 'te' and r['is_valid']:
                            best = r
                            break
                    if not best:
                        valid_results = [r for r in results if r['is_valid']]
                        if valid_results:
                            best = max(valid_results, key=lambda x: x.get('confidence', 1.0))
                    if not best and results:
                        best = results[0]
                    if best:
                        print(f"🗣️ Heard ({best['language']}): '{best['text']}' (confidence: {best['confidence']:.2f})")
                        self.command_queue.put({
                            'text': best['text'],
                            'language': best['language'],
                            'timestamp': time.time()
                        })
                        self.last_successful_language = best['language']
                        self.current_language = best['language']
                        self.silence_counter = 0
                    else:
                        self.silence_counter += 1
                        if self.silence_counter >= self.switch_threshold:
                            self._try_next_language()
                time.sleep(0.01)
            except Exception as e:
                print(f"❌ Listen error: {e}")
                time.sleep(0.1)

    def _is_valid_command(self, text, language):
        commands = Config.LANGUAGE_COMMANDS.get(language, {})
        text_lower = text.lower()
        for command_type, phrases in commands.items():
            for phrase in phrases:
                if phrase.lower() in text_lower:
                    return True
        irrigation_keywords = {
            'hi': ['पानी', 'सिंचाई', 'जल'],
            'gu': ['પાણી', 'સિંચાઈ'],
            'te': ['నీరు', 'ప్రారంభించు', 'ఆపు']
        }
        keywords = irrigation_keywords.get(language, [])
        for keyword in keywords:
            if keyword in text_lower:
                return True
        return False

    def _switch_to_language(self, new_language):
        if new_language in self.languages:
            old_language = self.current_language
            self.current_language = new_language
            self.silence_counter = 0
            print(f"🔄 Language switched: {old_language.title()} → {new_language.title()}")

    def _try_next_language(self):
        current_index = self.languages.index(self.current_language)
        next_index = (current_index + 1) % len(self.languages)
        next_language = self.languages[next_index]
        print(f"🔄 Trying next language: {self.current_language.title()} → {next_language.title()}")
        self.current_language = next_language
        self.silence_counter = 0

    def get_command(self):
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def stop_listening(self):
        self.is_listening = False
        if self.microphone:
            self.microphone.stop_stream()
        print("🛑 Fixed recognition stopped")

    def get_available_languages(self):
        return self.languages

    def get_current_language(self):
        return self.current_language