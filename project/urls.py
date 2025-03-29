from django.urls import path
from .views import ProposalCreateView, ProposalListView, ProposalDetailView, proposal_feedback

urlpatterns = [
    path('create/', ProposalCreateView.as_view(), name='proposal_create'),
    path('projects/', ProposalListView.as_view(), name='proposal_list'),
    path('project/<uuid:pk>/', ProposalDetailView.as_view(), name='proposal_detail'),
    path('<uuid:pk>/feedback/', proposal_feedback, name='proposal_feedback'),
]
