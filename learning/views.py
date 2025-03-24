from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LearningResource, Ebook
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from dashboard.models import Profile, Notification
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

@login_required(login_url='login')
def view_ebook(request, uuid):
    user = request.user
    ebook = get_object_or_404(Ebook, uuid=uuid)
    
    # Check if the user has paid for the ebook
    user_has_paid = False  # You will need to implement this logic with a payment gateway

    return render(request, 'learning/view.html', {'ebook': ebook, 'user_has_paid': user_has_paid, 'notifications':Notification.objects.filter(user=user),})

@login_required(login_url='login')
def pay_for_ebook(request, uuid):
    ebook = get_object_or_404(Ebook, uuid=uuid)
    user = request.user

    # Process payment (integrate your payment gateway here)
    
    # On successful payment:
    profile = Profile.objects.get(user=user)
    profile.points += 1  # Award 1 point for purchasing an ebook
    profile.save()

    return redirect('view_ebook', ebook_id=ebook.id)


@login_required(login_url='login')
def learning_resources_view(request):
    resources = LearningResource.objects.all()
    return render(request, 'learning/learning_resources.html', {'resources': resources, 'notifications':Notification.objects.filter(user=request.user),})

@csrf_exempt
def upload_resource(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            description = data.get('description')
            resource_type = data.get('resource_type')
            access_type = data.get('access_type')
            video_link = data.get('video_link', None)
            price = data.get('price', 0)
            
            # Save resource to DB
            resource = LearningResource.objects.create(
                title=title,
                description=description,
                resource_type=resource_type,
                access_type=access_type,
                video_link=video_link if resource_type == 'video' else None,
                price=price if access_type == 'paid' else None,
                created_by=request.user
            )
            messages.success(request, "Your Learning Resource has been uploaded successfully for review, we will notify you once approved.")
        except Exception as e:
            messages.warning(request, "An error occured while trying to upload your resource, please try again later!")
            #return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 