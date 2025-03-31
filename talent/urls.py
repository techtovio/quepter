from django.urls import path
from . import views

urlpatterns = [
    path('', views.talent_list, name='talent_list'),
    path('create/', views.create_talent, name='create_talent'),
    path('<uuid:uuid>/', views.talent_detail, name='talent_detail'),
    path('<uuid:uuid>/book/', views.book_talent, name='book_talent'),
    path('<uuid:uuid>/review/', views.add_review, name='add_review'),
    path('<uuid:uuid>/follow/', views.toggle_follow, name='toggle_follow'),
]