import json
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods

from .models import CommunityPost, CommunityAnswer, CommunityNotification
from .seed_data import ensure_community_seed_data
from .translator import translate_text

POPULAR_CROPS = [
    {"name": "Capsicum & Chilli", "icon": "🌶️"},
    {"name": "Tomato", "icon": "🍅"},
    {"name": "Pumpkin", "icon": "🎃"},
    {"name": "Zucchini", "icon": "🥒"},
    {"name": "Rice", "icon": "🌾"},
    {"name": "Wheat", "icon": "🌾"},
    {"name": "Cotton", "icon": "🌿"},
    {"name": "Groundnut", "icon": "🥜"},
    {"name": "Potato", "icon": "🥔"},
    {"name": "Onion", "icon": "🧅"},
]


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def feed_view(request):
    """Main Plantix-style Community Problem Feed."""
    ensure_community_seed_data()
    session_key = _ensure_session_key(request)

    crop_filter = request.GET.get('crop', '').strip()
    search_query = request.GET.get('q', '').strip()

    posts = CommunityPost.objects.prefetch_related('answers').all()

    if crop_filter and crop_filter.lower() != 'all':
        posts = posts.filter(crop__icontains=crop_filter)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(crop__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(author_name__icontains=search_query)
        )

    # User's notifications (logged in or session-based)
    if request.user.is_authenticated:
        user_notifs_qs = CommunityNotification.objects.filter(
            Q(recipient_user=request.user) | Q(recipient_session_key=session_key)
        )
    else:
        user_notifs_qs = CommunityNotification.objects.filter(recipient_session_key=session_key)

    unread_notifications_count = user_notifs_qs.filter(is_read=False).count()

    # If no notifications exist yet for this user/session, show recent community activity
    if user_notifs_qs.exists():
        notifications_list = list(user_notifs_qs[:10])
    else:
        notifications_list = list(CommunityNotification.objects.all()[:6])

    # User's session-stored votes
    user_votes = request.session.get('community_votes', {})
    answer_votes = request.session.get('community_answer_votes', {})

    context = {
        'posts': posts,
        'active_crop': crop_filter or 'All',
        'search_query': search_query,
        'crops': POPULAR_CROPS,
        'user_votes': user_votes,
        'answer_votes': answer_votes,
        'notifications': notifications_list,
        'unread_count': unread_notifications_count,
        'total_posts': CommunityPost.objects.count(),
    }
    return render(request, 'community/feed.html', context)


def ask_community_view(request):
    """Ask Community: Form for farmers to share problems publicly."""
    session_key = _ensure_session_key(request)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        crop = request.POST.get('crop', '').strip() or 'General'
        author_name = request.POST.get('author_name', '').strip()

        # If user is authenticated, use their name
        if request.user.is_authenticated:
            user_author = request.user
            if not author_name:
                author_name = getattr(request.user, 'full_name', '') or request.user.get_full_name() or request.user.username
        else:
            user_author = None
            if not author_name:
                author_name = 'Farmer'

        # Match crop icon
        crop_icon = '🌱'
        for c in POPULAR_CROPS:
            if c['name'].lower() in crop.lower() or crop.lower() in c['name'].lower():
                crop_icon = c['icon']
                break

        if not title:
            messages.error(request, 'Please provide a question indicating what is wrong with your crop.')
            return render(request, 'community/ask.html', {'crops': POPULAR_CROPS})

        image = request.FILES.get('image')

        post = CommunityPost.objects.create(
            author=user_author,
            author_session_key=session_key,
            author_name=author_name,
            author_location='India',
            crop=crop,
            crop_icon=crop_icon,
            title=title[:200],
            description=description[:2500],
            image=image,
            tags=f"#{crop}, #FarmerAdvice"
        )

        messages.success(request, 'Your question has been shared with the community! Fellow farmers & agronomists will answer soon.')
        return redirect(reverse('community:feed'))

    return render(request, 'community/ask.html', {'crops': POPULAR_CROPS})


def post_detail_view(request, post_id):
    """Detailed view of a community post with answer thread."""
    ensure_community_seed_data()
    post = get_object_or_404(CommunityPost.objects.prefetch_related('answers'), pk=post_id)
    user_votes = request.session.get('community_votes', {})
    answer_votes = request.session.get('community_answer_votes', {})

    return render(request, 'community/detail.html', {
        'post': post,
        'answers': post.answers.all(),
        'user_votes': user_votes,
        'answer_votes': answer_votes,
    })


