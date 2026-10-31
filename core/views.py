from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.cache import cache
from io import BytesIO
import os
import pandas as pd
from .models import Dataset, ImageDataset, AudioDataset, VideoDataset
from analytics.analyzer import DataAnalyzer
from analytics.ai_summary import generate_ai_summary
from analytics.pdf import generate_pdf
from analytics.cleaner import DataCleaner
from analytics.image_analyzer import ImageAnalyzer
from analytics.audio_analyzer import AudioAnalyzer
from analytics.video_analyzer import VideoAnalyzer
from ml_engine.trainer import ModelTrainer

# ============================================================
# 🟢 HELPER FUNCTION (Synchronous Processing - No Celery)
# ============================================================
def process_media_upload(request, file_key, model_class, field_name, analyzer_class, allowed_exts, media_type):
    # 🟢 FIX: Agar page sirf khula hai (GET request), toh upload form dikhao, redirect mat karo
    if request.method == 'GET':
        return render(request, f'core/upload_{media_type}.html')

    if request.method == 'POST' and request.FILES.get(file_key):
        uploaded_file = request.FILES[file_key]
        
        # 1. Validation
        if not uploaded_file.name.lower().endswith(allowed_exts):
            messages.error(request, f"Invalid {media_type} format! Upload {', '.join(allowed_exts)}.")
            return redirect(request.path)
            
        # 50MB limit for all files
        if uploaded_file.size > 50 * 1024 * 1024:
            messages.error(request, f"File too large! Maximum allowed size is 50MB.")
            return redirect(request.path)

        # 2. Save to Database
        try:
            kwargs = {field_name: uploaded_file}
            instance = model_class(name=uploaded_file.name, **kwargs)
            if request.user.is_authenticated:
                instance.user = request.user
            instance.save()
        except Exception as e:
            messages.error(request, f"Upload failed. Server error: {str(e)[:80]}")
            return redirect(request.path)

        # 3. Process Analysis (DIRECTLY - Synchronous)
        try:
            cache.set(f'{media_type}_status_{instance.id}', 'processing', timeout=3600)
            
            file_path = getattr(instance, field_name).path
            analyzer = analyzer_class(file_path)
            analysis = analyzer.get_analysis()
            
            cache.set(f'{media_type}_result_{instance.id}', analysis, timeout=3600)
            cache.set(f'{media_type}_status_{instance.id}', 'completed', timeout=3600)
            messages.success(request, f"{media_type.capitalize()} analyzed successfully!")
        except Exception as e:
            cache.set(f'{media_type}_status_{instance.id}', f'failed: {str(e)}', timeout=3600)
            messages.error(request, f"{media_type.capitalize()} analysis failed: {str(e)}")

        # 4. Redirect to Detail page
        redirect_kwargs = {f'{media_type}_id': instance.id}
        return redirect(f'{media_type}_detail', **redirect_kwargs)

    return redirect(request.path)

# ============================================================
# TABULAR DATA VIEWS
# ============================================================

@login_required(login_url='login')
def dataset_list_view(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'core/dataset_list.html', {'datasets': datasets})

@login_required(login_url='login')
def dashboard_view(request, dataset_id=None):
    context = {
        'image_count': ImageDataset.objects.count(),
        'audio_count': AudioDataset.objects.count(),
        'video_count': VideoDataset.objects.count(),
    }
    
    if not dataset_id:
        return render(request, 'core/upload.html', context)

    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    try:
        analyzer = DataAnalyzer(latest_dataset.file.path)
        context['summary'] = analyzer.get_summary()
        context['head'] = analyzer.get_head()
        context['columns'] = analyzer.get_columns()
        context['dataset_name'] = latest_dataset.name
        context['dataset_id'] = latest_dataset.id
        context['chart'] = analyzer.get_chart()
        context['time_chart'] = analyzer.get_time_series_chart()
        context['correlation_chart'] = analyzer.get_correlation_heatmap()
        context['quality'] = analyzer.get_data_quality()
        context['text_analysis'] = analyzer.get_text_analysis()
        context['spotify_chart'] = analyzer.get_popularity_vs_danceability_chart()
        context['ai_summary'] = generate_ai_summary(analyzer)
    except Exception as e:
        context['error'] = str(e)
        
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='login')
def upload_dataset(request):
    if request.method == 'POST' and request.FILES.get('dataset_file'):
        uploaded_file = request.FILES['dataset_file']
        
        if not uploaded_file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
            messages.error(request, "Invalid file type! Please upload CSV or Excel file only.")
            return redirect('dashboard')
            
        if uploaded_file.size > 50 * 1024 * 1024:
            messages.error(request, "File too large! Maximum allowed size is 50MB.")
            return redirect('dashboard')

        try:
            dataset = Dataset(name=uploaded_file.name, file=uploaded_file)
            if request.user.is_authenticated:
                dataset.user = request.user
            dataset.save()
            messages.success(request, "Dataset uploaded successfully! Analysis is ready.")
            return redirect('dashboard_with_id', dataset_id=dataset.id)
        except Exception as e:
            messages.error(request, f"Upload failed. Server error: {str(e)[:80]}")
            return redirect('dashboard')
            
    return redirect('dashboard')

