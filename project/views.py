from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.core.exceptions import ValidationError
from wallet.models import UserWallet
from dotenv import load_dotenv
from wallet.contracts import mirror_node
import os
from .models import Proposal
from .forms import ProposalForm
from club.models import Club, ClubMembership
import binascii
load_dotenv()
from hiero_sdk_python import (
    Client,
    AccountId,
    PrivateKey,
    TransferTransaction,
    Network,
    TokenAssociateTransaction,
    TokenId
)

def transfer_tokens(operator_id_sender, operator_key_sender, recipient_id, amount):
    network_type = os.getenv('NETWORK')
    network = Network(network=network_type)
    client = Client(network)

    operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    token_id = TokenId.from_string(os.getenv('Token_ID'))

    client.set_operator(operator_id, operator_key)

    transaction = (
        TransferTransaction()
        .add_token_transfer(token_id, operator_id_sender, -amount)
        .add_token_transfer(token_id, recipient_id, amount)
        .freeze_with(client)
        .sign(operator_key_sender)
    )

    try:
        receipt = transaction.execute(client)
        print("Token transfer successful.")
        return True
    except Exception as e:
        print(f"Token transfer failed: {str(e)}")
        return False

class ProposalCreateView(View):
    def get(self, request):
        form = ProposalForm()
        return render(request, 'proposals/proposal_form.html', {'form': form})

    def post(self, request):
        form = ProposalForm(request.POST)
        if form.is_valid():
            try:
                # Ensure that user have sufficient QPT before anything
                wallet = UserWallet.objects.get(user=request.user)
                network_type = os.getenv('NETWORK')
                token_id = os.getenv('Token_ID')
                club = form.cleaned_data.get('club')
                club_id = AccountId.from_string(club.app_id)
                operator_id = AccountId.from_string(request.user.wallet.recipient_id)
                operator_key = PrivateKey.from_string(request.user.wallet.decrypt_key().split("hex=")[-1].strip(">"))
                membership = ClubMembership.objects.filter(club=club, user=request.user)
                if membership:
                    pass
                else:
                    messages.warning(request, f'You must be a member of {club} before proposing a project under this club.')
                    return redirect('proposal_create')
                balance = mirror_node.get_token_balance_for_account(account_id=wallet.recipient_id, token_id=token_id)
                if balance >= 2:
                    transaction = transfer_tokens(operator_id_sender=operator_id, operator_key_sender=operator_key, recipient_id=club_id, amount=2)
                    print(transaction)
                    if transaction == True:
                        proposal = form.save(commit=False)
                        proposal.created_by = request.user
                        proposal.evaluate()  # AI evaluation before saving
                        proposal.save()
                        # Return feedback immediately after evaluation
                        #return JsonResponse({
                        #    'status': 'success',
                        #    'message': 'Proposal submitted successfully.',
                        #    'feedback': proposal.feedback,
                        #    'proposal_status': proposal.status,
                        #    'proposal_outcome': proposal.outcome
                        #})
                        messages.success(request, f'Proposal Submitted successfully.')
                        return redirect('proposal_create')
                    else:
                        messages.warning(request, 'An Error occured while trying to transfer your QPT, please try again later')
                        return redirect('proposal_create')
                else:
                    messages.warning(request, f'You have insufficient QPT to propose a project, your QPT balance is {balance}.')
                    return redirect('proposal_create')
            except ValidationError as e:
                messages.warning(request, f'We encountered an error trying to validate your forms {e}.')
                return redirect('proposal_create')
            except Exception as e:
                messages.warning(request, f'An error occured {e}.')
                return redirect('proposal_create')
        else:
            messages.warning(request, f'You have insufficient QPT to propose a project, your QPT balance is {balance}.')
            return redirect('proposal_create')

class ProposalListView(ListView):
    model = Proposal
    template_name = 'proposals/proposal_list.html'
    context_object_name = 'proposals'

    def get_queryset(self):
        return Proposal.objects.filter(created_by=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user's proposals
        user_proposals = Proposal.objects.filter(created_by=self.request.user)

        # Analytics
        context['total_projects'] = user_proposals.count()
        context['accepted_projects'] = user_proposals.filter(status='approved').count()
        context['rejected_projects'] = user_proposals.filter(status='rejected').count()
        context['pending_projects'] = user_proposals.filter(status='pending').count()

        return context


class ProposalDetailView(DetailView):
    model = Proposal
    template_name = 'proposals/proposal_detail.html'
    context_object_name = 'proposal'

@login_required
def proposal_feedback(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk, created_by=request.user)
    
    return JsonResponse({
        'feedback': proposal.feedback,
        'status': proposal.status,
        'outcome': proposal.outcome
    })
