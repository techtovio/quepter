from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import InvestmentOpportunity, MemberInvestmentRequest, MentorshipProgram
from django.contrib.auth.decorators import login_required
from dashboard.models import Notification
from django.http import HttpResponseRedirect
from django.contrib import messages
import json

@login_required(login_url='login')
def investment_opportunities(request):
    user = request.user
    opportunities = InvestmentOpportunity.objects.all()
    return render(request, 'investment/investment.html', {'opportunities': opportunities, 'notifications':Notification.objects.filter(user=user),})

@login_required(login_url='login')
def submit_application(request, opportunity_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        points = body['points']
        application_text = body['application_text']
        profile = request.user.profile
        opportunity = InvestmentOpportunity.objects.get(id=opportunity_id) 
        if int(profile.points) > int(points) and int(profile.points) > opportunity.min_points_required:
            # Check other Qualifications required
            if profile.account_age() < int(opportunity.account_age_requirements):
                messages.warning(request, "Your Account Age does not meet the minimum duration required, please keep using Quepter Youth Hub to meet this requirement.")
                return JsonResponse({'success': False, 'message': 'Your Account Age does not meet the minimum duration required, please keep using Quepter Youth Hub to meet this requirement.'})
            if profile.referred_friends.count() < int(opportunity.invites_required):
                messages.warning(request, "Please invite more friends to meet minimum amount of invites required before applying for this opportunity.")
                return JsonResponse({'success': False, 'message':'Please invite more friends to meet minimum amount of invites required before applying for this opportunity.'})
            user_clubs = profile.user_clubs()
            if opportunity.club_required not in user_clubs:
                messages.warning(request, "You must be a member of the respective club to qualify for this opportunity")
                return JsonResponse({'success': False, 'message':'You must be a member of the respective club to qualify for this opportunity.'})
            MemberInvestmentRequest.objects.create(
                user=request.user, project=opportunity, points=points, application_text=application_text
            )
            Notification.objects.create(
                user=request.user,
                title="Funding request received successfully.",
                message=f"Congratulations {profile.name()}, Your funding request has been received successfully for approval, kindly wait while we process your request."
            )
            messages.success(request, "Congratulations, Your funding request has been submitted successfully, you will be notified once our team finish processing your application.")
            return JsonResponse({'success': True, 'message':'Congratulations, Your funding request has been submitted successfully, you will be notified once our team finish processing your application.'})
        else:
            messages.warning(request, "You have insufficient points to apply for this funding opportunity, keep contributing to the club to gather enough points!")
    #return JsonResponse({'success': False, 'message': 'Invalid request!'})
            return JsonResponse({'success': False, 'message':'You have insufficient points to apply for this funding opportunity, keep contributing to the club to gather enough points!'})

@login_required(login_url='login')
def mentorship_programs(request):
    programs = MentorshipProgram.objects.all()
    return render(request, 'investment/mentorship_programs.html', {'programs': programs, 'notifications':Notification.objects.filter(user=request.user),})

@login_required(login_url='login')
def create_investment(request):
    user = request.user
    if user.profile.is_admin:
        if request.method == "POST":
            title = request.POST['title']
            description = request.POST['description']
            location = request.POST['location']
            min_points_required = request.POST['min_points_required']
            if title and description and location and min_points_required:
                invest = InvestmentOpportunity.objects.create(
                    title=title,
                    description=description,
                    location=location,
                    min_points_required=min_points_required,
                )
                invest.save()
                messages.success(request, "New Investment opportunity has been created successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))