from celery import shared_task
from django.core.cache import cache
import os


@shared_task(bind=True)
def analyze_video_task(self, video_id):
    """Video analysis background mein chalao"""
    from .models import VideoDataset
    from analytics.video_analyzer import VideoAnalyzer

    try:
        video = VideoDataset.objects.get(id=video_id)
        cache.set(f'video_status_{video_id}', 'processing', timeout=3600)

        analyzer = VideoAnalyzer(video.video.path)
        analysis = analyzer.get_analysis()

        cache.set(f'video_result_{video_id}', analysis, timeout=3600)
        cache.set(f'video_status_{video_id}', 'completed', timeout=3600)

        return {'status': 'success', 'video_id': video_id}
    except Exception as e:
        cache.set(f'video_status_{video_id}', f'failed: {str(e)}', timeout=3600)
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def analyze_audio_task(self, audio_id):
    """Audio analysis background mein chalao"""
    from .models import AudioDataset
    from analytics.audio_analyzer import AudioAnalyzer

    try:
        audio = AudioDataset.objects.get(id=audio_id)
        cache.set(f'audio_status_{audio_id}', 'processing', timeout=3600)

        analyzer = AudioAnalyzer(audio.audio.path)
        analysis = analyzer.get_analysis()

        cache.set(f'audio_result_{audio_id}', analysis, timeout=3600)
        cache.set(f'audio_status_{audio_id}', 'completed', timeout=3600)

        return {'status': 'success', 'audio_id': audio_id}
    except Exception as e:
        cache.set(f'audio_status_{audio_id}', f'failed: {str(e)}', timeout=3600)
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def analyze_image_task(self, image_id):
    """Image analysis background mein chalao"""
    from .models import ImageDataset
    from analytics.image_analyzer import ImageAnalyzer

    try:
        image = ImageDataset.objects.get(id=image_id)
        cache.set(f'image_status_{image_id}', 'processing', timeout=3600)

        analyzer = ImageAnalyzer(image.image.path)
        analysis = analyzer.get_analysis()

        cache.set(f'image_result_{image_id}', analysis, timeout=3600)
        cache.set(f'image_status_{image_id}', 'completed', timeout=3600)

        return {'status': 'success', 'image_id': image_id}
    except Exception as e:
        cache.set(f'image_status_{image_id}', f'failed: {str(e)}', timeout=3600)
        return {'status': 'failed', 'error': str(e)}