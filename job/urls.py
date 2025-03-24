from django.urls import path
from . import views

urlpatterns = [
    path('opportunity/<uuid:uuid>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunity/apply/', views.apply_job, name='apply_job'),
    path('opportunity/create/', views.create_job, name='create_job'),
    path('opportunity/delete/<uuid:uuid>/', views.delete_job, name='delete_job'),
]