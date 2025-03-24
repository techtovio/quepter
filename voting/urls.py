from django.urls import path
from . import views

urlpatterns = [
    path('vote/leaders/', views.leadership, name='leadership'),
    path('vote/cast/', views.cast_vote_ajax, name='cast_vote_ajax'),
    path('leadership/apply/', views.apply_leadership_ajax, name='apply_leadership_ajax'),
    path('leadership/create/position/', views.create_position, name='create_position'),
]
