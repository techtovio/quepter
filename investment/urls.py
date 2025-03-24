from django.urls import path
from . import views

urlpatterns = [
    path('opportunities/', views.investment_opportunities, name='investment_opportunities'),
    path('opportunities/create/', views.create_investment, name='create_investment'),
    path('submit_application/<int:opportunity_id>/', views.submit_application, name='submit_funding_application'),
    path('mentorship_programs/', views.mentorship_programs, name='mentorship_programs'),
]
