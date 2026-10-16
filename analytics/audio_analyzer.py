import os

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class AudioAnalyzer:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def get_basic_info(self):
        """Basic audio info"""
        return {
            'file_name': os.path.basename(self.audio_path),
            'size_kb': round(os.path.getsize(self.audio_path) / 1024, 2),
            'format': os.path.splitext(self.audio_path)[1].replace('.', '').upper()
        }

    def get_audio_features(self):
        """Librosa se audio features"""
        if not LIBROSA_AVAILABLE:
            return {'error': 'librosa not installed'}

        try:
            y, sr = librosa.load(self.audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)

            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            return {
                'duration_sec': round(float(duration), 2),
                'sample_rate': int(sr),
                'tempo_bpm': round(float(tempo), 2) if not hasattr(tempo, '__len__') else round(float(tempo[0]), 2),
                'samples': len(y)
            }
        except Exception as e:
            return {'error': str(e)}

    def transcribe(self):
        """Whisper se speech-to-text"""
        if not WHISPER_AVAILABLE:
            return {'error': 'Whisper not installed', 'text': ''}

        try:
            # Base model (fast, decent accuracy)
            model = whisper.load_model("base")
            result = model.transcribe(self.audio_path, language=None, fp16=False)
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
            'features': self.get_audio_features(),
            'transcription': self.transcribe()
        }