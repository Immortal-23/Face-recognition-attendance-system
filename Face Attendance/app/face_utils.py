import cv2
import numpy as np
import base64
from deepface import DeepFace
from .models import Student, db
import os
import threading
import time
from flask import current_app
from datetime import datetime

class WebcamFaceRecognition:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, app=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WebcamFaceRecognition, cls).__new__(cls)
                cls._instance.initialized = False
            return cls._instance

    def __init__(self, app=None):
        if not self.initialized:
            self.cap = None
            self.is_running = False
            self.current_frame = None
            self.face_detected = False
            self.recognized_student = None
            self.last_recognition_time = 0
            self.recognition_cooldown = 2  # seconds between recognitions
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.app = app
            self._frame_lock = threading.Lock()
            self.initialized = True

    def start(self):
        """Start webcam capture"""
        with self._lock:
            if self.cap is None:
                try:
                    self.cap = cv2.VideoCapture(0)
                    if not self.cap.isOpened():
                        raise Exception("Could not open webcam")
                    self.is_running = True
                    self.processing_thread = threading.Thread(target=self._process_frames, daemon=True)
                    self.processing_thread.start()
                except Exception as e:
                    print(f"Error starting webcam: {str(e)}")
                    self.stop()
                    raise

    def stop(self):
        """Stop webcam capture"""
        with self._lock:
            self.is_running = False
            if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
                if threading.current_thread() != self.processing_thread:
                    self.processing_thread.join(timeout=1.0)
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            with self._frame_lock:
                self.current_frame = None
                self.face_detected = False
                self.recognized_student = None

    def _process_frames(self):
        """Process frames from webcam"""
        while self.is_running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    print("Webcam not available")
                    break

                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break

                # Mirror the frame
                frame = cv2.flip(frame, 1)

                # Detect face
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                with self._frame_lock:
                    self.face_detected = len(faces) > 0

                # Draw rectangle around face
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Try to recognize face if enough time has passed
                current_time = time.time()
                if self.face_detected and (current_time - self.last_recognition_time) > self.recognition_cooldown:
                    try:
                        # Extract face region
                        x, y, w, h = faces[0]
                        face_img = frame[y:y+h, x:x+w]
                        
                        # Get embedding
                        embedding_result = DeepFace.represent(face_img, model_name='VGG-Face', enforce_detection=False)
                        
                        if embedding_result and self.app:
                            # Extract the embedding vector from the result
                            embedding = np.array(embedding_result[0]['embedding'])
                            print(f"Generated embedding shape: {embedding.shape}")
                            
                            # Compare with database
                            with self.app.app_context():
                                students = Student.query.all()
                                min_distance = float('inf')
                                matched_student = None

                                for student in students:
                                    stored_embedding = student.get_face_embedding()
                                    print(f"Stored embedding shape for student {student.name}: {stored_embedding.shape}")
                                    distance = np.linalg.norm(embedding - stored_embedding)
                                    print(f"Distance for student {student.name}: {distance}")
                                    
                                    if distance < min_distance and distance < 0.4:
                                        min_distance = distance
                                        matched_student = student

                                with self._frame_lock:
                                    self.recognized_student = matched_student
                                    if matched_student:
                                        print(f"Recognized student: {matched_student.name} with distance: {min_distance}")
                                    else:
                                        print("No student matched within threshold")
                                    self.last_recognition_time = current_time

                    except Exception as e:
                        print(f"Recognition error: {str(e)}")

                # Add recognition result to frame
                if self.recognized_student:
                    cv2.putText(frame, f"Welcome, {self.recognized_student.name}!", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif self.face_detected:
                    cv2.putText(frame, "Face detected - Not recognized", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                with self._frame_lock:
                    self.current_frame = frame

            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                break

        self.stop()

    def get_frame(self):
        """Get current frame with annotations"""
        with self._frame_lock:
            return self.current_frame

    def is_face_detected(self):
        """Check if face is currently detected"""
        with self._frame_lock:
            return self.face_detected

    def get_recognized_student(self):
        """Get currently recognized student"""
        with self._frame_lock:
            return self.recognized_student

def detect_face(image_data):
    """Detect face in base64 image data"""
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Convert base64 to image
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, "Failed to decode image"
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None, "No face detected"
            
        if len(faces) > 1:
            return None, "Multiple faces detected"
            
        # Get the face region
        x, y, w, h = faces[0]
        face_img = img[y:y+h, x:x+w]
        
        # Check face quality
        quality_ok, message = check_face_quality(face_img)
        if not quality_ok:
            return None, message
            
        return face_img, "Success"
        
    except Exception as e:
        return None, str(e)

def check_face_quality(face_img):
    """Check if face image meets quality requirements"""
    try:
        # Check image size
        if face_img.shape[0] < 100 or face_img.shape[1] < 100:
            return False, "Face too small. Please move closer to the camera."
            
        # Check brightness
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        if brightness < 40:
            return False, "Image too dark. Please ensure better lighting."
        if brightness > 250:
            return False, "Image too bright. Please reduce lighting."
            
        # Check blur
        laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian < 100:
            return False, "Image is blurry. Please stay still and ensure good focus."
            
        return True, "Face quality check passed"
        
    except Exception as e:
        return False, f"Failed to check face quality: {str(e)}"

def detect_and_align_face(img):
    """Detect and align face in image"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect face using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None, "No face detected. Please ensure your face is clearly visible."
            
        # Get the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Extract face region
        face_img = img[y:y+h, x:x+w]
        
        # Resize face image to standard size
        face_img = cv2.resize(face_img, (224, 224))
        return face_img, "Face detected successfully"
        
    except Exception as e:
        print(f"Error in face detection: {str(e)}")
        return None, "Failed to detect face"

def process_image(image_data):
    """Process base64 image data and return face image"""
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Convert base64 to image
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            return None, "Failed to decode image"
        
        # Detect and align face
        face_img, message = detect_and_align_face(img)
        if face_img is None:
            return None, message
            
        # Check face quality
        quality_ok, quality_message = check_face_quality(face_img)
        if not quality_ok:
            return None, quality_message
            
        return face_img, "Success"
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None, str(e)

def verify_face_for_registration(image_data):
    """Process and verify face image for registration"""
    try:
    # Convert base64 to image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect face using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None, "No face detected"
            
        if len(faces) > 1:
            return None, "Multiple faces detected"
            
        # Get face embedding using DeepFace
        x, y, w, h = faces[0]
        face_img = image[y:y+h, x:x+w]
        embedding_result = DeepFace.represent(face_img, model_name='VGG-Face', enforce_detection=False)
        
        if not embedding_result:
            return None, "Failed to generate face embedding"
            
        embedding = np.array(embedding_result[0]['embedding'])
        return embedding, "Success"
        
    except Exception as e:
        return None, str(e)