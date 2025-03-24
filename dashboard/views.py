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
from datetime import datetime, timedelta
from django.utils import timezone
import string
import random
from event.models import Event
from project.models import Project
from job.models import JobPosition, JobApplication
from post.models import CommunityPost
from dashboard.models import Profile, Verify, Transaction, Notification, Contribute, Mentorship, Success_Story, Message, Blog, Funding
from django.views.decorators.csrf import csrf_exempt
from dashboard.SMS import sendSMS
from investment.models import InvestmentOpportunity, MemberInvestmentRequest
from voting.models import LeadershipPosition, Vote
from decimal import Decimal

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def home(request):
    success_story = Success_Story.objects.all()
    events = Event.objects.filter(is_completed=False)
    projects = Project.objects.all()
    events = Event.objects.all()
    content = {
        'success_story':success_story,
        'events':events,
        'projects':projects,
        'events':events,
    }
    return render(request, 'index.html', content)

def donate(request):
    return render(request, 'contribute.html')

def about(request):
    success_story = Success_Story.objects.all()
    events = Event.objects.filter(is_completed=False)
    projects = Project.objects.all()
    events = Event.objects.all()
    content = {
        'success_story':success_story,
        'events':events,
        'projects':projects,
        'events':events,
    }
    return render(request, 'about.html', content)

def blog(request):
    success_story = Success_Story.objects.all()
    events = Event.objects.filter(is_completed=False)
    projects = Project.objects.all()
    events = Event.objects.all()
    blogs = Blog.objects.all()
    content = {
        'success_story':success_story,
        'events':events,
        'projects':projects,
        'events':events,
        'blogs':blogs,
    }
    return render(request, 'blog.html', content)

def contact(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        name = fname + " " + lname
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']
        Message.objects.create(name=name, email=email, phone=phone, message=message)
        messages.success(request, "Your message has been submitted successfully, our team will get back to you as soon as possible.")
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
        }
        return render(request, 'contact.html', content)

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    time = datetime.now()
    blogs = Blog.objects.all()[:3]
    feed = CommunityPost.objects.all().order_by('-date_posted')[:5]
    mentorships = Mentorship.objects.all()

    context = {
        'profile':Profile.objects.get(user=user),
        'notifications':Notification.objects.filter(user=user),
        'projects':Project.objects.filter(participants=request.user),
        'time':time,
        'all_projects':Project.objects.all(),
        'opportunities': JobPosition.objects.all(),
        'feed': feed,
        'events': Event.objects.all(),
        'mentorships': mentorships,
        'blogs':blogs,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='login')
