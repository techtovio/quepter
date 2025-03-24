from django.shortcuts import render, get_object_or_404
from event.models import Event
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from dashboard.models import Notification

@login_required(login_url='login')
def event_detail(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    return render(request, 'dashboard/event_detail.html', {'event': event, 'notifications':Notification.objects.filter(user=request.user),})

@login_required(login_url='login')
def create_event(request):
    user = request.user
    if user.profile.is_admin:
        if request.method == "POST":
            title = request.POST['title']
            image = request.FILES.get('image')
            description = request.POST['description']
            date = request.POST['date']
            location = request.POST['location']
            if title and image and description and date and location:
                event = Event.objects.create(
                    title=title,
                    image=image,
                    description=description,
                    date=date,
                    location=location
                )
                event.save()
                messages.success(request, "New Event has been created successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

 
@login_required(login_url='login')
def completed_event(request, uuid):
    user = request.user
    if user.profile.is_admin:
        event = get_object_or_404(Event, uuid=uuid)
        event.is_completed = True
        event.save()
        messages.success(request, "Event status has been saved successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def delete_event(request, uuid):
    user = request.user
    if user.profile.is_admin:
        event = get_object_or_404(Event, uuid=uuid)
        event.delete()
        messages.success(request, "Event has been deleted successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))