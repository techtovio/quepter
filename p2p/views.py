from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import PointTransfer, PointSale, PointTransaction
from django.contrib.auth.models import User
from django.db import transaction
from dashboard.models import Profile, Notification
import json

@login_required(login_url='login')
def p2p(request):
    return render(request, "dashboard/p2p.html", {'notifications':Notification.objects.filter(user=request.user),})

@login_required
def sell_points(request):
    if request.method == 'POST':
        points = int(request.POST.get('points'))
        price = float(request.POST.get('price'))

        seller = request.user
        if seller.profile.points >= points:
            with transaction.atomic():
                PointSale.objects.create(seller=seller, points=points, price=price)
                seller.profile.points -= points
                seller.profile.save()
                Notification.objects.create(
                    user=seller,
                    title="Points Listed Successfully",
                    message=f"Dear {seller.first_name}, you have successfully listed {points} for sale at kes {price} per point"
                )
                return JsonResponse({'status': 'success', 'message': 'Points listed for sale!'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Insufficient points'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@require_POST
def list_for_sale(request):
    points = int(request.POST.get('points'))
    price = 10#int(request.POST.get('price'))

    if points < 9:
        return JsonResponse({'success': False, 'error': 'Invalid points to list for sale, ensure that you have atleast 10 points.'})

    # Ensure user has enough points to sell
    profile = request.user.profile
    if profile.points < points:
        return JsonResponse({'success': False, 'error': 'Insufficient points to list for sale.'})

    # Deduct points and create a sale record
    profile.points -= points
    profile.save()

    point_to_deduct = int(points/10)
    points_after_deduction = points-point_to_deduct

    PointSale.objects.create(
        seller=request.user,
        points=points_after_deduction,
        price=price*points_after_deduction
    )

    return JsonResponse({'success': True})

@login_required
def get_available_sales(request):
    sales = PointSale.objects.filter(status='available').order_by('-created_at')[:10]
    sales_data = [
        {
            'id': sale.id,
            'seller': sale.seller.first_name + ' ' + sale.seller.last_name,
            'points': sale.points,
            'price': float(sale.price),
            'is_own': sale.seller == request.user,  # True if the sale belongs to the logged-in user
        }
        for sale in sales
    ]
    return JsonResponse({'sales': sales_data})
    
@login_required
@require_POST
def buy_points(request):
    try:
        data = json.loads(request.body)
        sale_id = data.get('sale_id')
        sale = PointSale.objects.get(id=sale_id, status='available')

        buyer_profile = request.user.profile

        if buyer_profile.funds < sale.price:
            return JsonResponse({'success': False, 'error': 'Insufficient funds to buy points.'})
        
        # Process the sale
        seller_profile = sale.seller.profile
        seller_profile.points -= sale.points
        buyer_profile.points += sale.points
        seller_profile.funds += sale.price
        buyer_profile.funds -= sale.price

        seller_profile.save()
        buyer_profile.save()

        # Mark the sale as completed
        sale.status = 'sold'
        sale.save()

        # Create a notification for the seller
        Notification.objects.create(
            user=sale.seller,
            message=f'{request.user.username} bought {sale.points} points from you for {sale.price} KES.'
        )

        return JsonResponse({'success': True})
    except PointSale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def transfer_points(request):
    try:
        recipient_code = request.POST.get('recipient_code')
        print(recipient_code)
        points = int(request.POST.get('points'))

        if points <= 0:
            return JsonResponse({'success': False, 'error': 'Points must be greater than zero.'})

        sender_profile = request.user.profile

        if sender_profile.points < points:
            return JsonResponse({'success': False, 'error': 'You do not have enough points to transfer.'})

        # Find the recipient by their profile code
        recipient_profile = Profile.objects.get(code=recipient_code)

        # Transfer the points
        sender_profile.points -= points
        recipient_profile.points += points
        sender_profile.save()
        recipient_profile.save()

        # Create a notification for the recipient
        Notification.objects.create(
            user=recipient_profile.user,
            message=f'{request.user.first_name} has transferred {points} points to you.'
        )

        return JsonResponse({'success': True})
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Recipient not found.'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid points value.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_user_points_and_notifications(request):
    profile = request.user.profile
    points = profile.points
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    notifications_data = [
        {"message": n.message, "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
        for n in notifications
    ]
    
    ## Mark notifications as read
    #notifications.update(is_read=True)
    
    return JsonResponse({
        "points": points,
        "notifications": notifications_data
    })

@login_required
@require_POST
def cancel_sale(request):
    try:
        sale_id = json.loads(request.body).get('sale_id')
        sale = PointSale.objects.get(id=sale_id, seller=request.user, status='available')
        sale.status = 'canceled'
        profile = sale.seller.profile
        profile.points += sale.points
        sale.save()
        profile.save()

        return JsonResponse({'success': True, 'message': 'Sale canceled successfully.'})
    except PointSale.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sale not found or already inactive.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def get_transaction_history(request):
    # Fetch the sales and purchases of the logged-in user
    sales = PointSale.objects.filter(seller=request.user).order_by('-created_at')
    purchases = PointSale.objects.filter(status='sold').exclude(seller=request.user).order_by('-created_at')

    # Prepare the data for both sales and purchases
    history_data = [
        {
            'transaction_type': 'sell',
            'points': sale.points,
            'price': float(sale.price),
            'date': sale.created_at.strftime('%Y-%m-%d %H:%M'),
            'related_user': sale.seller.username if sale.status == 'sold' else 'N/A',
            'status': sale.status.capitalize()  # Capitalize for display (Available, Sold, Canceled)
        }
        for sale in sales
    ] + [
        {
            'transaction_type': 'buy',
            'points': purchase.points,
            'price': float(purchase.price),
            'date': purchase.created_at.strftime('%Y-%m-%d %H:%M'),
            'related_user': purchase.seller.username,
            'status': 'Completed'
        }
        for purchase in purchases
    ]

    # Sort history data by date to show the most recent first
    history_data.sort(key=lambda x: x['date'], reverse=True)
    return JsonResponse({'history': history_data})