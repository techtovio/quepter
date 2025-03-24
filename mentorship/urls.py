from django.urls import path
from . import views

urlpatterns = [
    path('mentorship/', views.mentorship_page, name='mentorship_page'),
    path('mentorship/send_one_on_one_message/', views.send_one_on_one_message, name='send_one_on_one_message'),
    path('mentorship/send_group_message/', views.send_group_message, name='send_group_message'),
    path('mentorship/load_one_on_one_messages/<int:mentorship_id>/', views.load_one_on_one_messages, name='load_one_on_one_messages'),
    path('mentorship/load_group_messages/<int:group_id>/', views.load_group_messages, name='load_group_messages'),
]
