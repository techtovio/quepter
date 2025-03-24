from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Project, ChatMessage
from django.contrib.auth.models import User
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from dashboard.models import Profile, Notification
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .contracts.proposal_fee_contract import pay_proposal_fee
from .contracts.backing_contract import back_project
from .models import Proposal, Backing

@login_required(login_url='login')
def projects(request):
    projects = Project.objects.filter(is_completed=False)
    return render(request, 'dashboard/projects.html', {
        'projects': projects,
        'notifications':Notification.objects.filter(user=request.user),
    })

@login_required(login_url='login')
def load_chat_messages(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    messages = ChatMessage.objects.filter(project=project).order_by('timestamp').values('user__first_name', 'message', 'timestamp')
    return JsonResponse(list(messages), safe=False)

@csrf_exempt
def send_chat_message(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        data = json.loads(request.body)
        message = data.get('message')
        user = request.user

        if message:
            ChatMessage.objects.create(project=project, user=user, message=message)
            return JsonResponse({'status': 'Message sent successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='login')
def project_detail(request, uuid):
    user=request.user
    project = get_object_or_404(Project, uuid=uuid)
    chat_messages = ChatMessage.objects.filter(project=project).order_by('timestamp')

    return render(request, 'dashboard/project_detail.html', {
        'project': project,
        'chat_messages': chat_messages,
        'notifications':Notification.objects.filter(user=user),
    })



@csrf_exempt
@login_required(login_url='login')
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')
        project_uuid = data.get('project_uuid')  # Make sure to pass the project's UUID from the front-end
        
        project = Project.objects.get(uuid=project_uuid)  # Fetch the project by UUID
        user = User.objects.get(id=request.user.id)

        # Save the message
        new_message = ChatMessage.objects.create(
            project=project,
            user=user,
            message=content
        )
        new_message.save()

        # Return the response
        response_data = {
            'success': True,
            'author': user.username,
            'content': new_message.message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse(response_data)
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def vote_project(request, uuid):
    if request.method == 'POST' and request.is_ajax():
        project = Project.objects.get(uuid=uuid)
        
        # Increment the vote count
        project.votes += 1
        project.save()

        return JsonResponse({'success': True, 'total_votes': project.votes})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='login')
def get_user_points(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    points = profile.points
    return JsonResponse({"points": points})

@login_required(login_url='login')
def propose_project(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Check if user has enough points
        profile = Profile.objects.get(user=user)
        if profile.points < 100:
            messages.warning(request, "You need at least 100 points to propose a project")#JsonResponse({"status": "error", "message": "You need at least 100 points to propose a project."})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Check if the uploaded file is an image
        if image and image.content_type.split('/')[0] != 'image':
            messages.warning(request, "The uploaded file is not a valid image")#JsonResponse({"status": "error", "message": "The uploaded file is not a valid image."})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Resize the image (e.g., to 800x800 pixels)
        try:
            img = Image.open(image)
            img = img.convert('RGB')  # Convert to RGB in case it's in another format (e.g., PNG with transparency)
            img.thumbnail((350, 350))  # Resize to max width/height of 800px

            # Save resized image to a BytesIO object
            image_io = io.BytesIO()
            img.save(image_io, format='JPEG')

            # Create a new InMemoryUploadedFile for the resized image
            image_file = InMemoryUploadedFile(
                image_io, None, 'resized_image.jpg', 'image/jpeg', image_io.tell(), None
            )

        except Exception as e:
            messages.warning(request, "Error processing image: " + str(e))#JsonResponse({"status": "error", "message": "Error processing image: " + str(e)})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Save the project with the resized image
        project = Project.objects.create(
            title=title,
            description=description,
            image=image_file,  # Save the resized image
            user=user
        )

        # Deduct points and save the profile
        profile.points -= 100
        profile.save()

        messages.success(request, f"Conratulations {user.first_name}! Your Project has been proposed and approved successfully!")#JsonResponse({"status": "success", "message": "Project proposed successfully!"})
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    messages.warning(request, "Invalid request method.")#JsonResponse({"status": "error", "message": "Invalid request method."})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




#####################################

@api_view(['POST'])
def submit_proposal(request):
    title = request.data.get('title')
    description = request.data.get('description')
    club_id = request.data.get('club_id')
    user = request.user
    
    try:
        # AI Threshold Calculation
        threshold = calculate_backing_threshold(1000, 0.2)

        pay_proposal_fee(user.wallet_address, club_id, threshold)

        proposal = Proposal.objects.create(
            title=title,
            description=description,
            created_by=user,
            club_id=club_id,
            fee_paid=True
        )
        proposal.save()

        return Response({"message": "Proposal submitted successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
def back_project(request):
    proposal_id = request.data.get('proposal_id')
    amount = request.data.get('amount')
    user = request.user

    try:
        proposal = Proposal.objects.get(id=proposal_id)
        back_project(user.wallet_address, proposal.club.id, amount)

        backing = Backing.objects.create(
            backer=user,
            proposal=proposal,
            amount=amount
        )
        backing.save()

        return Response({"message": "Backing successful"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)