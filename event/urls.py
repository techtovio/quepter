from django.urls import path
from . import views

urlpatterns = [
    path('events/create/', views.create_event, name='create_event'),
    path('events/<uuid:uuid>/', views.event_detail, name='event_detail'),
    path('events/<uuid:uuid>/complete/', views.completed_event, name='completed_event'),
    path('events/<uuid:uuid>/delete/', views.delete_event, name='delete_event'),
]