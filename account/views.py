from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
import requests
import json
from django.http import HttpResponseRedirect
import string
import random
from dashboard.models import Profile, Success_Story, Notification, Transaction
from event.models import Event
from project.models import Project
from django.views.decorators.csrf import csrf_exempt
from dashboard.SMS import sendSMS
from django.contrib.auth.models import User
#huYHDCeLVqtgZ6E4SXAWa8bPyAYQ6SWfar00iYAW
#7LDy66vuZbNrpYamV8gz -- username
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required(login_url="login")
def account(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    if request.method == "POST":
        #fname = request.POST['fname']
        #lname = request.POST['lname']
        profession = request.POST['profession']
        county = request.POST['county']
        profile.profession = profession
        profile.county = county
        profile.save()
        
        messages.success(request, "Your profile details have been updated successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        success_story = Success_Story.objects.all()
        events = Event.objects.filter(is_completed=False)
        projects = Project.objects.all()
        events = Event.objects.all()

        content = {
            'success_story':success_story,
            'events':events,
            'projects':projects,
            'events':events,
            'profile':profile,
            'notifications':Notification.objects.filter(user=user),
            'transactions': Transaction.objects.filter(user=request.user).order_by('-timestamp'),
        }
        return render(request, 'accounts/account.html', content)

@login_required(login_url="login")
def profile_image(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    if request.method == "POST":
        img = request.FILES['image']
        profile.image = img
        profile.save()
        messages.success(request, "Your Profile Photo has been updated successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url="login")
def notification_settings(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    content = {
        'profile':profile,
        'notifications':Notification.objects.filter(user=user),
    }
    
    return render(request, "accounts/notifications.html", content)

@login_required(login_url="login")
def connection_settings(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    content = {
        'profile':profile,
        'notifications':Notification.objects.filter(user=user),
    }
    
    return render(request, "accounts/connections.html", content)