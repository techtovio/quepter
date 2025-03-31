from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import DAO, Proposal, Vote, Member

def dao_home(request):
    dao = DAO.objects.first()  # Only one DAO exists
    is_member = Member.objects.filter(user=request.user, dao=dao).exists() if request.user.is_authenticated else False
    active_proposals = Proposal.objects.filter(dao=dao, status='active')
    
    # Create a dictionary of voting status for each proposal
    user_has_voted = {}
    if request.user.is_authenticated:
        for proposal in active_proposals:
            user_has_voted[proposal.id] = Vote.objects.filter(
                proposal=proposal, 
                voter=request.user
            ).exists()

    context = {
        'dao': dao,
        'is_member': is_member,
        'active_proposals': active_proposals,
        'user_has_voted': user_has_voted,  # Pass the dictionary directly
        'user_voting_power': 100.00 if is_member else 0,
    }
    return render(request, 'dao/dao.html', context)

@login_required
def create_proposal(request):
    if request.method == 'POST':
        dao = DAO.objects.first()
        proposal = Proposal.objects.create(
            dao=dao,
            creator=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
        )
        return JsonResponse({'success': True, 'proposal_id': proposal.id})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def vote(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    Vote.objects.create(
        proposal=proposal,
        voter=request.user,
        vote=request.POST.get('vote')
    )
    return JsonResponse({'success': True})