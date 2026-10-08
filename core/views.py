from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from .models import Dataset
from analytics.analyzer import DataAnalyzer
from analytics.ai_summary import generate_ai_summary
from analytics.pdf import generate_pdf
from ml_engine.trainer import ModelTrainer


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
            context['time_chart'] = analyzer.get_time_series_chart()
            context['correlation_chart'] = analyzer.get_correlation_heatmap()
            context['quality'] = analyzer.get_data_quality()
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

        context = {
            'email_sent': True,
            'dataset_id': dataset_id,
            'dataset_name': latest_dataset.name,
        }
        try:
            context['head'] = analyzer.get_head()
            context['columns'] = analyzer.get_columns()
            context['chart'] = analyzer.get_chart()
            context['time_chart'] = analyzer.get_time_series_chart()
            context['correlation_chart'] = analyzer.get_correlation_heatmap()
            context['quality'] = analyzer.get_data_quality()
            context['ai_summary'] = generate_ai_summary(analyzer)
        except:
            pass
        return render(request, 'core/dashboard.html', context)

    return redirect('dashboard_with_id', dataset_id=dataset_id)