@require_POST
def post_answer_view(request, post_id):
    """Add a solution or advice to a public community post, and alert the author!"""
    session_key = _ensure_session_key(request)
    post = get_object_or_404(CommunityPost, pk=post_id)

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            author_name = data.get('author_name', '').strip()
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        content = request.POST.get('content', '').strip()
        author_name = request.POST.get('author_name', '').strip()

    if not content:
        return JsonResponse({'error': 'Answer content cannot be empty'}, status=400)

    if request.user.is_authenticated:
        user = request.user
        if not author_name:
            author_name = getattr(request.user, 'full_name', '') or request.user.get_full_name() or request.user.username
        role = 'Farmer'
    else:
        user = None
        if not author_name:
            author_name = 'Fellow Farmer'
        role = 'Farmer'

    # Save answer
    answer = CommunityAnswer.objects.create(
        post=post,
        author=user,
        author_session_key=session_key,
        author_name=author_name,
        author_role=role,
        content=content
    )

    # Create Notification for the Post Author!
    notification = CommunityNotification.objects.create(
        recipient_user=post.author,
        recipient_session_key=post.author_session_key,
        recipient_name=post.author_name,
        post=post,
        answer=answer,
        actor_name=author_name,
        actor_role=role,
        title=f"New reply on: {post.title[:45]}",
        message=f"{author_name} shared a solution: \"{content[:140]}\""
    )

    exact_time_str = answer.created_at.strftime('%d %b %Y, %I:%M %p')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'answer': {
                'id': answer.id,
                'author_name': answer.author_name,
                'author_role': answer.author_role,
                'content': answer.content,
                'created_at': 'Just now',
                'exact_time': exact_time_str,
                'likes': 0,
                'is_verified': answer.is_verified_solution,
            },
            'answers_count': post.answers.count(),
            'notification_created': True
        })

    messages.success(request, 'Your answer was posted and the author has been notified!')
    return redirect(reverse('community:feed') + f'#post-{post.id}')


@require_POST
def post_vote_view(request, post_id):
    """Toggle like or dislike on a post (saved publicly in DB)."""
    post = get_object_or_404(CommunityPost, pk=post_id)
    action = request.POST.get('action') or 'like'

    user_votes = request.session.get('community_votes', {})
    current_vote = user_votes.get(str(post_id))

    if action == 'like':
        if current_vote == 'like':
            # Remove like
            post.likes = max(0, post.likes - 1)
            user_votes.pop(str(post_id), None)
            new_vote = None
        else:
            if current_vote == 'dislike':
                post.dislikes = max(0, post.dislikes - 1)
            post.likes += 1
            user_votes[str(post_id)] = 'like'
            new_vote = 'like'
    elif action == 'dislike':
        if current_vote == 'dislike':
            post.dislikes = max(0, post.dislikes - 1)
            user_votes.pop(str(post_id), None)
            new_vote = None
        else:
            if current_vote == 'like':
                post.likes = max(0, post.likes - 1)
            post.dislikes += 1
            user_votes[str(post_id)] = 'dislike'
            new_vote = 'dislike'
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    post.save(update_fields=['likes', 'dislikes'])
    request.session['community_votes'] = user_votes
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'likes': post.likes,
        'dislikes': post.dislikes,
        'current_vote': new_vote,
    })


@require_POST
def answer_vote_view(request, answer_id):
    """Toggle like on an answer/reply."""
    answer = get_object_or_404(CommunityAnswer, pk=answer_id)
    answer_votes = request.session.get('community_answer_votes', {})
    current_vote = answer_votes.get(str(answer_id))

    if current_vote == 'like':
        answer.likes = max(0, answer.likes - 1)
        answer_votes.pop(str(answer_id), None)
        new_vote = None
    else:
        answer.likes += 1
        answer_votes[str(answer_id)] = 'like'
        new_vote = 'like'

    answer.save(update_fields=['likes'])
    request.session['community_answer_votes'] = answer_votes
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'likes': answer.likes,
        'current_vote': new_vote
    })


def post_translate_view(request, post_id):
    """Translate post title and description to Hindi or requested language."""
    post = get_object_or_404(CommunityPost, pk=post_id)
    target_lang = request.GET.get('lang', 'hi').strip()

    translated_title = translate_text(post.title, target_lang)
    translated_desc = translate_text(post.description, target_lang)

    # Translate tags if present
    translated_tags = []
    for tag in post.get_tags():
        translated_tags.append(translate_text(tag, target_lang))

    lang_names = {'hi': 'हिन्दी (Hindi)', 'mr': 'मराठी (Marathi)', 'kn': 'ಕನ್ನಡ (Kannada)'}

    return JsonResponse({
        'success': True,
        'title': translated_title,
        'description': translated_desc,
        'tags': translated_tags,
        'target_lang': lang_names.get(target_lang, 'Hindi'),
        'original_title': post.title,
        'original_desc': post.description
    })


def notifications_api_view(request):
    """Fetch notifications for current user or session."""
    session_key = _ensure_session_key(request)

    if request.user.is_authenticated:
        user_notifs_qs = CommunityNotification.objects.filter(
            Q(recipient_user=request.user) | Q(recipient_session_key=session_key)
        )
    else:
        user_notifs_qs = CommunityNotification.objects.filter(recipient_session_key=session_key)

    unread_count = user_notifs_qs.filter(is_read=False).count()

    if user_notifs_qs.exists():
        notifs_to_show = list(user_notifs_qs[:15])
    else:
        notifs_to_show = list(CommunityNotification.objects.all()[:6])

    data = []
    for n in notifs_to_show:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'actor_name': n.actor_name,
            'actor_role': n.actor_role,
            'post_id': n.post.id,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d %b, %I:%M %p'),
            'timesince': n.created_at.strftime('%d %b %Y'),
        })

    return JsonResponse({
        'success': True,
        'notifications': data,
        'unread_count': unread_count
    })


@require_POST
def mark_notifications_read_view(request):
    """Mark all notifications as read."""
    session_key = _ensure_session_key(request)

    if request.user.is_authenticated:
        CommunityNotification.objects.filter(
            Q(recipient_user=request.user) | Q(recipient_session_key=session_key)
        ).update(is_read=True)
    else:
        CommunityNotification.objects.filter(recipient_session_key=session_key).update(is_read=True)

    return JsonResponse({'success': True, 'unread_count': 0})
