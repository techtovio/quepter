from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.urls import path
from quepter.views import register, login_form, registration_affiliate, webmanifest
from django.contrib.auth import views as auth_views
from .forms import PasswordChangeForm, PasswordResetForm, password_validation, SetPasswordForm
from dashboard.views import resendSMS, verify
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


admin.site.index_title = "QUEPTER YOUTH HUB"
admin.site.site_header = "QUEPTER YOUTH HUB"
admin.site.site_title =  "QUEPTER YOUTH HUB"

urlpatterns = [
    path('oauth/admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('', include('event.urls')),
    path('', include('post.urls')),
    path('', include('learning.urls')),
    path('', include('project.urls')),
    path('', include('p2p.urls')),
    path('', include('club.urls')),
    path('', include('leaderboard.urls')),
    path('', include('wallet.urls')),
    path('', include('dao.urls')),
    path('talents/', include('talent.urls')),
    path('investment/', include('investment.urls')),
    path('accounts/', include('account.urls')),
    path('accounts/register/', register, name='register'),
    path('accounts/member/verify/<str:phone_no>/<str:email>/', verify, name='verify'),
    path('accounts/resend/verification/<str:phone_no>/', resendSMS, name='resendSMS'),
    path('accounts/register/<str:acode>/', registration_affiliate, name='registration_link'),
    path('accounts/login/', login_form, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name="logout"),
    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html', form_class=PasswordResetForm, success_url='/accounts/password-reset/done/'), name="password-reset"), # Passing Success URL to Override default URL, also created password_reset_email.html due to error from our app_name in URL
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name="password_reset_done"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', form_class=SetPasswordForm, success_url='/accounts/password-reset-complete/'), name="password_reset_confirm"), # Passing Success URL to Override default URL
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name="password_reset_complete"),
    path('.well-known/manifest.json', webmanifest, name='webmanifest'),
    
]

# To display images
#if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)