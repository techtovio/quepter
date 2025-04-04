from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import UserWallet, Transaction
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import TransferForm
from club.models import Club
import os
from dotenv import load_dotenv
from wallet.contracts.hedera import load_operator_credentials, create_new_account, query_balance, transfer_token
load_dotenv()
from wallet.contracts import mirror_node
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.views.decorators.http import require_GET
import requests
from dashboard.models import Profile
from hiero_sdk_python import (
    Client,
    AccountId,
    PrivateKey,
    TransferTransaction,
    Network,
    TokenAssociateTransaction,
    TokenId
)
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

@login_required
def wallet_details(request):
    wallet = get_object_or_404(UserWallet, user=request.user)
    qpt_balance = mirror_node.get_token_balance_for_account(account_id=wallet.recipient_id, token_id=os.getenv('Token_ID'))
    context = {
        'qpt_public_key': wallet.qpt_public_key.split("hex=")[-1].strip(">"),
        'recipient_id': wallet.recipient_id,
        'qpt_balance': qpt_balance,
    }
    return render(request, 'wallet/wallet_details.html', context)

@login_required
def wallet_balance(request):
    user = request.user
    wallet = UserWallet.objects.get(user=user)
    network_type = os.getenv('NETWORK')
    token_id = os.getenv('Token_ID')
    balance = mirror_node.get_token_balance_for_account(account_id=wallet.recipient_id, token_id=token_id)
    print(balance)
    data = {
        'qpt_balance':balance
    }
    return JsonResponse(data)


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = [
        {
            'transaction_type': txn.transaction_type,
            'currency': txn.currency,
            'amount': txn.amount,
            'recipient_id': txn.recipient_id,
            'status': txn.status,
            'created_at': txn.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for txn in page_obj
    ]
    return JsonResponse({'transactions': data})

def associate_token(recipient_id_new, recipient_key_new):
    network = Network(network='testnet')
    client = Client(network)

    recipient_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    recipient_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    token_id = TokenId.from_string(os.getenv('Token_ID'))  # Update as needed
    client.set_operator(recipient_id, recipient_key)

    transaction = (
        TokenAssociateTransaction()
        .set_account_id(recipient_id_new)
        .add_token_id(token_id)
        .freeze_with(client)
        .sign(recipient_key_new)
    )

    try:
        receipt = transaction.execute(client)
        print("Token association successful.")
    except Exception as e:
        print(f"Token association failed: {str(e)}")

def assign_user_wallets(request):
    operator_id, operator_key = load_operator_credentials()
    network_type = os.getenv('NETWORK')
    token_id = os.getenv('Token_ID')
    network = Network(network=network_type)
    client = Client(network)
    client.set_operator(operator_id, operator_key)
    # Handle User Wallets
    users = User.objects.all()
    for user in users:
        name = user.get_full_name()
        try:
            recipient_id, recipient_private_key, new_account_public_key = create_new_account(name, client)
            #associate_token(client, recipient_id, recipient_private_key, [token_id])
            associate_token(recipient_id, recipient_private_key)
            UserWallet.objects.create(user=user, qpt_public_key=new_account_public_key, qpt_private_key=recipient_private_key, recipient_id=recipient_id)
        except Exception as e:
            print(e)
    return render(request, 'contracts/assign_user_wallet.html')

def assign_club_wallets(request):
    operator_id, operator_key = load_operator_credentials()

    network_type = os.getenv('NETWORK')
    token_id = os.getenv('Token_ID')
    network = Network(network=network_type)
    client = Client(network)
    client.set_operator(operator_id, operator_key)
    # Handle Club Wallets
    clubs = Club.objects.all()
    for club in clubs:
        name = club.name
        try:
            recipient_id, recipient_private_key, new_account_public_key = create_new_account(name, client)
            #associate_token(client, recipient_id, recipient_private_key, [token_id])
            associate_token(recipient_id, recipient_private_key)
            club.app_id = recipient_id
            club.public_key = new_account_public_key
            club.qpt_private_key = recipient_private_key
            club.save()
        except Exception as e:
            print(e)
    return render(request, 'contracts/assign_user_wallet.html')

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

def fund_clubs(request):
    clubs = Club.objects.all()#ADMIN_KEY
    operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
    operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
    for club in clubs:
        recipient_id = AccountId.from_string(club.app_id)
        transfer_tokens(operator_id_sender=operator_id, operator_key_sender=operator_key, recipient_id=recipient_id, amount=1000)
    return render(request, 'contracts/assign_user_wallet.html')

@login_required
@require_POST
def buy_qpt(request):
    try:
        amount = float(request.POST.get('amount'))
        if amount <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Amount must be greater than zero'
            }, status=400)
            
        conversion_rate = float(10)  # 1 QPT = 10 KES
        required_funds = amount * conversion_rate
        
        if request.user.profile.funds < required_funds:
            return JsonResponse({
                'status': 'error',
                'message': f"Insufficient funds. You need KES {required_funds:.2f} to buy {amount} QPT."
            }, status=400)
        
        operator_id = AccountId.from_string(os.getenv('OPERATOR_ID'))
        operator_key = PrivateKey.from_string(os.getenv('OPERATOR_KEY'))
        recipient_id = AccountId.from_string(request.user.wallet.recipient_id)
        
        transfer_success = transfer_tokens(
            operator_id_sender=operator_id,
            operator_key_sender=operator_key,
            recipient_id=recipient_id,
            amount=int(amount)
        )
        
        if not transfer_success:
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction failed. Please try again.'
            }, status=500)
        
        # Update user funds
        profile = Profile.objects.get(user=request.user)
        profile.funds -= required_funds
        profile.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully purchased {amount} QPT!',
            'new_fiat_balance': f"{request.user.profile.funds:.2f}",
            #'new_qpt_balance': f"{Decimal(request.user.wallet.qpt_balance) + amount:.2f}"
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)

