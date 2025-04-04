from django.shortcuts import render, get_object_or_404
from job.models import JobPosition, JobApplication
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from django.http import HttpResponseRedirect
from django.contrib import messages
from dashboard.models import Notification
from club.models import ClubMembership

@csrf_exempt
def apply_job(request):
    if request.method == 'POST' and request.is_ajax():
        job = JobPosition.objects.get(uuid=uuid)
        name = request.POST.get('name')
        email = request.POST.get('email')
        resume = request.FILES.get('resume')

        # Save the application
        application = JobApplication.objects.create(
            job=job,
            applicant_name=name,
            applicant_email=email,
            resume=resume
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='login')
def opportunity_detail(request, uuid):
    opportunity = get_object_or_404(JobPosition, uuid=uuid)
    try:
        club_membership = ClubMembership.objects.get(user=request.user)
    except ClubMembership.DoesNotExist:
        club_membership = None
    return render(request, 'dashboard/job.html', {'job': opportunity, 'notifications':Notification.objects.filter(user=request.user), "club_membership":club_membership})


@login_required(login_url='login')
@csrf_exempt
def delete_job(request, uuid):
    if request.method == 'POST':
        try:
            job = get_object_or_404(JobPosition, uuid=uuid)
            job.delete()
            return JsonResponse({'status': 'success', 'message': 'Job deleted successfully!'})
        except JobPosition.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job not found!'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method!'})


@login_required(login_url='login')
def create_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        job_category = request.POST.get('job_category')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        deadline = request.POST.get('deadline')
        requirements = request.POST.get('requirements')
        
        if title and job_category and location and salary and deadline and requirements:
            job = JobPosition.objects.create(
                title=title,
                description=description,
                uuid=uuid.uuid4(),
                category=job_category,
                location=location,
                salary=salary,
                deadline=deadline,
                requirements=requirements,
            )
            job.save()
            messages.success(request, "Job position has been created successfully!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.warning(request, "All Fields are required!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    messages.warning(request, 'Invalid request method!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))