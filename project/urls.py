from django.urls import path
from . import views

urlpatterns = [
    path('project/<uuid:uuid>/', views.project_detail, name='project_detail'),
    path('send-message/', views.send_message, name='send_message'),
    path('propose_project/', views.propose_project, name='propose_project'),
    path('get_user_points/', views.get_user_points, name='get_user_points'),
    path('projects/all/', views.projects, name='projects'),
    path('submit-proposal/', views.submit_proposal, name='submit-proposal'),
    path('back-project/', views.back_project, name='back-project'),
]
