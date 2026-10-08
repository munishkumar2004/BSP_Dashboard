# pyright: reportMissingModuleSource=false
from django.shortcuts import render, redirect
from core.models import Dataset

def dashboard_view(request):
    # Dashboard page render karega
    return render(request, 'core/dashboard.html')

def upload_dataset(request):
    # File upload handle karega
    if request.method == 'POST' and request.FILES.get('dataset_file'):
        uploaded_file = request.FILES['dataset_file']
        # Database mein save karo
        dataset = Dataset(name=uploaded_file.name, file=uploaded_file)
        if request.user.is_authenticated:
            dataset.user = request.user
        dataset.save()
        return redirect('dashboard')
    return redirect('dashboard')