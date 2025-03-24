from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('challenges/', views.challenges_view, name='challenges'),
    path('challenges/complete/<uuid:challenge_id>/', views.complete_challenge, name='complete_challenge'),
    path('rewards/', views.redeem_rewards, name='rewards'),
]
