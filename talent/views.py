from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Talent, Booking, Review, Follower, TALENT_CATEGORIES
from .forms import TalentForm, BookingForm, ReviewForm
from django.utils import timezone
from django.db.models import Avg, Count

def talent_list(request):
    talents = Talent.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating')
    categories = dict(TALENT_CATEGORIES)
    return render(request, 'talents/talent_list.html', {
        'talents': talents,
        'categories': categories
    })

def talent_detail(request, uuid):
    talent = get_object_or_404(Talent, uuid=uuid)
    is_following = False
    if request.user.is_authenticated:
        is_following = Follower.objects.filter(
            user=request.user,
            talent=talent
        ).exists()
    
    # Get available booking slots (example logic)
    available_slots = [
        timezone.now() + timezone.timedelta(days=i) 
        for i in range(1, 15) 
        if i % 2 == 0  # Just example availability logic
    ]
    
    return render(request, 'talents/talent_detail.html', {
        'talent': talent,
        'is_following': is_following,
        'available_slots': available_slots,
        'reviews': talent.reviews.select_related('user'),
        'booking_form': BookingForm(),
        'review_form': ReviewForm()
    })

@login_required
def create_talent(request):
    if request.method == 'POST':
        form = TalentForm(request.POST, request.FILES)
        if form.is_valid():
            talent = form.save(commit=False)
            talent.user = request.user
            talent.club = request.user.club_memberships.first().club  # Assuming user belongs to a club
            talent.save()
            messages.success(request, 'Talent profile created successfully!')
            return redirect('talent_detail', uuid=talent.uuid)
    else:
        form = TalentForm()
    return render(request, 'talents/talent_form.html', {'form': form})

@login_required
def book_talent(request, uuid):
    talent = get_object_or_404(Talent, uuid=uuid)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.talent = talent
            booking.save()
            messages.success(request, 'Booking request sent successfully!')
            return redirect('talent_detail', uuid=talent.uuid)
    return redirect('talent_detail', uuid=talent.uuid)

@login_required
def add_review(request, uuid):
    talent = get_object_or_404(Talent, uuid=uuid)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.talent = talent
            review.save()
            talent.calculate_rating()
            messages.success(request, 'Review added successfully!')
    return redirect('talent_detail', uuid=talent.uuid)

@login_required
def toggle_follow(request, uuid):
    talent = get_object_or_404(Talent, uuid=uuid)
    follower, created = Follower.objects.get_or_create(
        user=request.user,
        talent=talent
    )
    if not created:
        follower.delete()
        messages.success(request, f'Unfollowed {talent.name}')
    else:
        messages.success(request, f'Now following {talent.name}')
    return redirect('talent_detail', uuid=talent.uuid)