from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import threading
import sys
import os
import time
import importlib.util

# Ensure the main system is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import ZeroUISmartFarmingSystem

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from retrain_models import AgriTechModelRetrainer

app = FastAPI(
    title="Zero-UI Smart Farming System API",
    description="API for controlling and monitoring the Zero-UI Smart Farming System",
    version="2.0"
)

# --- Initialize the system (as in main.py) ---
farming_system = ZeroUISmartFarmingSystem()
farming_system.initialize_phase2_features()
farming_system.start_full_system()

# --- Pydantic Models for Requests/Responses ---

class IrrigationCommand(BaseModel):
    action: str  # "start" or "stop"
    reason: Optional[str] = None

class VoiceCommand(BaseModel):
    text: str
    language: str

class GestureCommand(BaseModel):
    gesture: str

# --- Retrain Models State ---
retrain_status = {
    'in_progress': False,
    'last_result': None,
    'last_error': None,
    'last_timestamp': None
}
retrain_lock = threading.Lock()

def retrain_models_background():
    global retrain_status
    with retrain_lock:
        retrain_status['in_progress'] = True
        retrain_status['last_error'] = None
        retrain_status['last_result'] = None
        retrain_status['last_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        retrainer = AgriTechModelRetrainer()
        output_dir = retrainer.retrain_all_models()
        with retrain_lock:
            retrain_status['in_progress'] = False
            retrain_status['last_result'] = {
                'output_dir': output_dir,
                'timestamp': retrainer.timestamp
            }
            retrain_status['last_error'] = None
    except Exception as e:
        with retrain_lock:
            retrain_status['in_progress'] = False
            retrain_status['last_error'] = str(e)
            retrain_status['last_result'] = None

# --- Test All Features State ---
test_status = {
    'in_progress': False,
    'last_result': None,
    'last_error': None,
    'last_timestamp': None
}
test_lock = threading.Lock()

def run_full_system_test():
    global test_status
    with test_lock:
        test_status['in_progress'] = True
        test_status['last_error'] = None
        test_status['last_result'] = None
        test_status['last_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    import io
    import contextlib
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            farming_system.test_all_components()
            print("\n" + "="*80)
            print("PHASE 2 ADVANCED FEATURES TEST")
            print("="*80)
            farming_system.test_phase2_features()
        result = output.getvalue()
        with test_lock:
            test_status['in_progress'] = False
            test_status['last_result'] = result
            test_status['last_error'] = None
    except Exception as e:
        with test_lock:
            test_status['in_progress'] = False
            test_status['last_error'] = str(e)
            test_status['last_result'] = None
    finally:
        output.close()

# --- API Endpoints ---

@app.get("/status", summary="Get system status")
def get_status():
    return farming_system.smart_controller.get_system_status()

@app.post("/irrigation", summary="Start or stop irrigation")
def control_irrigation(cmd: IrrigationCommand):
    if cmd.action == "start":
        result = farming_system.smart_controller.actuator.turn_on()
        if result:
            farming_system.smart_controller.override_active = False
            return {"status": "started"}
        else:
            return {"status": "already_on"}
    elif cmd.action == "stop":
        result = farming_system.smart_controller.actuator.turn_off()
        if result:
            farming_system.smart_controller.override_active = True
            return {"status": "stopped"}
        else:
            return {"status": "already_off"}
    else:
        return {"error": "Invalid action"}

@app.post("/voice", summary="Send a voice command")
def send_voice_command(cmd: VoiceCommand):
    # Simulate a voice command as if it was heard by the recognizer
    command_data = {"text": cmd.text, "language": cmd.language}
    result = farming_system.voice_processor.process_multilingual_command(command_data)
    return {"result": result}

@app.post("/gesture", summary="Send a gesture command")
def send_gesture_command(cmd: GestureCommand):
    result = farming_system.gesture_processor.process_gesture(cmd.gesture)
    return {"result": result}

@app.get("/emotion", summary="Analyze farmer emotion")
def analyze_emotion(command_text: str = Query(..., description="Text to analyze")):
    if farming_system.emotion_detector:
        return farming_system.emotion_detector.analyze_farmer_state(command_text=command_text)
    return {"error": "Emotion detector not available"}

@app.get("/yield", summary="Predict harvest yield")
def predict_yield():
    if farming_system.yield_predictor:
        # Example: use current sensor values
        farm_data = {
            'avg_soil_moisture': farming_system.soil_sensor.get_value(),
            'total_irrigation_hours': 120,
            'avg_temperature': farming_system.weather_sensor.get_weather()['temperature'],
            'total_rainfall': 180,
            'days_since_planting': 85,
            'fertilizer_applications': 4
        }
        return farming_system.yield_predictor.predict_harvest_yield(farm_data)
    return {"error": "Yield predictor not available"}

@app.get("/dashboard", summary="Get dashboard data")
def get_dashboard(user_id: str = "admin"):
    if farming_system.farm_dashboard:
        return farming_system.farm_dashboard.generate_dashboard_data(user_id)
    return {"error": "Dashboard not available"}

@app.post("/retrain_models", summary="Retrain all ML models")
def retrain_models():
    with retrain_lock:
        if retrain_status['in_progress']:
            return {"status": "in_progress", "message": "Retraining already running."}
        retrain_status['in_progress'] = True
        retrain_status['last_error'] = None
        retrain_status['last_result'] = None
        retrain_status['last_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    threading.Thread(target=retrain_models_background, daemon=True).start()
    return {"status": "started", "message": "Model retraining started in background."}

@app.get("/retrain_status", summary="Get retrain models status")
def get_retrain_status():
    with retrain_lock:
        return retrain_status.copy()

@app.post("/test_all", summary="Run comprehensive system test")
def test_all():
    with test_lock:
        if test_status['in_progress']:
            return {"status": "in_progress", "message": "Test already running."}
        test_status['in_progress'] = True
        test_status['last_error'] = None
        test_status['last_result'] = None
        test_status['last_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    threading.Thread(target=run_full_system_test, daemon=True).start()
    return {"status": "started", "message": "Comprehensive system test started in background."}

@app.get("/test_status", summary="Get comprehensive test status and result")
def get_test_status():
    with test_lock:
        return test_status.copy()

# --- Add more endpoints as needed for multi-farm, analytics, etc. ---

# --- Instructions ---
# Run with: uvicorn zero_ui_smart_farming.api.main_api:app --reload --port 8000
# Then open http://localhost:8000/docs for Swagger UI 