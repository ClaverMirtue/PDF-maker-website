from django.urls import path
from . import views

app_name = 'pdfapp'

urlpatterns = [
    # Home page and static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search_files, name='search'),
    
    # PDF operations
    path('edit-pdf/', views.edit_pdf, name='edit_pdf'),
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),
    path('image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),
    
    # File operations
    path('upload/', views.upload_file, name='upload_file'),
    path('files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    
    # API endpoints for AJAX operations
    path('api/upload/', views.api_upload, name='api_upload'),
    path('api/save-pdf/', views.api_save_pdf, name='api_save_pdf'),
    
    # User dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/files/', views.user_files, name='user_files'),
]
