from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import OneOnOneMentorship, GroupMentorship, MentorshipMessage
from dashboard.models import Notification

# Main mentorship page
@login_required
def mentorship_page(request):
    # Load user's one-on-one mentorship and group mentorship
    one_on_one_mentorship = OneOnOneMentorship.objects.filter(mentee=request.user).first()
    group_mentorship = GroupMentorship.objects.filter(members=request.user).first()

    return render(request, 'mentorship.html', {
        'one_on_one_mentorship': one_on_one_mentorship,
        'group_mentorship': group_mentorship,
        'notifications':Notification.objects.filter(user=request.user),
    })

# Send one-on-one message
@login_required
def send_one_on_one_message(request):
    if request.method == 'POST':
        mentorship_id = request.POST.get('mentorship_id')
        mentorship = get_object_or_404(OneOnOneMentorship, id=mentorship_id)
        message = request.POST.get('message')
        MentorshipMessage.objects.create(sender=request.user, receiver=mentorship.mentor, message=message, mentorship=mentorship)
        return JsonResponse({'status': 'success'})

# Send group message
@login_required
def send_group_message(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(GroupMentorship, id=group_id)
        message = request.POST.get('message')
        MentorshipMessage.objects.create(sender=request.user, message=message, group_mentorship=group)
        return JsonResponse({'status': 'success'})

# Load one-on-one messages (AJAX)
@login_required
def load_one_on_one_messages(request, mentorship_id):
    mentorship = get_object_or_404(OneOnOneMentorship, id=mentorship_id)
    messages = MentorshipMessage.objects.filter(mentorship=mentorship).order_by('sent_at')
    return render(request, 'mentorship/messages.html', {'messages': messages})

# Load group messages (AJAX)
@login_required
def load_group_messages(request, group_id):
    group = get_object_or_404(GroupMentorship, id=group_id)
    messages = MentorshipMessage.objects.filter(group_mentorship=group).order_by('sent_at')
    return render(request, 'mentorship/messages.html', {'messages': messages})