TESTNET_MIRROR_URL = os.getenv('MIRROR_URL')#"https://testnet.mirrornode.hedera.com/api/v1"

@never_cache
def token_info(request):
    token_id = os.getenv('Token_ID')
    url = f"https://testnet.mirrornode.hedera.com/api/v1/tokens/{token_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        return JsonResponse({
            'status': 'success',
            'name': data.get('name', 'Unknown'),
            'symbol': data.get('symbol', 'UNK'),
            'total_supply': int(data.get('total_supply', 0)),
            'decimals': int(data.get('decimals', 0)),
            'token_id': token_id,
            'timestamp': response.headers.get('Date', '')
        })
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_GET
def account_balance(request):
    account_id = os.getenv('OPERATOR_ID')
    token_id = os.getenv('Token_ID')
    
    try:
        response = requests.get(f"{TESTNET_MIRROR_URL}/accounts/{account_id}/tokens")
        response.raise_for_status()
        tokens = response.json().get('tokens', [])
        
        balance = next(
            (int(token['balance']) for token in tokens if token['token_id'] == token_id),
            0
        )
        
        return JsonResponse({
            'account_id': account_id,
            'balance': balance,
            'status': 'success'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_GET
def token_holders(request):
    token_id = os.getenv('Token_ID')
    if not token_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Token_ID not configured'
        }, status=500)

    try:
        # Get page number from request (default to 1)
        page = int(request.GET.get('page', 1))
        per_page = 10  # Show 10 holders per page
        
        # Get all holders from mirror node
        response = requests.get(
            f"https://testnet.mirrornode.hedera.com/api/v1/tokens/{token_id}/balances",
            params={'limit': 100},  # Get top 100 holders
            timeout=5
        )
        response.raise_for_status()
        
        holders_data = response.json().get('balances', [])
        
        # Process and sort holders
        all_holders = sorted(
            [
                {
                    'account': holder['account'],
                    'balance': int(holder['balance'])
                }
                for holder in holders_data
                if int(holder['balance']) > 0
            ],
            key=lambda x: -x['balance']  # Sort by balance descending
        )
        
        # Calculate pagination
        total_holders = len(all_holders)
        total_pages = (total_holders + per_page - 1) // per_page
        start_index = (page - 1) * per_page
        paginated_holders = all_holders[start_index:start_index + per_page]
        
        return JsonResponse({
            'status': 'success',
            'holders': paginated_holders,
            'total_circulating': sum(h['balance'] for h in all_holders),
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_holders': total_holders,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)