import os
import threading

class Config:
    MOISTURE_LOW_THRESHOLD = 30
    MAX_IRRIGATION_DURATION_MIN = 45
    MIN_FLOW_RATE_LPM = 2.0
    PRESSURE_MIN_BAR = 1.5
    PRESSURE_MAX_BAR = 3.5
    IRRIGATION_TIME_WINDOWS = [(5, 10), (16, 20)]  # Morning 5-10AM, Evening 4-8PM
    IRRIGATION_DAYS_ALLOWED = [0, 1, 2, 3, 4, 5, 6]
    SEASONAL_ADJUSTMENT = {
        'summer': {'MOISTURE_LOW_THRESHOLD': 35, 'MAX_IRRIGATION_DURATION_MIN': 60},
        'winter': {'MOISTURE_LOW_THRESHOLD': 25, 'MAX_IRRIGATION_DURATION_MIN': 30}
    }
    TEMP_TRIGGER_C = 38
    HUMIDITY_COMPENSATION = 85
    WIND_SPEED_MAX_MPS = 8
    MIN_IRRIGATION_INTERVAL = 60 * 60
    RAIN_FORECAST_SKIP_HOURS = 6  # Skip auto irrigation if rain is predicted in next 6 hours
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/system.log"
    VOICE_SAMPLE_RATE = 16000
    VOICE_CHUNK_SIZE = 4000

    # Absolute model paths for each language
    BASE_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    VOICE_MODEL_PATHS = {
        "hi": os.path.join(BASE_MODEL_PATH, "vosk-model-hi-0.22"),
        "gu": os.path.join(BASE_MODEL_PATH, "vosk-model-gu-0.42"),
        "te": os.path.join(BASE_MODEL_PATH, "vosk-model-small-te-0.42"),
    }
    # Default model path (Hindi)
    VOICE_MODEL_PATH = VOICE_MODEL_PATHS["hi"]

    # Supported languages (short codes)
    SUPPORTED_LANGUAGES = ["hi", "gu", "te"]

    # Voice commands (all supported commands in all languages)
    VOICE_COMMANDS = [
        # Hindi
        "पानी चालू करो", "सिंचाई शुरू करो", "पानी बंद करो", "सिंचाई बंद करो",
        # Gujarati
        "પાણી ચાલુ કરો", "સિંચાઈ શરૂ કરો", "પાણી બંધ કરો", "સિંચાઈ બંધ કરો",
        # Telugu
        "నీరు ప్రారంభించు", "నీరు మొదలు పెట్టు", "నీరు ఆపు", "నీరు నిలిపివేయి",
        # English (if supported)
        "start irrigation", "stop irrigation", "irrigation on", "irrigation off"
    ]

    # Per-language command mapping (optional, for reference)
    LANGUAGE_COMMANDS = {
        "hi": {
            "start": ["पानी चालू करो", "सिंचाई शुरू करो"],
            "stop": ["पानी बंद करो", "सिंचाई बंद करो"]
        },
        "gu": {
            "start": ["પાણી ચાલુ કરો", "સિંચાઈ શરૂ કરો"],
            "stop": ["પાણી બંધ કરો", "સિંચાઈ બંધ કરો"]
        },
        "te": {
            "start": ["నీరు ప్రారంభించు", "నీరు మొదలు పెట్టు"],
            "stop": ["నీరు ఆపు", "నీరు నిలిపివేయి"]
        }
    }