import os
from celery import Celery

# 🟢 macOS Fix: PyTorch/Ultralytics ke fork crash ko rokne ke liye
for var in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(var, "1")

# OpenMP runtime conflict (libomp) ko ignore karo
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# Objective-C fork safety abort ko band karo
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')

app = Celery('dashboard_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')