@login_required(login_url='login')
def train_model_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    trainer = ModelTrainer(latest_dataset.file.path)
    
    target_col = request.POST.get('target_column') if request.method == 'POST' else None
    result, error = trainer.train(target_col=target_col)

    if error:
        messages.error(request, f"Training failed: {error}")
        return redirect('dashboard_with_id', dataset_id=dataset_id)

    messages.success(request, f"Model trained successfully using {result['best_algorithm']}!")
    request.session['ml_result'] = result
    return redirect('dashboard_with_id', dataset_id=dataset_id)

@login_required(login_url='login')
def download_report_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    analyzer = DataAnalyzer(latest_dataset.file.path)
    ml_result = request.session.get('ml_result', {})
    context = {
        'dataset_name': latest_dataset.name,
        'columns': analyzer.get_columns(),
        'head': analyzer.get_pdf_table(),
        'ml_score': ml_result.get('best_score', 'Not Trained Yet'),
        'best_algorithm': ml_result.get('best_algorithm', 'Not Trained Yet'),
    }
    pdf = generate_pdf(context)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{latest_dataset.name}.pdf"'
    return response

@login_required(login_url='login')
def email_report_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    analyzer = DataAnalyzer(latest_dataset.file.path)
    ml_result = request.session.get('ml_result', {})
    context = {
        'dataset_name': latest_dataset.name,
        'columns': analyzer.get_columns(),
        'head': analyzer.get_pdf_table(),
        'ml_score': ml_result.get('best_score', 'Not Trained Yet'),
        'best_algorithm': ml_result.get('best_algorithm', 'Not Trained Yet'),
    }
    pdf = generate_pdf(context)

    if pdf:
        subject = f"BSP Dashboard Report: {latest_dataset.name}"
        body = f"Hello,\n\nPlease find attached the analysis report for {latest_dataset.name}.\n\nRegards,\nBSP Dashboard Team"
        to_email = request.user.email if request.user.email else 'test@example.com'
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.attach(f"report_{latest_dataset.name}.pdf", pdf, 'application/pdf')
        email.send()
        messages.success(request, "Email sent successfully! Check terminal.")
        return redirect('dashboard_with_id', dataset_id=dataset_id)
    return redirect('dashboard_with_id', dataset_id=dataset_id)

