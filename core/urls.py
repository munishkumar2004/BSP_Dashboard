from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dataset/<int:dataset_id>/', views.dashboard_view, name='dashboard_with_id'),
    path('datasets/', views.dataset_list_view, name='dataset_list'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('train/<int:dataset_id>/', views.train_model_view, name='train_model'),
    path('download-report/<int:dataset_id>/', views.download_report_view, name='download_report'),
    path('email-report/<int:dataset_id>/', views.email_report_view, name='email_report'),
    path('merge/', views.merge_datasets_view, name='merge_datasets'),
    path('clean/<int:dataset_id>/', views.clean_data_view, name='clean_data'),
    
    # Media Lists
    path('images/', views.image_list_view, name='image_list'),
    path('audios/', views.audio_list_view, name='audio_list'),
    path('videos/', views.video_list_view, name='video_list'),

    # Uploads & Details
    path('upload-image/', views.upload_image_view, name='upload_image'),
    path('image/<int:image_id>/', views.image_detail_view, name='image_detail'),
    path('upload-audio/', views.upload_audio_view, name='upload_audio'),
    path('audio/<int:audio_id>/', views.audio_detail_view, name='audio_detail'),
    path('upload-video/', views.upload_video_view, name='upload_video'),
    path('video/<int:video_id>/', views.video_detail_view, name='video_detail'),
    
    # Delete Paths
    path('delete-dataset/<int:dataset_id>/', views.delete_dataset_view, name='delete_dataset'),
    path('delete-image/<int:image_id>/', views.delete_image_view, name='delete_image'),
    path('delete-audio/<int:audio_id>/', views.delete_audio_view, name='delete_audio'),
    path('delete-video/<int:video_id>/', views.delete_video_view, name='delete_video'),
]