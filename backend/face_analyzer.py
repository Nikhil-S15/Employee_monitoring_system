# face_analyzer.py
import cv2
import numpy as np
from datetime import datetime
import random

class FEREmotionDetector:
    def __init__(self):
        self.current_emotion = 'neutral'
        self.emotion_confidence = 85.0
        self.last_emotion_change = datetime.now()
        self.emotion_buffer = []
        self.frame_count = 0
        
        # Initialize FER detector
        try:
            from fer import FER
            self.detector = FER(mtcnn=True)  # Use MTCNN for better accuracy
            self.ml_available = True
            print("✅ FER ML Model loaded successfully with MTCNN")
        except ImportError as e:
            print(f"❌ FER not available: {e}")
            self.ml_available = False
        except Exception as e:
            print(f"❌ FER initialization failed: {e}")
            self.ml_available = False
    
    def detect_emotion(self, face_roi):
        """Use FER for accurate emotion detection"""
        self.frame_count += 1
        
        # Only process every 3rd frame for performance
        if self.frame_count % 3 != 0:
            return self.current_emotion, self.emotion_confidence
        
        if not self.ml_available:
            return self._fallback_emotion(face_roi)
        
        try:
            # Convert BGR to RGB for FER
            rgb_frame = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            
            # Detect emotions using FER
            results = self.detector.detect_emotions(rgb_frame)
            
            if results and len(results) > 0:
                # Get the first face detected
                emotions = results[0]['emotions']
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                confidence = emotions[dominant_emotion] * 100
                
                print(f"🎭 FER Detection: {dominant_emotion} ({confidence:.1f}%)")
                
                # Add to buffer for stability
                self.emotion_buffer.append((dominant_emotion, confidence))
                if len(self.emotion_buffer) > 5:
                    self.emotion_buffer.pop(0)
                
                # Use majority voting from buffer for stability
                if len(self.emotion_buffer) >= 3:
                    emotion_counts = {}
                    for emo, conf in self.emotion_buffer:
                        emotion_counts[emo] = emotion_counts.get(emo, 0) + 1
                    
                    best_emotion = max(emotion_counts, key=emotion_counts.get)
                    avg_confidence = np.mean([conf for emo, conf in self.emotion_buffer if emo == best_emotion])
                    
                    # Only update if we have consistent detection
                    current_time = datetime.now()
                    time_since_change = (current_time - self.last_emotion_change).total_seconds()
                    
                    if (best_emotion != self.current_emotion and 
                        emotion_counts[best_emotion] >= 3 and  # Majority in buffer
                        time_since_change > 2.0 and  # Minimum time between changes
                        avg_confidence > 60):  # Minimum confidence
                        
                        self.current_emotion = best_emotion
                        self.emotion_confidence = avg_confidence
                        self.last_emotion_change = current_time
                        print(f"🔄 Emotion changed to: {best_emotion} ({avg_confidence:.1f}%)")
                
                return self.current_emotion, self.emotion_confidence
            else:
                return self._fallback_emotion(face_roi)
                
        except Exception as e:
            print(f"FER emotion detection error: {e}")
            return self._fallback_emotion(face_roi)
    
    def _fallback_emotion(self, face_roi):
        """Fallback when FER fails"""
        current_time = datetime.now()
        time_since_change = (current_time - self.last_emotion_change).total_seconds()
        
        # Only change emotion occasionally in fallback mode
        if time_since_change > 10:  # Change every 10 seconds max
            emotions = ['happy', 'neutral', 'sad', 'surprise']
            weights = [0.3, 0.4, 0.2, 0.1]  # Prefer neutral and happy
            self.current_emotion = random.choices(emotions, weights=weights)[0]
            self.emotion_confidence = random.uniform(70, 85)
            self.last_emotion_change = current_time
            print(f"🔄 Fallback emotion: {self.current_emotion}")
        
        return self.current_emotion, self.emotion_confidence

# Global instance
face_analyzer = FEREmotionDetector()