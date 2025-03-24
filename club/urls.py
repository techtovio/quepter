from django.urls import path
from . import views

urlpatterns = [
    path('clubs/', views.club_list, name='club_list'),
    path('clubs/<uuid:uuid>/', views.club_detail, name='club_detail'),
    path('clubs/<uuid:uuid>/join/', views.join_club, name='join_club'),
    path('clubs/<uuid:uuid>/broadcast/', views.create_broadcast, name='create_broadcast'),
    path('club/<uuid:uuid>/contribute/', views.contribute_to_club, name='contribute_to_club'),
]
