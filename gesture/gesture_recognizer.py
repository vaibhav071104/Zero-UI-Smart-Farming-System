# -*- coding: utf-8 -*-
import cv2
import mediapipe as mp
import threading
import queue
import time
import numpy as np
from config.config import Config

class GestureRecognizer:
    def __init__(self):
        self.config = Config()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,  # Lowered for easier detection
            min_tracking_confidence=0.3    # Lowered for better tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.cap = None
        self.gesture_queue = queue.Queue()
        self.is_detecting = False
        self.detection_thread = None
        
        # Enhanced tracking variables
        self.previous_landmarks = None
        self.gesture_history = []
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # 1 second between gestures
        
        # Swipe detection variables
        self.swipe_start_pos = None
        self.swipe_threshold = 0.08  # Increased for more reliable detection
        self.min_swipe_distance = 0.15
        
    def start_detection(self):
        """Start gesture detection"""
        if self.is_detecting:
            return
            
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot open camera")
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
                
            self.is_detecting = True
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            print("👋 Enhanced gesture detection started")
            
        except Exception as e:
            print(f"❌ Failed to start gesture detection: {e}")
            raise
    
    def _detection_loop(self):
        """Enhanced gesture detection loop"""
        frame_count = 0
        
        while self.is_detecting:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # Process every 2nd frame for better performance
                if frame_count % 2 != 0:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Improve image quality
                frame = cv2.GaussianBlur(frame, (5, 5), 0)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame with MediaPipe
                results = self.hands.process(rgb_frame)
                
                current_time = time.time()
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Detect gesture with improved algorithm
                        gesture = self._enhanced_gesture_classification(hand_landmarks, current_time)
                        
                        if gesture and self._is_gesture_valid(gesture, current_time):
                            self.gesture_queue.put(gesture)
                            print(f"👋 Detected gesture: {gesture}")
                            self.last_gesture_time = current_time
                        
                        # Draw enhanced landmarks
                        self._draw_enhanced_landmarks(frame, hand_landmarks)
                
                # Add instruction text on frame
                self._add_instruction_text(frame)
                
                # Display frame
                cv2.imshow('Enhanced Gesture Recognition', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ Gesture detection error: {e}")
                time.sleep(0.1)
    
    def _enhanced_gesture_classification(self, landmarks, current_time):
        """Enhanced gesture classification with multiple methods"""
        try:
            # Extract landmark coordinates
            landmark_coords = []
            for lm in landmarks.landmark:
                landmark_coords.append([lm.x, lm.y])
            
            landmark_array = np.array(landmark_coords)
            
            # Method 1: Static gesture classification
            static_gesture = self._classify_static_gesture(landmark_array)
            
            # Method 2: Dynamic swipe detection
            swipe_gesture = self._enhanced_swipe_detection(landmark_array, current_time)
            
            # Priority: Swipe gestures > Static gestures
            if swipe_gesture:
                return swipe_gesture
            elif static_gesture:
                return self._smooth_gesture(static_gesture)
            
            return None
            
        except Exception as e:
            print(f"❌ Enhanced gesture classification error: {e}")
            return None
    
    def _classify_static_gesture(self, landmarks):
        """Improved static gesture classification"""
        try:
            # Finger tip and PIP joint indices
            finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
            finger_pips = [3, 6, 10, 14, 18]
            finger_mcp = [2, 5, 9, 13, 17]   # MCP joints for better accuracy
            
            # Check which fingers are extended
            fingers_up = []
            
            # Thumb (check x coordinate relative to MCP)
            if landmarks[finger_tips[0]][0] > landmarks[finger_mcp[0]][0]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
            
            # Other fingers (check y coordinate with improved threshold)
            for i in range(1, 5):
                tip_y = landmarks[finger_tips[i]][1]
                pip_y = landmarks[finger_pips[i]][1]
                mcp_y = landmarks[finger_mcp[i]][1]
                
                # More robust finger detection
                if tip_y < pip_y and tip_y < mcp_y:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)
            
            # Enhanced gesture classification
            total_fingers = sum(fingers_up)
            
            if total_fingers == 0:
                return "fist"
            elif total_fingers == 5:
                return "palm_up"
            elif fingers_up == [1, 1, 0, 0, 0]:  # Thumb + Index
                return "thumb_up"
            elif fingers_up == [0, 1, 1, 0, 0]:  # Index + Middle
                return "peace_sign"
            elif fingers_up == [0, 1, 0, 0, 0]:  # Only Index
                return "point"
            elif total_fingers >= 3:
                return "open_hand"
            
            return None
            
        except Exception as e:
            print(f"❌ Static gesture classification error: {e}")
            return None
    
    def _enhanced_swipe_detection(self, curr_landmarks, current_time):
        """Enhanced swipe detection with better accuracy"""
        try:
            if self.previous_landmarks is None:
                self.previous_landmarks = curr_landmarks
                return None
            
            # Use index finger tip for swipe detection
            prev_index = self.previous_landmarks[8]
            curr_index = curr_landmarks[8]
            
            # Calculate movement
            dx = curr_index[0] - prev_index[0]
            dy = curr_index[1] - prev_index[1]
            distance = np.sqrt(dx**2 + dy**2)
            
            # Detect swipe start
            if self.swipe_start_pos is None and distance > 0.02:
                self.swipe_start_pos = prev_index
                self.swipe_start_time = current_time
                self.previous_landmarks = curr_landmarks
                return None
            
            # Detect swipe completion
            if self.swipe_start_pos is not None:
                total_dx = curr_index[0] - self.swipe_start_pos[0]
                total_dy = curr_index[1] - self.swipe_start_pos[1]
                total_distance = np.sqrt(total_dx**2 + total_dy**2)
                
                # Check if swipe is complete
                if total_distance > self.min_swipe_distance:
                    gesture = None
                    
                    # Determine swipe direction
                    if abs(total_dx) > abs(total_dy):
                        if total_dx > self.swipe_threshold:
                            gesture = "swipe_right"
                        elif total_dx < -self.swipe_threshold:
                            gesture = "swipe_left"
                    else:
                        if total_dy < -self.swipe_threshold:
                            gesture = "swipe_up"
                        elif total_dy > self.swipe_threshold:
                            gesture = "swipe_down"
                    
                    # Reset swipe tracking
                    self.swipe_start_pos = None
                    self.previous_landmarks = curr_landmarks
                    return gesture
                
                # Reset if swipe takes too long
                if current_time - self.swipe_start_time > 2.0:
                    self.swipe_start_pos = None
            
            self.previous_landmarks = curr_landmarks
            return None
            
        except Exception as e:
            print(f"❌ Enhanced swipe detection error: {e}")
            return None
    
    def _smooth_gesture(self, gesture):
        """Smooth gesture detection to reduce noise"""
        self.gesture_history.append(gesture)
        
        # Keep only last 5 detections
        if len(self.gesture_history) > 5:
            self.gesture_history = self.gesture_history[-5:]
        
        # Return gesture only if detected consistently
        if len(self.gesture_history) >= 3:
            recent_gestures = self.gesture_history[-3:]
            if recent_gestures.count(gesture) >= 2:
                return gesture
        
        return None
    
    def _is_gesture_valid(self, gesture, current_time):
        """Check if gesture is valid (not too frequent)"""
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return False
        return True
    
    def _draw_enhanced_landmarks(self, frame, hand_landmarks):
        """Draw enhanced landmarks with gesture indicators"""
        # Draw hand landmarks
        self.mp_drawing.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )
        
        # Draw swipe indicator
        if self.swipe_start_pos is not None:
            h, w, _ = frame.shape
            start_x = int(self.swipe_start_pos[0] * w)
            start_y = int(self.swipe_start_pos[1] * h)
            cv2.circle(frame, (start_x, start_y), 10, (0, 255, 255), -1)
    
    def _add_instruction_text(self, frame):
        """Add instruction text to frame"""
        instructions = [
            "Gestures:",
            "Swipe Right -> Start Irrigation",
            "Swipe Left -> Stop Irrigation", 
            "Palm Up -> Status Check",
            "Thumbs Up -> Confirm",
            "Peace Sign -> Emergency Stop",
            "Press 'q' to quit"
        ]
        
        y_offset = 30
        for i, instruction in enumerate(instructions):
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            cv2.putText(frame, instruction, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def get_gesture(self):
        """Get the latest detected gesture"""
        try:
            return self.gesture_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_detection(self):
        """Stop gesture detection"""
        self.is_detecting = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🚫 Enhanced gesture detection stopped")
    
    def __del__(self):
        """Cleanup resources"""
        self.stop_detection()
