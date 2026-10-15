from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=256)
    bio = models.TextField(blank=True, default='')
    avatar_emoji = models.CharField(max_length=10, default='📖')
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username

    def stories_written(self):
        return Story.objects.filter(author=self.user).count()

    def stories_played(self):
        return PlaySession.objects.filter(user=self.user).values('story').distinct().count()


GENRE_CHOICES = [
    ('fantasy',   'Fantasy'),
    ('scifi',     'Sci-Fi'),
    ('mystery',   'Mystery'),
    ('horror',    'Horror'),
    ('adventure', 'Adventure'),
    ('romance',   'Romance'),
    ('thriller',  'Thriller'),
    ('comedy',    'Comedy'),
]


class Story(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='fantasy')
    cover_emoji = models.CharField(max_length=10, default='📖')
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    start_node = models.ForeignKey(
        'Node', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='starting_story'
    )
    is_published = models.BooleanField(default=False)
    play_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'stories'

    def __str__(self):
        return self.title

    def average_rating(self):
        ratings = self.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.stars for r in ratings) / ratings.count(), 1)

    def rating_count(self):
        return self.ratings.count()

    def node_count(self):
        return self.nodes.count()

    def ending_count(self):
        return self.nodes.filter(is_ending=True).count()

    def good_endings(self):
        return self.nodes.filter(is_ending=True, ending_type='good').count()

    def get_genre_display_icon(self):
        icons = {
            'fantasy': '🐉', 'scifi': '🛸', 'mystery': '🔍',
            'horror': '👻', 'adventure': '🗺️', 'romance': '💌',
            'thriller': '🔐', 'comedy': '😂',
        }
        return icons.get(self.genre, '📖')


class Node(models.Model):
    ENDING_TYPES = [
        ('good',    'Good Ending'),
        ('bad',     'Bad Ending'),
        ('neutral', 'Neutral Ending'),
        ('',        'Not an Ending'),
    ]
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='nodes')
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_ending = models.BooleanField(default=False)
    ending_type = models.CharField(max_length=20, choices=ENDING_TYPES, default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.story.title}] {self.title or 'Node ' + str(self.order)}"

    def get_choices(self):
        return self.choices.all().order_by('order')


class Choice(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    next_node = models.ForeignKey(
        Node, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='incoming_choices'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.choice_text[:60]}..."


class Rating(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('story', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.story.title}: {self.stars}★"


class PlaySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='play_sessions')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='play_sessions')
    current_node = models.ForeignKey(
        Node, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='active_sessions'
    )
    started_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    ending_type = models.CharField(max_length=20, blank=True, default='')
    steps_taken = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.user.username} playing {self.story.title}"
