from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from post.models import CommunityPost, CommunityPostComment, CommunityPostLike
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from uuid import uuid4
from django.contrib.auth.decorators import login_required
from dashboard.models import Profile, Notification
import json
from django.contrib import messages

@login_required(login_url='login')
def create_post(request):
    if request.method == "POST":
        user = request.user
        title = request.POST['title']
        content = request.POST['content']
        category = request.POST['category']
        if title and content:
            CommunityPost.objects.create(title=title, content=content, author=user, category=category)#category=category
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def post_comment(request, uuid):
    post = get_object_or_404(CommunityPost, uuid=uuid)
    if request.method == "POST":
        user = request.user
        comment = request.POST['comment']
        if comment:
            CommunityPostComment.objects.create(post=post, user=user, comment=comment)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
def deletePost(request, uuid):
    user = request.user
    post = get_object_or_404(CommunityPost, uuid=uuid)
    post.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def editPostView(request, uuid):
    user = request.user
    post = get_object_or_404(CommunityPost, uuid=uuid)
    context = {
        'post':post,
        'notifications':Notification.objects.filter(user=request.user),
    }
    return render(request, 'dashboard/post.html', context)

@login_required(login_url='login')
def editPost(request, uuid):
    user = request.user
    post = get_object_or_404(CommunityPost, uuid=uuid)
    title = request.POST['title']
    content = request.POST['content']
    category = request.POST['category']
    post.title = title
    post.content = content
    post.category = category
    post.save()
    messages.success(request, "Your post has been edited successfully")
    #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('dashboard')

csrf_exempt
def like_post_ajax(request):
    if request.method == 'POST':
        try:
            user=request.user
            data = json.loads(request.body)
            post_id = data.get('post_id')
            post = CommunityPost.objects.get(uuid=post_id)
            try:
                like = CommunityPostLike.objects.get(user=user, post=post)
                like.delete()
            except CommunityPostLike.DoesNotExist:
                like = CommunityPostLike.objects.create(user=user, post=post)
            return JsonResponse({'success': True, 'likes': post.likes()})
        except CommunityPost.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_comment_ajax(request, uuid):
    if request.method == 'POST':
        user=request.user
        post = CommunityPost.objects.get(uuid=uuid)
        comment_text = json.loads(request.body).get('comment')
        if comment_text:
            new_comment = CommunityPostComment.objects.create(
                post=post,
                user=request.user,
                comment=comment_text,
                timestamp=timezone.now()
            )
            # Retrieve the profile image
            try:
                profile = Profile.objects.get(user=request.user)
                profile_image = profile.image.url
            except:
                # Handle case where Profile doesn't exist
                profile_image = '/static/person.webp'
            
            return JsonResponse({
                'success': True,
                'username': f'{user.first_name} {user.last_name}',
                'comment': new_comment.comment,
                'timestamp': new_comment.timestamp.strftime('%b %d, %Y %I:%M %p'),
                'profileImage': profile_image
            })
    return JsonResponse({'success': False})

@login_required(login_url='login')
def post_detail(request, uuid):
    user = request.user
    post = get_object_or_404(CommunityPost, uuid=uuid)
    comments = CommunityPostComment.objects.filter(post=post).order_by('timestamp')
    profile = Profile.objects.get(user=user)
    context = {
        'post': post,
        'comments': comments,
        'profile':profile,
        'notifications':Notification.objects.filter(user=user),
    }
    return render(request, 'dashboard/comments.html', context)