def transactions(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    transaction = Transaction.objects.filter(user=user)
    events = Event.objects.filter(is_completed=False)
    projects = Project.objects.all()
    all_notifications = Notification.objects.filter(user=user)
    time = datetime.now()

    context = {
        'profile':profile,
        'events':events,
        'notifications':Notification.objects.filter(user=user),
        'projects':projects,
        'time':time,
        'all_notifications':all_notifications,
    }

    context = {
        'profile':profile,
        'transactions':transaction,
    }
    return render(request, 'dashboard/transactions.html', context)

@login_required(login_url='login')
def projects(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    events = Event.objects.filter(is_completed=False)

    projects = Project.objects.all()
    time = datetime.now()

    context = {
        'profile':profile,
        'events':events,
        'notifications':Notification.objects.filter(user=user),
        'projects':projects,
        'time':time,
    }

    return render(request, 'dashboard/projects.html', context)

@login_required(login_url="login")
def pay_mpesa(request):
    user = request.user
    if request.method == "POST":
        tel = request.POST['tel']
        amount = request.POST['amount']
        if tel and amount:
            reference = id_generator()
            ua = {
                    'Content-Type': 'application/json',
                    'Authorization':'Basic WDFkN3VBYVYzTUxsYjI1VmNhS2U6UHBEMlFnVkMxUXJOalNWTWU4bHhXejd6RFVNNWwzcldnQlcwZkR6cQ==',
                }
            url = 'https://backend.payhero.co.ke/api/v2/payments'
            
            data = {
                "amount": int(amount),
                "phone_number": f"{tel}",
                "channel_id": 947, 
                "provider": "m-pesa",
                "external_reference": f"{reference}",
                "callback_url": "https://quepter.co.ke/payment/mpesa/success/"
            }
            res = requests.post(url=url, json=data, headers=ua)
            js = res.json()
            print(js)
            if js['success'] == True:
                # Add EXception to handle Already Exists subscription
                Transaction.objects.create(user=user, amount=amount, reference=reference)
                Notification.objects.create(user=user, title="Payment Initiated", message=f"New payment of Kes {amount} has been initiated successfully, complete by entering your pin.")
                #messages.success(request, "Payment initialized successfuly, please complete it by entering your pin")
                messages.success(request, f"STK push initiated successfully, If you did not get any pop up on your phone try following this manual steps to complete your payment: {js['manual_instructions']}")
            else:
                messages.warning(request, "An error occured while trying to process your payment, please try again later")
        else:
            messages.warning(request, "All Fields are requeired!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def activate_mpesa(request):
    user = request.user
    if request.method == "POST":
        tel = request.POST['tel']
        amount = 250
        if tel and amount:
            reference = id_generator()
            ua = {
                    'Content-Type': 'application/json',
                    'Authorization':'Basic RXMzSzN5c3lOMVVTMjBsaUtlRmo6SGpJOW5qQXVOOGJiSHFZNEhCVVZ3OXVYa0l3a1hwWjhlOUR4ekpUUw==',
                }
            url = 'https://backend.payhero.co.ke/api/v2/payments'
            
            data = {
                "amount": int(amount),
                "phone_number": f"{tel}",
                "provider": "sasapay", 
                "network_code":"63902",
                "external_reference": f"{reference}",
                "callback_url": "https://quepter.co.ke/activate/payment/mpesa/success/"
            }
            res = requests.post(url=url, json=data, headers=ua)
            js = res.json()
            print(js)
            if js['success'] == True:
                # Add EXception to handle Already Exists subscription
                Transaction.objects.create(user=user, amount=amount, reference=reference)
                Notification.objects.create(user=user, title="Payment Initiated", message=f"New payment of Kes {amount} has been initiated successfully, complete by entering your pin.")
                #messages.success(request, "Payment initialized successfuly, please complete it by entering your pin")
                messages.success(request, f"STK push initiated successfully, If you did not get any pop up on your phone try following this manual steps to complete your payment: {js['manual_instructions']}")
            else:
                messages.warning(request, "An error occured while trying to process your payment, please try again later")
        else:
            messages.warning(request, "All Fields are requeired!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def contribute(request):
    if request.method == "POST":
        tel = request.POST['tel']
        amount = request.POST['amount']
        if tel and amount:
            reference = id_generator()
            ua = {
                    'Content-Type': 'application/json',
                    'Authorization':'Basic WDFkN3VBYVYzTUxsYjI1VmNhS2U6UHBEMlFnVkMxUXJOalNWTWU4bHhXejd6RFVNNWwzcldnQlcwZkR6cQ==',
                }
            url = 'https://backend.payhero.co.ke/api/v2/payments'
            
            data = {
                "amount": int(amount),
                "phone_number": f"{tel}",
                "channel_id": 947, 
                "provider": "m-pesa",
                "external_reference": f"{reference}",
                "callback_url": "https://quepter.co.ke/contribute/payment/mpesa/success/"
            }
            res = requests.post(url=url, json=data, headers=ua)
            js = res.json()
            print(js)
            if js['success'] == True:
                # Add EXception to handle Already Exists subscription
                Contribute.objects.create(phone=tel, amount=amount, reference=reference)
                #Notification.objects.create(user=user, title="Payment Initiated", message=f"New payment of Kes {amount} has been initiated successfully, complete by entering your pin.")
                #messages.success(request, "Payment initialized successfuly, please complete it by entering your mpesa pin")
                messages.success(request, f"STK push initiated successfully, If you did not get any pop up on your phone try following this manual steps to complete your payment: {js['manual_instructions']}")
            else:
                messages.warning(request, "An error occured while trying to process your payment, please try again later")
        else:
            messages.warning(request, "All Fields are requeired!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def member_funding(request):
    if request.method == "POST":
        user = request.user
        tel = request.POST['tel']
        amount = request.POST['amount']
        
        messages.success(request, "This feature is Coming soon")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
def mpesaSuccess(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response_data = data.get('response', {})
            reference = response_data.get("ExternalReference")
            status = response_data.get("Status")
            payment = Transaction.objects.get(reference=reference)
            if status == "Success":
                payment.status = "Completed"
                user = payment.user
                Notification.objects.create(user=user, title="Funds Have been Received Successfully", message=f"New fund deposit of Kes {payment.amount} has been received successfully")
                profile = Profile.objects.get(user=user)
                profile.funds += payment.amount
                payment.save()
                profile.save()
            else:
                Notification.objects.create(user=user, title="Payment Cancelled", message=f"New payment of Kes {payment.amount} was not successful!")
                payment.status = "Cancelled"
                payment.save()
        except Exception as e:
            print(e)

@csrf_exempt
def activatePaid(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response_data = data.get('response', {})
            reference = response_data.get("ExternalReference")
            status = response_data.get("Status")
            payment = Transaction.objects.get(reference=reference)
            if status == "Success":
                payment.status = "Completed"
                user = payment.user
                profile = Profile.objects.get(user=user)
                Notification.objects.create(user=user, title="Membership Access Successful", message=f"Congratulations, You have successfully paid membership fee and you are now a member.")
                profile.is_verified = True
                payment.save()
                profile.save()
            else:
                Notification.objects.create(user=user, title="Membership Access Failed", message=f"Hello, your membership fee was not successful, please try again!")
                payment.status = "Cancelled"
                payment.save()
        except Exception as e:
            print(e)

@csrf_exempt
def contributeSuccess(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response_data = data.get('response', {})
            reference = response_data.get("ExternalReference")
            status = response_data.get("Status")
            payment = Contribute.objects.get(reference=reference)
            if status == "Success":
                payment.status = "Completed"
                payment.save()
            else:
                payment.status = "Cancelled"
                payment.save()
        except Exception as e:
            print(e)

@csrf_exempt
def fundingSuccess(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response_data = data.get('response', {})
            reference = response_data.get("invoice_id")
            status = response_data.get("state")
            payment = Funding.objects.get(reference=reference)
            if status == "COMPLETE":
                payment.status = "Completed"
                payment.save()
            else:
                payment.status = "Cancelled"
                payment.save()
        except Exception as e:
            print(e)

@login_required(login_url="login")
def clear_notif(request):
    user = request.user
    notif = Notification.objects.filter(user=user)
    for noti in notif:
        noti.delete()
    messages.success(request, "All notifications have been cleared successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def verify(request, phone_no, email):
    if request.method == "POST":
        code = request.POST['code']
        profile = Profile.objects.get(phone_no=phone_no)
        referrer = Profile.objects.get(user=profile.referrer)
        try:
            verify_ = Verify.objects.get(phone_no=phone_no)
            if verify_.attempts < 1:
                messages.warning(request, "Your account has been locked, please contact us for assistance on how you can access it again")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                if code == verify_.code:
                    verify_.status = True
                    profile.is_verified = True
                    # Award points to the referrer
                    referrer.points += Decimal('2')

                    # Award points to the referred user
                    profile.points += Decimal('0.5')
                    Notification.objects.create(
                        user=profile.user,
                        title="Welcome to Quepter Youth Hub",
                        message = f"Hello {profile.name()}, you have been awarded 0.5 points for successfully joining Quepter youth Hub."
                    )
                    Notification.objects.create(
                        user=referrer.user,
                        title="Congratulations! Referral Award",
                        message = f"Hello {referrer.name()}, you have been awarded 2 points for successfully inviting a friend, see your new earned badge at your profile."
                    )
                    verify_.save()
                    referrer.save()
                    profile.save()
                    messages.success(request, "Congratulations, your account has been Verified successfully, please login to continue.")
                    return redirect("login")
                else:
                    verify_.attempts -= 1
                    verify_.save()
                    messages.warning(request, f"You have entered an invalid code, you have {verify_.attempts} remaining attempts before we permanently lock your account, please try again!")
        except Verify.DoesNotExist:
            messages.warning(request, "We could not find your details, please login again!")
            return redirect('login')
    return render(request, "accounts/verify.html", {"phone_no":phone_no, "email":email})

def resendSMS(request):
    user = request.user
    if request.method == "POST":
        phone_no = request.POST['phone_no']
        try:
            profile = Profile.objects.get(phone_no=phone_no)
        except Profile.DoesNotExist:
            messages.warning(request, "Member with that contact information does not exist, please check your details and try again!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        try:
            vf = Verify.objects.get(phone_no=phone_no)
            if vf.times_Day == 0:
                #if vf.timestamp > datetime.now() + timedelta(days=30)
                messages.warning(request, "You have reached your maximum sms limit that you can receive in a day, please try again later, you can contact us if this issue persist")
            else:
                send = sendSMS(mobile=phone_no, code=vf.code)
                if send == True:
                    vf.times_Day -= 1
                    vf.save()
                    messages.success(request, f"A new SMS with an OTP Code has been sent to {phone_no}, use it to verify your account")
                else:
                    messages.warning(request, "An error occured while trying to verify your account, please try again")
        except Verify.DoesNotExist:
            ccode = id_generator(size=6)
            send = sendSMS(mobile=phone_no, code=ccode)
            if send == True:
                vff = Verify.objects.create(phone_no=phone_no, code=ccode)
                messages.success(request, f"A new SMS with an OTP Code has been sent to {phone_no}, use it to verify your account")
            else:
                messages.warning(request, "An error occured while trying to verify your account, please try again")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def mentorship_detail(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)
    return render(request, 'dashboard/mentorship_detail.html', {'mentorship': mentorship, 'notifications':Notification.objects.filter(user=request.user),})

# Example API view for AJAX requests
def api_projects(request):
    projects = Project.objects.filter(participants=request.user)
    data = [{'id': project.id, 'title': project.title, 'description': project.description} for project in projects]
    return JsonResponse(data, safe=False)

@login_required(login_url='login')
def administration(request):
    user = request.user
    if user.profile.is_admin:
        context = {
            'jobs':JobPosition.objects.all(),
            'projects':Project.objects.all(),
            'events':Event.objects.all(),
            'transactions':Transaction.objects.all(),
            'investments':InvestmentOpportunity.objects.all(),
            'members':Profile.objects.all(),
            'leadership': LeadershipPosition.objects.all(),
            'notifications':Notification.objects.filter(user=user),

        }
        return render(request, 'dashboard/administration.html', context)
    else:
        return redirect('dashboard')
    

@login_required(login_url='login')
def faqs(request):
    return render(request, 'dashboard/faqs.html', {'notifications':Notification.objects.filter(user=request.user),})

@login_required(login_url='login')
def withdraw_funds(request):
    user = request.user
    if request.method == 'POST':
        profile = Profile.objects.get(user=user)
        amount = request.POST['amount']
        if int(amount) < 100:
            messages.warning(request, "The minimum amount to withdraw is kes 100, please try again later!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if int(amount) > int(profile.funds):
            messages.warning(request, f"You do not have enough funds in your account to withdraw KES {amount}, your balance is KES {profile.funds}!")
        else:
            profile.funds -= int(amount)
            Notification.objects.create(
                user=user,
                title="Withdrawal request submitted successfully.",
                message = f"Your withdrawal request of Kes {amount} has been submitted submitted successfully, please wait while your request is being processed."
            )
            Transaction.objects.create(
                user=user,
                type="Withdrawal",
                amount=int(amount),
                reference=id_generator(),
            )
            profile.save()
            messages.success(request, f"Your withdrawal request of kes {amount} has been submitted successfully, please wait while your request is being processed.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))