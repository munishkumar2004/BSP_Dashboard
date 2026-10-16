from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.cache import cache
from io import BytesIO
import pandas as pd
from .models import Dataset, ImageDataset, AudioDataset, VideoDataset
from .tasks import analyze_video_task, analyze_audio_task, analyze_image_task
from analytics.analyzer import DataAnalyzer
from analytics.ai_summary import generate_ai_summary
from analytics.pdf import generate_pdf
from analytics.cleaner import DataCleaner
from analytics.image_analyzer import ImageAnalyzer
from analytics.audio_analyzer import AudioAnalyzer
from analytics.video_analyzer import VideoAnalyzer
from ml_engine.trainer import ModelTrainer


# ============================================================
# TABULAR DATA VIEWS
# ============================================================

@login_required(login_url='login')
def dataset_list_view(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    return render(request, 'core/dataset_list.html', {'datasets': datasets})


@login_required(login_url='login')
def dashboard_view(request, dataset_id=None):
    context = {}
    if dataset_id:
        latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    else:
        latest_dataset = Dataset.objects.last()

    context['image_count'] = ImageDataset.objects.count()
    context['audio_count'] = AudioDataset.objects.count()
    context['video_count'] = VideoDataset.objects.count()

    if latest_dataset:
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
            context['ai_summary'] = generate_ai_summary(analyzer)
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'core/dashboard.html', context)


@login_required(login_url='login')
def upload_dataset(request):
    if request.method == 'POST' and request.FILES.get('dataset_file'):
        uploaded_file = request.FILES['dataset_file']
        dataset = Dataset(name=uploaded_file.name, file=uploaded_file)
        if request.user.is_authenticated:
            dataset.user = request.user
        dataset.save()
        return redirect('dashboard_with_id', dataset_id=dataset.id)
    return redirect('dashboard')


@login_required(login_url='login')
def train_model_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    trainer = ModelTrainer(latest_dataset.file.path)
    result, error = trainer.train()

    if error:
        context = {'error': error, 'dataset_name': latest_dataset.name, 'dataset_id': dataset_id}
        try:
            analyzer = DataAnalyzer(latest_dataset.file.path)
            context['head'] = analyzer.get_head()
            context['columns'] = analyzer.get_columns()
            context['chart'] = analyzer.get_chart()
        except:
            pass
        return render(request, 'core/dashboard.html', context)

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
        'head': analyzer.get_head(),
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
        'head': analyzer.get_head(),
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
        context = {'email_sent': True, 'dataset_id': dataset_id, 'dataset_name': latest_dataset.name}
        try:
            context['head'] = analyzer.get_head()
            context['columns'] = analyzer.get_columns()
            context['chart'] = analyzer.get_chart()
            context['ai_summary'] = generate_ai_summary(analyzer)
        except:
            pass
        return render(request, 'core/dashboard.html', context)
    return redirect('dashboard_with_id', dataset_id=dataset_id)


@login_required(login_url='login')
def merge_datasets_view(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_datasets')
        if len(selected_ids) < 2:
            return render(request, 'core/merge_datasets.html', {
                'datasets': datasets,
                'error': 'Kam se kam 2 files select karo.'
            })
        try:
            dfs = []
            for did in selected_ids:
                ds = Dataset.objects.get(id=did)
                if str(ds.file.path).endswith('.csv'):
                    df = pd.read_csv(ds.file.path)
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
            return redirect('dashboard_with_id', dataset_id=new_dataset.id)
        except Exception as e:
            return render(request, 'core/merge_datasets.html', {
                'datasets': datasets,
                'error': str(e)
            })
    return render(request, 'core/merge_datasets.html', {'datasets': datasets})


@login_required(login_url='login')
def clean_data_view(request, dataset_id):
    latest_dataset = get_object_or_404(Dataset, id=dataset_id)
    analyzer = DataAnalyzer(latest_dataset.file.path)
    if request.method == 'POST':
        cleaner = DataCleaner(latest_dataset.file.path)
        if request.POST.get('remove_duplicates'):
            cleaner.remove_duplicates()
        if request.POST.get('fill_numeric'):
            cleaner.fill_numeric_missing()
        if request.POST.get('fill_text'):
            cleaner.fill_text_missing()
        if request.POST.get('drop_missing'):
            cleaner.drop_missing_rows()
        csv_buffer = BytesIO()
        cleaner.df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        base_name = latest_dataset.name
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        filename = f"cleaned_{base_name}.csv"
        new_dataset = Dataset(name=filename)
        new_dataset.file.save(filename, ContentFile(csv_buffer.read()))
        if request.user.is_authenticated:
            new_dataset.user = request.user
        new_dataset.save()
        return redirect('dashboard_with_id', dataset_id=new_dataset.id)
    return render(request, 'core/clean_data.html', {
        'dataset': latest_dataset,
        'dataset_id': dataset_id,
        'quality': analyzer.get_data_quality()
    })


# ============================================================
# IMAGE ANALYSIS VIEWS (Background Task)
# ============================================================

@login_required(login_url='login')
def upload_image_view(request):
    if request.method == 'POST' and request.FILES.get('image_file'):
        uploaded_file = request.FILES['image_file']
        img = ImageDataset(name=uploaded_file.name, image=uploaded_file)
        if request.user.is_authenticated:
            img.user = request.user
        img.save()

        # 🟢 Background task chalao
        analyze_image_task.delay(img.id)

        return redirect('image_detail', image_id=img.id)
    return render(request, 'core/upload_image.html')


@login_required(login_url='login')
def image_detail_view(request, image_id):
    img = get_object_or_404(ImageDataset, id=image_id)
    status = cache.get(f'image_status_{image_id}', 'pending')
    analysis = cache.get(f'image_result_{image_id}')
    return render(request, 'core/image_detail.html', {
        'image': img,
        'analysis': analysis,
        'status': status
    })


# ============================================================
# AUDIO ANALYSIS VIEWS (Background Task)
# ============================================================

@login_required(login_url='login')
def upload_audio_view(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        uploaded_file = request.FILES['audio_file']
        audio = AudioDataset(name=uploaded_file.name, audio=uploaded_file)
        if request.user.is_authenticated:
            audio.user = request.user
        audio.save()

        # 🟢 Background task chalao
        analyze_audio_task.delay(audio.id)

        return redirect('audio_detail', audio_id=audio.id)
    return render(request, 'core/upload_audio.html')


@login_required(login_url='login')
def audio_detail_view(request, audio_id):
    audio = get_object_or_404(AudioDataset, id=audio_id)
    status = cache.get(f'audio_status_{audio_id}', 'pending')
    analysis = cache.get(f'audio_result_{audio_id}')
    return render(request, 'core/audio_detail.html', {
        'audio': audio,
        'analysis': analysis,
        'status': status
    })


# ============================================================
# VIDEO ANALYSIS VIEWS (Background Task)
# ============================================================

@login_required(login_url='login')
def upload_video_view(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        uploaded_file = request.FILES['video_file']
        video = VideoDataset(name=uploaded_file.name, video=uploaded_file)
        if request.user.is_authenticated:
            video.user = request.user
        video.save()

        # 🟢 Background task chalao
        analyze_video_task.delay(video.id)

        return redirect('video_detail', video_id=video.id)
    return render(request, 'core/upload_video.html')


@login_required(login_url='login')
def video_detail_view(request, video_id):
    video = get_object_or_404(VideoDataset, id=video_id)
    status = cache.get(f'video_status_{video_id}', 'pending')
    analysis = cache.get(f'video_result_{video_id}')
    return render(request, 'core/video_detail.html', {
        'video': video,
        'analysis': analysis,
        'status': status
    })