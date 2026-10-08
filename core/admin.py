from django.contrib import admin
from .models import Dataset, MLModel, Report

admin.site.register(Dataset)
admin.site.register(MLModel)
admin.site.register(Report)