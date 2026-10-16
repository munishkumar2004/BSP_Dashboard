import os
from PIL import Image
import numpy as np

# Try to import optional libraries gracefully
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class ImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img = Image.open(image_path)

    def get_basic_info(self):
        """Basic image info: size, format, mode"""
        return {
            'width': self.img.width,
            'height': self.img.height,
            'format': self.img.format or 'Unknown',
            'mode': self.img.mode,
            'size_kb': round(os.path.getsize(self.image_path) / 1024, 2)
        }

    def get_color_analysis(self):
        """Dominant colors nikalna"""
        # Image ko RGB mein convert karo
        img_rgb = self.img.convert('RGB')
        # Small size mein resize (fast processing)
        img_small = img_rgb.resize((100, 100))
        pixels = np.array(img_small).reshape(-1, 3)

        # Average color
        avg_color = pixels.mean(axis=0).astype(int)

        # Most common color (quantize karke)
        quantized = (pixels // 32) * 32  # Reduce color space
        unique, counts = np.unique(quantized, axis=0, return_counts=True)
        top_indices = counts.argsort()[-5:][::-1]
        top_colors = [tuple(unique[i]) for i in top_indices]

        return {
            'average_color': tuple(avg_color),
            'average_hex': '#{:02x}{:02x}{:02x}'.format(*avg_color),
            'top_colors': ['#{:02x}{:02x}{:02x}'.format(*c) for c in top_colors]
        }

    def detect_objects(self):
        """YOLO se objects detect karo"""
        if not YOLO_AVAILABLE:
            return {'error': 'YOLO not installed', 'objects': []}

        try:
            # YOLOv8 nano model (fast, small)
            model = YOLO('yolov8n.pt')
            results = model(self.image_path)
            objects = []
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    objects.append({
                        'label': label,
                        'confidence': round(conf * 100, 2)
                    })
            return {'objects': objects, 'total': len(objects)}
        except Exception as e:
            return {'error': str(e), 'objects': []}

    def extract_text(self):
        """OCR se text nikalna"""
        if not TESSERACT_AVAILABLE:
            return {'error': 'pytesseract not installed', 'text': ''}

        try:
            text = pytesseract.image_to_string(self.img)
            return {'text': text.strip(), 'word_count': len(text.split())}
        except Exception as e:
            return {'error': str(e), 'text': ''}

    def get_analysis(self):
        """Sab kuch ek saath"""
        return {
            'basic': self.get_basic_info(),
            'colors': self.get_color_analysis(),
            'objects': self.detect_objects(),
            'text': self.extract_text()
        }