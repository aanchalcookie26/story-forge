from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password
import json

from .models import Story, Node, Choice, Rating, UserAccount, PlaySession, GENRE_CHOICES
from .forms import SignUpForm, SignInForm, StoryForm, RatingForm, ProfileForm, SearchForm


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
        )
        UserAccount.objects.create(
            user=user,
            username=data['username'],
            email=data['email'],
            hashed_password=make_password(data['password']),
        )
        login(request, user)
        messages.success(request, f"Welcome to StoryForge, {user.username}! 🎉")
        return redirect('homepage')
    return render(request, 'stories/signup.html', {'form': form})


def signin_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    form = SignInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! 📖")
            return redirect(request.GET.get('next', 'homepage'))
        else:
            form.add_error(None, 'Invalid username or password.')
    return render(request, 'stories/signin.html', {'form': form})


def signout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('signin')


# ─── HOMEPAGE & LEADERBOARD ───────────────────────────────────────────────────

def homepage(request):
    published = Story.objects.filter(is_published=True)
    top_stories = published.annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings'),
    ).order_by('-play_count')[:6]

    newest = published.order_by('-created_at')[:4]
    genre_list = GENRE_CHOICES

    # Pick one featured story (highest play count)
    featured = published.order_by('-play_count').first()

    ctx = {
        'top_stories': top_stories,
        'newest': newest,
        'genre_list': genre_list,
        'featured': featured,
    }
    return render(request, 'stories/homepage.html', ctx)


def leaderboard(request):
    genre_filter = request.GET.get('genre', '')
    stories = Story.objects.filter(is_published=True)
    if genre_filter:
        stories = stories.filter(genre=genre_filter)

    stories = stories.annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings'),
    ).order_by('-play_count')

    ctx = {
        'stories': stories,
        'genre_list': GENRE_CHOICES,
        'selected_genre': genre_filter,
    }
    return render(request, 'stories/leaderboard.html', ctx)


# ─── STORY DETAIL & PLAY ──────────────────────────────────────────────────────

def story_detail(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    if not story.is_published and story.author != request.user:
        messages.error(request, 'This story is not published yet.')
        return redirect('homepage')

    avg = story.average_rating()
    user_rating = None
    user_session = None

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(story=story, user=request.user).first()
        user_session = PlaySession.objects.filter(
            user=request.user, story=story, completed=False
        ).order_by('-last_updated').first()

    recent_ratings = story.ratings.select_related('user').order_by('-created_at')[:5]

    ctx = {
        'story': story,
        'avg': avg,
        'user_rating': user_rating,
        'user_session': user_session,
        'recent_ratings': recent_ratings,
        'node_count': story.node_count(),
        'ending_count': story.ending_count(),
    }
    return render(request, 'stories/story_detail.html', ctx)


@login_required
def story_play(request, story_id):
    story = get_object_or_404(Story, pk=story_id, is_published=True)

    # Resume or start fresh
    node_id = request.GET.get('node')
    session_id = request.GET.get('session')

    session = None
    if session_id:
        session = PlaySession.objects.filter(pk=session_id, user=request.user, story=story).first()

    if node_id:
        node = get_object_or_404(Node, pk=node_id, story=story)
    elif session and session.current_node:
        node = session.current_node
    else:
        # Fresh start
        node = story.start_node
        story.play_count += 1
        story.save(update_fields=['play_count'])

    if not session:
        session = PlaySession.objects.create(
            user=request.user,
            story=story,
            current_node=node,
        )
    else:
        session.current_node = node
        session.steps_taken += 1
        session.save(update_fields=['current_node', 'steps_taken', 'last_updated'])

    choices = node.get_choices()

    if node.is_ending:
        session.completed = True
        session.ending_type = node.ending_type
        session.save(update_fields=['completed', 'ending_type', 'last_updated'])

    # Progress calculation
    total_nodes = story.node_count()
    progress = min(100, int((session.steps_taken / max(total_nodes, 1)) * 100))

    ctx = {
        'story': story,
        'node': node,
        'choices': choices,
        'session': session,
        'progress': progress,
    }
    return render(request, 'stories/story_play.html', ctx)


@login_required
@require_POST
def make_choice(request, story_id):
    story = get_object_or_404(Story, pk=story_id, is_published=True)
    choice_id = request.POST.get('choice_id')
    session_id = request.POST.get('session_id')

    choice = get_object_or_404(Choice, pk=choice_id)
    if not choice.next_node:
        messages.error(request, 'This path leads nowhere — the story has a gap.')
        return redirect('story_play', story_id=story_id)

    url = f"/stories/{story_id}/play/?node={choice.next_node.pk}&session={session_id}"
    return redirect(url)


# ─── RATING ───────────────────────────────────────────────────────────────────

@login_required
@require_POST
def rate_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    stars = int(request.POST.get('stars', 5))
    stars = max(1, min(5, stars))

    rating, created = Rating.objects.update_or_create(
        story=story, user=request.user,
        defaults={'stars': stars}
    )
    action = 'submitted' if created else 'updated'
    messages.success(request, f'Rating {action}! You gave {story.title} {stars}★')
    return redirect('story_detail', story_id=story_id)


# ─── SEARCH ───────────────────────────────────────────────────────────────────

def search_view(request):
    form = SearchForm(request.GET or None)
    stories = Story.objects.filter(is_published=True)
    query = ''

    if form.is_valid():
        q = form.cleaned_data.get('q', '').strip()
        genre = form.cleaned_data.get('genre', '')
        sort = form.cleaned_data.get('sort', 'popular')
        query = q

        if q:
            stories = stories.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(author__username__icontains=q) |
                Q(genre__icontains=q)
            )
        if genre:
            stories = stories.filter(genre=genre)

        stories = stories.annotate(
            avg_rating=Avg('ratings__stars'),
            rating_count=Count('ratings'),
        )

        sort_map = {
            'popular': '-play_count',
            'rating':  '-avg_rating',
            'newest':  '-created_at',
            'oldest':  'created_at',
        }
        stories = stories.order_by(sort_map.get(sort, '-play_count'))
    else:
        stories = stories.annotate(
            avg_rating=Avg('ratings__stars'),
            rating_count=Count('ratings'),
        ).order_by('-play_count')

    ctx = {
        'form': form,
        'stories': stories,
        'query': query,
        'result_count': stories.count(),
    }
    return render(request, 'stories/search.html', ctx)


