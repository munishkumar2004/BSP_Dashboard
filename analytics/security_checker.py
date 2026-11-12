import os
from nsfw_image_detector import NSFWDetector
from detectzoo import load_detector
from PIL import Image

class SecurityChecker:
    def __init__(self):
        self.nsfw_detector = None
        self.ai_image_detector = None
        self.ai_video_detector = None
        self.ai_audio_detector = None

    def _load_image_models(self):
        if self.nsfw_detector is None:
            print("DEBUG: Loading NSFW Detector...")
            self.nsfw_detector = NSFWDetector()
        if self.ai_image_detector is None:
            print("DEBUG: Loading Image AI Detector...")
            self.ai_image_detector = load_detector("aeroblade")

    def _load_video_models(self):
        if self.ai_video_detector is None:
            print("DEBUG: Loading Video AI Detector...")
            try:
                self.ai_video_detector = load_detector("c2p_clip_deepfake")
                print("DEBUG: Video AI Detector Loaded Successfully!")
            except Exception as e:
                print(f"DEBUG ERROR: Failed to load Video Model -> {e}")
                self.ai_video_detector = None

    def _load_audio_models(self):
        if self.ai_audio_detector is None:
            print("DEBUG: Loading Audio AI Detector...")
            try:
                self.ai_audio_detector = load_detector("xlsr_sls_deepfake")
                print("DEBUG: Audio AI Detector Loaded Successfully!")
            except Exception as e:
                print(f"DEBUG ERROR: Failed to load Audio Model -> {e}")
                self.ai_audio_detector = None

    def check_image_safety(self, image_path):
        try:
            self._load_image_models() 
            
            # 1. NSFW Check
            image = Image.open(image_path)
            if self.nsfw_detector and self.nsfw_detector.is_nsfw(image):
                return False, "Sensitive/NSFW content detected. Upload rejected."

            # 2. AI-Generated Image Check
            if self.ai_image_detector:
                print("DEBUG: Running Image AI Prediction...")
                result = self.ai_image_detector.predict(image_path)
                print(f"DEBUG: Image AI Result -> Label: {result.label}, Confidence: {result.confidence}")
                
                if result.label.lower() == "ai" and result.confidence > 0.50:
                    return False, f"AI-generated image detected (Confidence: {result.confidence*100:.1f}%). Analysis not allowed."

            return True, "Real image. Ready for analysis."
        except Exception as e:
            print(f"DEBUG ERROR (Image): {str(e)}")
            return True, f"Security check skipped: {str(e)}"

    def check_video_safety(self, video_path):
        try:
            self._load_video_models()
            
            if self.ai_video_detector:
                print("DEBUG: Running Video AI Prediction...")
                result = self.ai_video_detector.predict(video_path)
                print(f"DEBUG: Video AI Result -> Label: {result.label}, Confidence: {result.confidence}")
                
                # Agar 50% se zyada AI hai, toh reject karo
                if result.label.lower() == "ai" and result.confidence > 0.50:
                    return False, f"AI-generated/Deepfake video detected. Analysis not allowed."
            else:
                 print("DEBUG: Video Model not loaded, skipping check.")

            return True, "Real video. Ready for analysis."
        except Exception as e:
            print(f"DEBUG ERROR (Video): {str(e)}")
            # Agar error aata hai, toh safe maan lo, par print zaroor karo
            return True, f"Video security check skipped: {str(e)}"

    def check_audio_safety(self, audio_path):
        try:
            self._load_audio_models()
            
            if self.ai_audio_detector:
                print("DEBUG: Running Audio AI Prediction...")
                result = self.ai_audio_detector.predict(audio_path)
                print(f"DEBUG: Audio AI Result -> Label: {result.label}, Confidence: {result.confidence}")
                
                if result.label.lower() == "ai" and result.confidence > 0.50:
                    return False, f"AI-generated voice detected. Analysis not allowed."
            else:
                 print("DEBUG: Audio Model not loaded, skipping check.")
                 
            return True, "Real audio. Ready for analysis."
        except Exception as e:
            print(f"DEBUG ERROR (Audio): {str(e)}")
            return True, f"Audio security check skipped: {str(e)}"