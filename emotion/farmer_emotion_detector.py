import os
import numpy as np
from datetime import datetime
from pyAudioAnalysis import audioSegmentation as aS
from pyAudioAnalysis import audioBasicIO

class FarmerEmotionDetector:
    def __init__(self):
        print("Initializing Farmer Emotion Detection System...")
        self.current_emotion = "neutral"
        self.stress_level = 0.0
        self.urgency_detected = False
        self.stress_threshold = 0.7
        self.urgency_keywords = ['जल्दी', 'तुरंत', 'emergency', 'urgent', 'help', 'problem', 'समस्या', 'मदद', 'crisis']
        print("Emotion detection system ready")

    def analyze_audio_emotion(self, audio_path):
        """Analyze emotion from an audio file (WAV) using pyAudioAnalysis"""
        try:
            [Fs, x] = audioBasicIO.read_audio_file(audio_path)
            x = audioBasicIO.stereo_to_mono(x)
            # Use pre-trained SVM model for emotion (pyAudioAnalysis comes with demo models)
            # You can train your own for better accuracy
            # Here we use the default model for demonstration
            segments, classes, acc, _ = aS.mt_file_classification(audio_path, "pyAudioAnalysis/data/svmSpeechEmo2", "svm", True)
            # Take the most common class in the file
            if len(classes) > 0:
                unique, counts = np.unique(classes, return_counts=True)
                main_emotion = unique[np.argmax(counts)]
                confidence = np.max(counts) / np.sum(counts)
            else:
                main_emotion = "neutral"
                confidence = 0.0
            self.current_emotion = main_emotion
            return {
                'primary_emotion': main_emotion,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'detailed_analysis': {'all_classes': classes.tolist() if hasattr(classes, 'tolist') else list(classes)}
            }
        except Exception as e:
            print(f"Audio emotion analysis error: {e}")
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat(),
                'detailed_analysis': {'error': str(e)}
            }

    def analyze_farmer_state(self, voice_data=None, video_frame=None, command_text="", audio_path=None):
        """Analyze emotion using audio (preferred), else fallback to text-based urgency"""
        if audio_path:
            return self.analyze_audio_emotion(audio_path)
        # Fallback to text-based urgency detection
        try:
            urgency_score = 0.0
            found_keywords = []
            if command_text:
                text_lower = command_text.lower()
                for keyword in self.urgency_keywords:
                    if keyword in text_lower:
                        found_keywords.append(keyword)
                        urgency_score += 0.3
                if len(command_text.split()) > 10:
                    urgency_score += 0.2
            self.stress_level = min(urgency_score, 1.0)
            self.urgency_detected = self.stress_level > self.stress_threshold
            self.current_emotion = "stressed" if self.urgency_detected else "neutral"
            return {
                'primary_emotion': self.current_emotion,
                'stress_level': self.stress_level,
                'urgency_detected': self.urgency_detected,
                'requires_immediate_attention': self.urgency_detected,
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat(),
                'detailed_analysis': {'keywords_found': found_keywords}
            }
        except Exception as e:
            print(f"Emotion analysis error: {e}")
            return {
                'primary_emotion': 'neutral',
                'stress_level': 0.0,
                'urgency_detected': False,
                'requires_immediate_attention': False,
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat(),
                'detailed_analysis': {}
            }
