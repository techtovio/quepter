from django.urls import path
from . import views

urlpatterns = [
    path('dao/', views.dao_home, name='dao_home'),
    path('proposal/create/', views.create_proposal, name='create_proposal'),
    path('proposal/<int:proposal_id>/vote/', views.vote, name='vote'),
]