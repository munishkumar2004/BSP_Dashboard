from django.contrib import admin
from .models import Dataset, MLModel, Report, ImageDataset, AudioDataset, VideoDataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('name',)
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'
    list_per_page = 20


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'algorithm', 'accuracy', 'created_at')
    list_filter = ('algorithm', 'created_at')
    search_fields = ('name', 'algorithm')
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'generated_at')
    list_filter = ('generated_at', 'user')
    search_fields = ('title',)
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    list_per_page = 20


@admin.register(ImageDataset)
class ImageDatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    ordering = ('-uploaded_at',)


@admin.register(AudioDataset)
class AudioDatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    ordering = ('-uploaded_at',)


@admin.register(VideoDataset)
class VideoDatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'uploaded_at')
    list_filter = ('uploaded_at', 'user')
    ordering = ('-uploaded_at',)


admin.site.site_header = "BSP Dashboard Administration"
admin.site.site_title = "BSP Dashboard Admin"
admin.site.index_title = "Welcome to BSP Dashboard"