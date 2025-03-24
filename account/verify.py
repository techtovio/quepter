import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template.loader import render_to_string  # Correct import
from django.http import HttpResponse
from dashboard.models import Verify, Profile
from django.core.mail import EmailMessage

def generate_verification_code(length=6):
    """Generate a random numeric verification code of the specified length."""
    return ''.join(random.choices('0123456789', k=length))


def send_verification_code(phone_no):
    profile = Profile.objects.get(phone_no=phone_no)
    user = profile.user
    
    # Generate a verification code
    verification_code = generate_verification_code()
    
    try:
        Verify.objects.get(phone_no=phone_no)
    except Verify.DoesNotExist:
        Verify.objects.create(phone_no=phone_no, code=verification_code)
        html_message = render_to_string('accounts/email_verification_code.html', {
            'user': user,
            'verification_code': verification_code,
        })

        # Create and send the email
        email = EmailMessage(
            subject="Your Quepter Youth Hub Verification Code",
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.content_subtype = "html"  # Main point: set content type to HTML
        email.send()
    return True
