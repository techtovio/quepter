from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact, name='contact'),
    path('contribute/', views.donate, name='donate'),
    path('clearnotifications/', views.clear_notif, name='clear_notif'),
    path('contribute/mpesa/', views.contribute, name='contribute'),
    path("contribute/payment/mpesa/success/", views.contributeSuccess, name='contributeSuccess'),
    path('blog/', views.blog, name='blog'),
    path("member/dashboard/", views.dashboard, name='dashboard'),
    path("member/mpesa-pay/", views.pay_mpesa, name='pay_mpesa'),
    path("member/activate-pay/", views.activate_mpesa, name='activate_mpesa'),
    path('mentorships/<int:mentorship_id>/', views.mentorship_detail, name='mentorship_detail'),
    path('api/projects/', views.api_projects, name='api_projects'),
    path('member/voluntary/contribution/', views.member_funding, name='member_funding'),
    path('member/voluntary/contribute/payment/mpesa/success/', views.fundingSuccess, name='fundingSuccess'),
    path('payment/mpesa/success/', views.mpesaSuccess, name='mpesaSuccess'),
    path('oauth/v2/administration/', views.administration, name='administration'),
    path('member/faqs/', views.faqs, name='faqs'),
    path('member/withdraw/', views.withdraw_funds, name='withdraw_funds'),
]