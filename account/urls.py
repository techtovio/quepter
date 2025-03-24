from django.urls import path
from . import views

urlpatterns = [
    path('', views.account, name='profile'),
    path('profile/upload/photo/', views.profile_image, name='upload-profile'),
    path('notification/settings/', views.notification_settings, name='notification-settings'),
    path('connection/settings/', views.connection_settings, name='connection-settings')
]
