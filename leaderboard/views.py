from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Leaderboard, Challenge, UserChallengeParticipation, Reward
from django.utils import timezone
from dashboard.models import Notification

@login_required
def leaderboard_view(request):
    if request.is_ajax():
        leaderboard = Leaderboard.objects.select_related('user').all()
        data = [
            {
                "rank": idx + 1,
                "user": entry.user.username,
                "points": entry.points
            } for idx, entry in enumerate(leaderboard)
        ]
        return JsonResponse({"leaderboard": data}, safe=False)
    return render(request, 'leaderboard/leaderboard.html', {'notifications':Notification.objects.filter(user=request.user),})

@login_required
def challenges_view(request):
    if request.is_ajax():
        active_challenges = Challenge.objects.filter(is_active=True)
        user_participation = UserChallengeParticipation.objects.filter(user=request.user)
        data = [
            {
                "id": challenge.uuid,
                "name": challenge.name,
                "description": challenge.description,
                "points_awarded": challenge.points_awarded,
                "completed": user_participation.filter(challenge=challenge, completed=True).exists()
            } for challenge in active_challenges
        ]
        return JsonResponse({"challenges": data}, safe=False)
    return render(request, 'leaderboard/challenges.html')

@login_required
def complete_challenge(request, challenge_id):
    if request.method == "POST" and request.is_ajax():
        challenge = get_object_or_404(Challenge, uuid=challenge_id)
        user_participation, created = UserChallengeParticipation.objects.get_or_create(
            user=request.user, 
            challenge=challenge
        )
        if not user_participation.completed:
            user_participation.completed = True
            user_participation.date_completed = timezone.now()
            user_participation.save()

            # Update user points in the leaderboard
            leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=request.user)
            leaderboard_entry.points += challenge.points_awarded
            leaderboard_entry.save()

        return JsonResponse({"message": "Challenge completed!", "points": leaderboard_entry.points})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def redeem_rewards(request):
    if request.is_ajax():
        available_rewards = Reward.objects.filter(is_active=True)
        data = [
            {
                "id": reward.id,
                "name": reward.name,
                "description": reward.description,
                "points_required": reward.points_required,
            } for reward in available_rewards
        ]
        return JsonResponse({"rewards": data}, safe=False)
    return render(request, 'leaderboard/rewards.html')
