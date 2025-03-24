from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Club, ClubMembership, ClubBroadcast, ClubContribution
from django.contrib.auth.decorators import user_passes_test
from dashboard.models import Profile, Notification
from decimal import Decimal
from django.http import HttpResponseRedirect

@login_required
def club_detail(request, uuid):
    """Shows the details of a specific club, including broadcasts if the user is a member."""
    club = get_object_or_404(Club, uuid=uuid)
    is_member = club.members.filter(id=request.user.id).exists()
    broadcasts = ClubBroadcast.objects.filter(club=club).order_by('-created_at') if is_member else None
    try:
        membership = ClubMembership.objects.filter(user=request.user, club=club).first()
        total_contributed = membership.total_contributed
        loyalty_points = membership.loyalty_points
    except Exception as e:
        total_contributed = 0.00
        loyalty_points = 0.00
        

    return render(request, 'clubs/club_details.html', {
        'club': club,
        'is_member': is_member,
        'broadcasts': broadcasts,
        'notifications':Notification.objects.filter(user=request.user),
        'weekly_contributions': club.weekly_contribution_amount,
        'total_contributions': total_contributed,
        'loyalty_points': loyalty_points,
        'annual_returns': club.calculate_annual_returns(),
    })

@user_passes_test(lambda u: u.is_staff)
@login_required
def create_broadcast(request, uuid):
    """Allows authorized admins to send a broadcast message to all club members."""
    club = get_object_or_404(Club, uuid=uuid)
    
    if request.method == "POST":
        message = request.POST.get('message')
        if message:
            ClubBroadcast.objects.create(club=club, message=message)
            messages.success(request, "Broadcast message sent successfully.")
        else:
            messages.warning(request, "Message cannot be empty.")
        
        return redirect('club_detail', uuid=club.uuid)
    
    return render(request, 'clubs/create_broadcast.html', {'club': club, 'notifications':Notification.objects.filter(user=request.user),})


@login_required
def club_list(request):
    """Displays all available clubs attractively, with joined clubs shown at the top."""
    # Clubs the user has already joined
    joined_clubs = Club.objects.filter(members=request.user)
    
    # Clubs the user has not joined
    other_clubs = Club.objects.exclude(members=request.user)
    
    # Pass both joined_clubs and other_clubs to the template
    return render(
        request,
        'clubs/club_list.html',
        {
            'joined_clubs': joined_clubs,
            'clubs': other_clubs,
            'notifications': Notification.objects.filter(user=request.user),
        }
    )

@login_required
def join_club(request, uuid):
    """Handles the logic for joining a club."""
    club = get_object_or_404(Club, uuid=uuid)
    profile = Profile.objects.get(user=request.user)
    referrer = Profile.objects.get(user=profile.referrer)
    
    # Check if the user is already a member
    if club.members.filter(id=request.user.id).exists():
        messages.warning(request, "You are already a member of this club.")
        return redirect('club_detail', uuid=club.uuid)
    
    # Deduct funds and create membership if user confirms
    if profile.funds >= int(club.joining_amount):
        profile.funds -= int(club.joining_amount)
        profile.save()
        # Award points to the referrer
        if club.name == "Business & Entrepreneurship":
            profile.is_verified = True
            # Award points to the referrer
            referrer.points += Decimal('2')
            # Award points to the referred user
            profile.points += Decimal('0.5')
            Notification.objects.create(
                user=profile.user,
                title="Welcome to Quepter Youth Hub",
                message = f"Hello {profile.name()}, you have been awarded 0.5 points for completing Quepter youth Hub membership process."
            )
            Notification.objects.create(
                user=referrer.user,
                title="Congratulations! Referral Award",
                message = f"Hello {referrer.name()}, you have been awarded 2 points for successfully inviting a friend, see your new earned badge at your profile."
            )
            referrer.save()
            profile.save()
            messages.success(request, "Congratulations, you have completed your registration process successfully, start your new journey by exploring our funding opportunities.")
            return redirect("dashboard")
        ClubMembership.objects.create(user=request.user, club=club, has_paid_membership_fee=True)
        messages.success(request, f"You have successfully joined {club.name}.")
    else:
        messages.warning(request, f"Insufficient funds to join this club, please add funds to your account, you funds KES {profile.funds}")
    return redirect('club_detail', uuid=club.uuid)


def contribute_to_club(request, uuid):
    if request.method == 'POST':
        club = get_object_or_404(Club, uuid=uuid)
        user = request.user
        amount = float(request.POST.get('amount', 0))
        
        if amount <= 0:
            messages.warning(request, f"Invalid amount, please enter a valid amount!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            profile = Profile.objects.get(user=user)
            if profile.funds >= int(amount):
                profile.points += int(int(amount)//10)
                profile.funds -= int(amount)
                profile.save()
                # Create a contribution record
                ClubContribution.objects.create(
                    user=request.user,
                    club=club,
                    amount=amount
                )
                #contribution.save()
                messages.success(request, "You are a real legend, keep contributing and see your profile grow!")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.warning(request, "You don't have enough funds in you account to complete this action, please add funds and try again")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))