@login_required(login_url='login')
def merge_datasets_view(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_datasets')
        if len(selected_ids) < 2:
            messages.warning(request, "Please select at least 2 datasets to merge.")
            return redirect('merge_datasets')
        try:
            dfs = []
            for did in selected_ids:
                ds = Dataset.objects.get(id=did)
                if str(ds.file.path).endswith('.csv'):
                    df = pd.read_csv(ds.file.path, on_bad_lines='skip')
                else:
                    df = pd.read_excel(ds.file.path)
                dfs.append(df)
            merged_df = pd.concat(dfs, ignore_index=True)
            csv_buffer = BytesIO()
            merged_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            filename = f"merged_{len(selected_ids)}files.csv"
            new_dataset = Dataset(name=filename)
            new_dataset.file.save(filename, ContentFile(csv_buffer.read()))
            if request.user.is_authenticated:
                new_dataset.user = request.user
            new_dataset.save()
            messages.success(request, "Datasets merged successfully!")
            return redirect('dashboard_with_id', dataset_id=new_dataset.id)
        except Exception as e:
            messages.error(request, f"Merge failed: {str(e)}")
            return redirect('merge_datasets')
    return render(request, 'core/merge_datasets.html', {'datasets': datasets})

@login_required(login_url='login')
def clean_data_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    analyzer = DataAnalyzer(latest_dataset.file.path)
    if request.method == 'POST':
        cleaner = DataCleaner(latest_dataset.file.path)
        if request.POST.get('remove_duplicates'): cleaner.remove_duplicates()
        if request.POST.get('fill_numeric'): cleaner.fill_numeric_missing()
        if request.POST.get('fill_text'): cleaner.fill_text_missing()
        if request.POST.get('drop_missing'): cleaner.drop_missing_rows()
        csv_buffer = BytesIO()
        cleaner.df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        base_name = latest_dataset.name.rsplit('.', 1)[0] if '.' in latest_dataset.name else latest_dataset.name
        filename = f"cleaned_{base_name}.csv"
        new_dataset = Dataset(name=filename)
        new_dataset.file.save(filename, ContentFile(csv_buffer.read()))
        if request.user.is_authenticated:
            new_dataset.user = request.user
        new_dataset.save()
        messages.success(request, "Data cleaned and saved successfully!")
        return redirect('dashboard_with_id', dataset_id=new_dataset.id)
    return render(request, 'core/clean_data.html', {
        'dataset': latest_dataset, 'dataset_id': dataset_id, 'quality': analyzer.get_data_quality()
    })

# ============================================================
# MEDIA UPLOADS (Using Helper + Synchronous Processing)
# ============================================================

@login_required(login_url='login')
def upload_image_view(request):
    return process_media_upload(request, 'image_file', ImageDataset, 'image', ImageAnalyzer, ('.jpg', '.jpeg', '.png', '.bmp', '.webp'), 'image')

@login_required(login_url='login')
def upload_audio_view(request):
    return process_media_upload(request, 'audio_file', AudioDataset, 'audio', AudioAnalyzer, ('.mp3', '.wav', '.m4a', '.ogg', '.flac'), 'audio')

@login_required(login_url='login')
def upload_video_view(request):
    return process_media_upload(request, 'video_file', VideoDataset, 'video', VideoAnalyzer, ('.mp4', '.avi', '.mov', '.mkv', '.webm'), 'video')

# Detail Views
@login_required(login_url='login')
def image_detail_view(request, image_id):
    img = get_object_or_404(ImageDataset, id=image_id)
    return render(request, 'core/image_detail.html', {'image': img, 'analysis': cache.get(f'image_result_{image_id}'), 'status': cache.get(f'image_status_{image_id}', 'pending')})

@login_required(login_url='login')
def audio_detail_view(request, audio_id):
    audio = get_object_or_404(AudioDataset, id=audio_id)
    return render(request, 'core/audio_detail.html', {'audio': audio, 'analysis': cache.get(f'audio_result_{audio_id}'), 'status': cache.get(f'audio_status_{audio_id}', 'pending')})

@login_required(login_url='login')
def video_detail_view(request, video_id):
    video = get_object_or_404(VideoDataset, id=video_id)
    return render(request, 'core/video_detail.html', {'video': video, 'analysis': cache.get(f'video_result_{video_id}'), 'status': cache.get(f'video_status_{video_id}', 'pending')})

# Delete Views
@login_required(login_url='login')
def delete_dataset_view(request, dataset_id):
    if request.method == 'POST':
        get_object_or_404(Dataset, id=dataset_id).delete()
        messages.warning(request, "Dataset deleted successfully.")
    return redirect('dataset_list')

@login_required(login_url='login')
def delete_image_view(request, image_id):
    if request.method == 'POST':
        get_object_or_404(ImageDataset, id=image_id).delete()
        messages.warning(request, "Image deleted successfully.")
    return redirect('image_list')

@login_required(login_url='login')
def delete_audio_view(request, audio_id):
    if request.method == 'POST':
        get_object_or_404(AudioDataset, id=audio_id).delete()
        messages.warning(request, "Audio deleted successfully.")
    return redirect('audio_list')

@login_required(login_url='login')
def delete_video_view(request, video_id):
    if request.method == 'POST':
        get_object_or_404(VideoDataset, id=video_id).delete()
        messages.warning(request, "Video deleted successfully.")
    return redirect('video_list')

# List Views
@login_required(login_url='login')
def image_list_view(request):
    return render(request, 'core/image_list.html', {'images': ImageDataset.objects.all().order_by('-uploaded_at')})

@login_required(login_url='login')
def audio_list_view(request):
    return render(request, 'core/audio_list.html', {'audios': AudioDataset.objects.all().order_by('-uploaded_at')})

@login_required(login_url='login')
def video_list_view(request):
    return render(request, 'core/video_list.html', {'videos': VideoDataset.objects.all().order_by('-uploaded_at')})