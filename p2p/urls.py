# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('p2p', views.p2p, name='p2p'),
    path('get-user-points-and-notifications/', views.get_user_points_and_notifications, name='get_user_points_and_notifications'),
    path('list-for-sale/', views.list_for_sale, name='list_for_sale'),
    path('get-available-sales/', views.get_available_sales, name='get_available_sales'),
    path('buy-points/', views.buy_points, name='buy_points'),
    path('transfer-points/', views.transfer_points, name='transfer_points'),
    path('p2p/cancel/', views.cancel_sale, name='cancel_sale'),  # Handle canceling a sale
    path('p2p/history/', views.get_transaction_history, name='get_transaction_history'),
]
