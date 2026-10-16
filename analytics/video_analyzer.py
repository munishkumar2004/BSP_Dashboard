import os
import cv2
import tempfile

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path

    def get_basic_info(self):
        """Video metadata"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            cap.release()

            return {
                'file_name': os.path.basename(self.video_path),
                'size_kb': round(os.path.getsize(self.video_path) / 1024, 2),
                'format': os.path.splitext(self.video_path)[1].replace('.', '').upper(),
                'duration_sec': round(duration, 2),
                'fps': round(fps, 2),
                'frame_count': frame_count,
                'resolution': f"{width} × {height}"
            }
        except Exception as e:
            return {'error': str(e)}

    def extract_frames(self, num_frames=5):
        """5 sample frames extract karo (evenly spaced)"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                return []

            # Evenly spaced frame indices
            step = max(1, total_frames // num_frames)
            frame_indices = [i * step for i in range(num_frames) if i * step < total_frames]

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Temp file mein save karo
                    temp_path = os.path.join(tempfile.gettempdir(), f"frame_{idx}.jpg")
                    cv2.imwrite(temp_path, frame)
                    frames.append({
                        'index': idx,
                        'path': temp_path,
                        'timestamp': round(idx / max(1, cap.get(cv2.CAP_PROP_FPS)), 2)
                    })

            cap.release()
            return frames
        except Exception as e:
            return []

    def detect_objects_in_frames(self):
        """Har frame mein objects detect karo"""
        if not YOLO_AVAILABLE:
            return {'error': 'YOLO not installed', 'detections': []}

        frames = self.extract_frames(num_frames=5)
        if not frames:
            return {'error': 'Could not extract frames', 'detections': []}

        try:
            model = YOLO('yolov8n.pt')
            all_detections = []

            for frame_info in frames:
                results = model(frame_info['path'])
                frame_objects = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = model.names[cls]
                        if conf > 0.4:  # Sirf confident detections
                            frame_objects.append({
                                'label': label,
                                'confidence': round(conf * 100, 2)
                            })

                all_detections.append({
                    'timestamp': frame_info['timestamp'],
                    'frame_index': frame_info['index'],
                    'objects': frame_objects,
                    'count': len(frame_objects)
                })

            # Clean up temp files
            for f in frames:
                try:
                    os.remove(f['path'])
                except:
                    pass

            # Unique objects across all frames
            all_labels = []
            for d in all_detections:
                for obj in d['objects']:
                    all_labels.append(obj['label'])
            unique_objects = list(set(all_labels))

            return {
                'detections': all_detections,
                'unique_objects': unique_objects,
                'total_unique': len(unique_objects)
            }
        except Exception as e:
            return {'error': str(e), 'detections': []}

    def transcribe_audio(self):
        """Video ka audio transcribe karo Whisper se"""
        if not WHISPER_AVAILABLE:
            return {'error': 'Whisper not installed', 'text': ''}

        try:
            model = whisper.load_model("base")
            result = model.transcribe(self.video_path, fp16=False)
            text = result.get('text', '').strip()
            language = result.get('language', 'unknown')

            return {
                'text': text,
                'language': language,
                'word_count': len(text.split())
            }
        except Exception as e:
            return {'error': str(e), 'text': ''}

    def get_analysis(self):
        """Sab kuch ek saath"""
        return {
            'basic': self.get_basic_info(),
            'detections': self.detect_objects_in_frames(),
            'transcription': self.transcribe_audio()
        }