# ─── PROFILE ──────────────────────────────────────────────────────────────────

def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    try:
        account = target_user.account
    except UserAccount.DoesNotExist:
        account = None

    user_stories = Story.objects.filter(
        author=target_user, is_published=True
    ).annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings'),
    ).order_by('-play_count')

    sessions = PlaySession.objects.filter(
        user=target_user, completed=True
    ).select_related('story').order_by('-last_updated')[:10]

    ctx = {
        'target_user': target_user,
        'account': account,
        'user_stories': user_stories,
        'sessions': sessions,
        'is_own_profile': request.user == target_user,
    }
    return render(request, 'stories/profile.html', ctx)


@login_required
def edit_profile(request):
    account, _ = UserAccount.objects.get_or_create(
        user=request.user,
        defaults={
            'username': request.user.username,
            'email': request.user.email,
            'hashed_password': '',
        }
    )
    form = ProfileForm(request.POST or None, instance=account)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile', username=request.user.username)
    return render(request, 'stories/edit_profile.html', {'form': form, 'account': account})


# ─── STORY MANAGEMENT ─────────────────────────────────────────────────────────

@login_required
def create_story(request):
    form = StoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        story = form.save(commit=False)
        story.author = request.user
        story.save()
        messages.success(request, f'Story "{story.title}" created! Now add your nodes.')
        return redirect('story_detail', story_id=story.pk)
    return render(request, 'stories/create_story.html', {'form': form})


@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id, author=request.user)
    if request.method == 'POST':
        title = story.title
        story.delete()
        messages.success(request, f'"{title}" has been deleted.')
        return redirect('profile', username=request.user.username)
    return render(request, 'stories/confirm_delete.html', {'story': story})


# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

def api_node(request, node_id):
    """Return node data as JSON for the animated reader."""
    node = get_object_or_404(Node, pk=node_id)
    choices = [
        {'id': c.pk, 'text': c.choice_text, 'next_node_id': c.next_node_id}
        for c in node.get_choices()
    ]
    return JsonResponse({
        'id': node.pk,
        'title': node.title,
        'text': node.text,
        'is_ending': node.is_ending,
        'ending_type': node.ending_type,
        'choices': choices,
        'story_emoji': node.story.cover_emoji,
        'story_title': node.story.title,
    })


def error_404(request, exception=None):
    return render(request, 'stories/error.html', {'code': 404, 'msg': 'Page not found'}, status=404)


def error_500(request):
    return render(request, 'stories/error.html', {'code': 500, 'msg': 'Server error'}, status=500)
