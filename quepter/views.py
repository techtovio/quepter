from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User,Group
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from dashboard.models import Profile, Verify, Notification
import requests
from random import randint
from django.core.mail import send_mail
import string
import random
from dashboard.SMS import sendSMS
from dashboard.sendgmail import sendingMail
from account.verify import send_verification_code
from club.models import Club, ClubMembership, ClubBroadcast
from django.http import HttpResponse
from django.views.decorators.http import require_GET
import json
import os
from django.conf import settings
from wallet.views import associate_token
from wallet.contracts.hedera import load_operator_credentials, create_new_account
from hiero_sdk_python import (
    Client,
    AccountId,
    PrivateKey,
    TransferTransaction,
    Network,
    TokenAssociateTransaction,
    TokenId
)
from wallet.models import UserWallet

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def assign_user_wallet(name):
    operator_id, operator_key = load_operator_credentials()
    network_type = os.getenv('NETWORK')
    token_id = os.getenv('Token_ID')
    network = Network(network=network_type)
    client = Client(network)
    client.set_operator(operator_id, operator_key)
    try:
        recipient_id, recipient_private_key, new_account_public_key = create_new_account(name, client)
        associate_token(recipient_id, recipient_private_key)

        return {
            'status':'success',
            'new_account_public_key': f'{new_account_public_key}',
            'recipient_private_key': f'{recipient_private_key}',
            'recipient_id':f'{recipient_id}'
        }
    except Exception as e:
        print(e)
        return {
            'status':'failed',
            'error':e
        }
    
def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        phone_no = request.POST.get('phoneNo')
        email = request.POST.get('email').lower()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        password1 = request.POST['password1']
        if password != password1:
            messages.warning(request, "Password does not match, try Again!")
            return redirect('register')
        if email and first_name and last_name and password is not None:
            try:
                User.objects.get(email=email)
                messages.warning(request, "User with that details exist, please login or sign up with unique credentials")
                return redirect("register")
            except Exception as e:
                try:
                    try:
                        Profile.objects.get(phone_no=phone_no)
                        messages.warning(request, "Your Details (phone number/ID/Email) has been registered on our platform earlier, we DO NOT allow multiple accounts on individuals! Please Login.")
                        return redirect('login')
                    except Profile.DoesNotExist:
                        pass
                    try:
                        response = assign_user_wallet(name=f'{first_name} {last_name}')
                        print(response)
                        if response['status'] == 'success':
                            new_account_public_key = response['new_account_public_key']
                            recipient_private_key = response['recipient_private_key']
                            recipient_id = response['recipient_id']
                        else:
                            messages.warning(request, "An error occured while trying to assign you a wallet, please try again")
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    except Exception as e:
                        messages.warning(request, f'Wallet Creation Faile: |{e}')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    nu = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=email)
                    referrer = Profile.objects.get(phone_no="0706889399")
                    Profile.objects.create(user=nu, phone_no=phone_no, gender=gender, referrer=referrer.user)
                    UserWallet.objects.create(user=nu, qpt_public_key=new_account_public_key, qpt_private_key=recipient_private_key, recipient_id=recipient_id)
                    messages.success(request, "Account has been created successfully, please login to continue")
                    return redirect('login')
                except Exception as e:
                    print(e)
                    messages.warning(request, f"An error occured while trying to create your account, please try again")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "All fields are required")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'accounts/register.html')
    
def registration_affiliate(request, acode):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        phone_no = request.POST.get('phoneNo')
        email = request.POST.get('email').lower()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        password1 = request.POST['password1']
        if password != password1:
            messages.warning(request, "Password does not match, try Again!")
            return redirect('register')
        if email and first_name and last_name and password is not None:
            try:
                User.objects.get(email=email)
                messages.warning(request, "User with that details exist, please login or sign up with unique credentials")
                return redirect("register")
            except Exception as e:
                try:
                    affiliate = Profile.objects.get(code=acode)
                    try:
                        Profile.objects.get(phone_no=phone_no)
                        messages.warning(request, "Your Details (phone number/ID/Email) has been registered on our platform earlier, we DO NOT allow multiple accounts on individuals! PLease Login.")
                        return redirect('login')
                    except Profile.DoesNotExist:
                        pass
                    try:
                        response = assign_user_wallet(name=f'{first_name} {last_name}')
                        print(response)
                        if response['status'] == 'success':
                            new_account_public_key = response['new_account_public_key']
                            recipient_private_key = response['recipient_private_key']
                            recipient_id = response['recipient_id']
                        else:
                            messages.warning(request, "An error occured while trying to assign you a wallet, please try again")
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    except Exception as e:
                        messages.warning(request, f'Wallet Creation Faile: |{e}')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    nu = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=email)
                    Profile.objects.create(user=nu, phone_no=phone_no, referrer=affiliate.user, gender=gender)
                    UserWallet.objects.create(user=nu, qpt_public_key=new_account_public_key, qpt_private_key=recipient_private_key, recipient_id=recipient_id)
                    messages.success(request, "Account has been created successfully, please login to continue")
                    return redirect('login')
                except Exception as e:
                    print(e)
                    messages.warning(request, f"An error occured while trying to create your account, please try again")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "All fields are required")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'accounts/register_affiliate.html')

def login_form(request):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['email'].lower()
        password = request.POST['password']
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                try:
                    profile = Profile.objects.get(user=user)
                    phone_no = profile.phone_no
                except Profile.DoesNotExist:
                    messages.warning(request, "We are finding problems getting your profile, please try again later!")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                try:
                    #verify = Verify.objects.get(phone_no=phone_no)
                    #if verify.status == True:
                    login(request, user)
                    current_user =request.user
                    # Check if user has joined compulsory club
                    club = Club.objects.get(name="Business and Entrepreneurship Club")
                    if club.members.filter(id=current_user.id).exists():
                        messages.success(request, f"Welcome back, { current_user.first_name }! You are an amazing member, explore what you have achieved at quepter youth hub.")
                        return redirect('dashboard')
                    else:
                        messages.success(request, f"Congratulations {current_user.first_name}, You are one step away to complete your Quepter Youth Hub membership process. Join our Business and Entrepreneurship Club today!")
                        return redirect('club_detail', uuid=club.uuid)
                except Verify.DoesNotExist:
                    messages.warning(request, "An error occured while trying to verify your account, please try again")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.warning(request,"Invalid Username or password")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "All fields are required")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'accounts/login.html')


def webmanifest(request):
    manifest_path = os.path.join(settings.STATIC_ROOT, 'manifest.json')
    with open(manifest_path) as f:
        manifest = json.load(f)
    return HttpResponse(
        json.dumps(manifest),
        content_type='application/manifest+json'
    )