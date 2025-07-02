# voice/state_reset_recognizer.py
# -*- coding: utf-8 -*-
import json
import queue
import threading
import time
import os
import pyaudio
import vosk
from config.config import Config

class StateResetMultiLanguageRecognizer:
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.recognizers = {}
        self.audio_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.listen_thread = None
        self.microphone = None

        # Language management
        self.languages = []
        self.current_language = 'hi'
        self.recognition_count = 0

        self._initialize_models()
        self._initialize_audio()

    def _initialize_models(self):
        print("🌍 Initializing STATE-RESET multi-language recognition...")
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
            print("✅ State-reset microphone ready")
        except Exception as e:
            print(f"❌ Audio init failed: {e}")
            raise

    def _audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def _reset_recognizer(self, language):
        try:
            self.recognizers[language] = vosk.KaldiRecognizer(
                self.models[language],
                Config.VOICE_SAMPLE_RATE
            )
            print(f"🔄 Recognizer reset for {language}")
        except Exception as e:
            print(f"❌ Failed to reset recognizer for {language}: {e}")

    def start_listening(self):
        if self.is_listening:
            print("Already listening.")
            return
        if self.microphone is None:
            print("❌ Microphone is not initialized. Cannot start listening.")
            return
        self.is_listening = True
        try:
            self.microphone.start_stream()
        except AttributeError:
            print("❌ Microphone object does not have 'start_stream' method or is not initialized.")
            self.is_listening = False
            return
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("🎤 State-reset multi-language listening started")
        print("💡 Recognizer will reset after each command for continuous recognition")

    def _listen_loop(self):
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    best_result = None
                    best_language = None
                    best_confidence = 0

                    for lang in self.languages:
                        recognizer = self.recognizers[lang]
                        if recognizer.AcceptWaveform(audio_data):
                            result = json.loads(recognizer.Result())
                            text = result.get('text', '').strip()
                            if text:
                                print(f"DEBUG: Recognized text: '{text}' (language: {lang})")
                                confidence = len(text) * 0.1
                                if self._is_irrigation_command(text):
                                    confidence += 2.0
                                if lang == 'te':
                                    text_lower = text.lower()
                                    if 'neeru aapu' in text_lower or 'నీరు ఆపు' in text:
                                        confidence += 5.0
                                    elif 'neeru' in text_lower and 'aapu' in text_lower:
                                        confidence += 3.0
                                    if any(word in text_lower for word in ['neeru', 'aapu', 'నీరు', 'ఆపు']):
                                        confidence += 3.0
                                    if 'neeru' in text_lower and 'aapu' in text_lower:
                                        confidence += 2.0
                                elif lang == 'gu':
                                    if any(word in text.lower() for word in ['neeru', 'aapu']):
                                        confidence -= 2.0
                                    if any(word in text.lower() for word in ['pani', 'band', 'પાણી', 'બંધ']):
                                        confidence += 1.5
                                elif lang == 'hi':
                                    if any(word in text.lower() for word in ['neeru', 'aapu']):
                                        confidence -= 2.0
                                    if any(word in text.lower() for word in ['pani', 'band', 'पानी', 'बंद']):
                                        confidence += 1.5
                                if confidence > best_confidence:
                                    best_confidence = confidence
                                    best_result = text
                                    best_language = lang
                        else:
                            partial_result = recognizer.PartialResult()
                            partial_text = json.loads(partial_result).get('partial', '')
                            if partial_text:
                                print(f"DEBUG: Partial: '{partial_text}' (language: {lang})")

                    if best_result and best_language:
                        print(f"🗣️ Heard ({best_language}): '{best_result}' (confidence: {best_confidence:.2f})")
                        self.current_language = best_language
                        self.command_queue.put({
                            'text': best_result,
                            'language': best_language,
                            'timestamp': time.time()
                        })
                        self.recognition_count += 1
                        print(f"✅ Command #{self.recognition_count} recognized in {best_language}")
                        self._reset_recognizer(best_language)
                    else:
                        current_recognizer = self.recognizers[self.current_language]
                        partial_result = json.loads(current_recognizer.PartialResult())
                        partial_text = partial_result.get('partial', '')
                        if partial_text:
                            print(f"🔊 Listening... '{partial_text}'")
                time.sleep(0.01)
            except Exception as e:
                print(f"❌ Listen error: {e}")
                self._reset_recognizer(self.current_language)
                time.sleep(0.1)

    def _is_irrigation_command(self, text):
        text_lower = text.lower()
        irrigation_keywords = [
            'पानी', 'सिंचाई', 'जल',  # Hindi
            'પાણી', 'સિંચાઈ',        # Gujarati
            'నీరు', 'ప్రారంభించు', 'ఆపు',  # Telugu
            'band', 'shuru', 'aapu', 'neeru'
        ]
        return any(keyword in text_lower for keyword in irrigation_keywords)

    def get_command(self):
        try:
            return self.command_queue.get(timeout=5)
        except queue.Empty:
            return None

    def stop_listening(self):
        self.is_listening = False
        if self.microphone:
            self.microphone.stop_stream()
            self.microphone.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        print("🛑 State-reset multi-language listening stopped")

    def get_available_languages(self):
        return self.languages

    def get_current_language(self):
        return self.current_language

    def get_recognition_count(self):
        return self.recognition_count