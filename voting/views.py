from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Vote, Candidate, Blockchain, LeadershipPosition
import hashlib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from dashboard.models import Notification

@login_required(login_url='login')
def leadership(request):
    position = LeadershipPosition.objects.all()
    return render(request, 'vote/vote.html', {'positions':position, 'notifications':Notification.objects.filter(user=request.user),})

@login_required
@csrf_exempt
def cast_vote_ajax(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        candidate = Candidate.objects.get(id=candidate_id)

        # Ensure user hasn't already voted for this position
        if Vote.objects.filter(user=request.user, candidate__position=candidate.position).exists():
            return JsonResponse({'error': "You have already voted for this position."}, status=400)

        # Create the vote
        vote = Vote.objects.create(user=request.user, candidate=candidate)

        # Generate a hash for the vote (blockchain)
        previous_block = Blockchain.objects.last()
        previous_hash = previous_block.block_hash if previous_block else "0"
        vote_data = f"{vote.user.id}{vote.candidate.id}{previous_hash}".encode('utf-8')
        block_hash = hashlib.sha256(vote_data).hexdigest()

        # Create the blockchain entry
        Blockchain.objects.create(previous_hash=previous_hash, vote=vote, block_hash=block_hash)

        return JsonResponse({'success': "Your vote has been cast securely."}, status=200)

    return JsonResponse({'error': "Invalid request."}, status=400)

@login_required
@csrf_exempt
def apply_leadership_ajax(request):
    if request.method == 'POST':
        position_id = request.POST.get('position_id')
        position = LeadershipPosition.objects.get(id=position_id)
        
        user_profile = request.user.profile
        
        # Ensure user meets point and referral requirements
        if user_profile.points < position.points_required or user_profile.referred_friends.count() < 5:
            return JsonResponse({'error': "You do not meet the requirements."}, status=400)
        
        # Apply for leadership
        Candidate.objects.create(user=request.user, position=position, points=user_profile.points, referral_count=user_profile.referred_friends.count())

        return JsonResponse({'success': "You have applied for leadership."}, status=200)

    return JsonResponse({'error': "Invalid request."}, status=400)

@login_required(login_url='login')
def create_position(request):
    user = request.user
    if user.profile.is_admin:
        if request.method == "POST":
            title = request.POST['title']
            description = request.POST['description']
            points_required = request.POST['points_required']
            if title and description and points_required:
                position = LeadershipPosition.objects.create(
                    title=title,
                    description=description,
                    points_required=points_required,
                )
                position.save()
                messages.success(request, "New Leadership position has been created successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))