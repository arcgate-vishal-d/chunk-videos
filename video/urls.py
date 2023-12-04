from django.urls import path

from video import views

urlpatterns = [
    path('upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]