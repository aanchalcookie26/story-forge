from django.contrib import admin
from .models import Story, Node, Choice, Rating, UserAccount, PlaySession


class ChoiceInline(admin.TabularInline):
    model = Choice
    fk_name = 'node'
    extra = 2
    fields = ['choice_text', 'next_node', 'order']


class NodeInline(admin.TabularInline):
    model = Node
    extra = 0
    fields = ['title', 'order', 'is_ending', 'ending_type']
    show_change_link = True


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'author', 'is_published', 'play_count', 'node_count', 'average_rating', 'created_at']
    list_filter = ['genre', 'is_published']
    search_fields = ['title', 'author__username']
    list_editable = ['is_published']
    inlines = [NodeInline]
    readonly_fields = ['play_count', 'created_at', 'updated_at']


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'story', 'order', 'is_ending', 'ending_type']
    list_filter = ['is_ending', 'ending_type', 'story']
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'node', 'next_node', 'order']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'stars', 'created_at']
    list_filter = ['stars']


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'joined_at']


@admin.register(PlaySession)
class PlaySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'story', 'completed', 'ending_type', 'steps_taken', 'last_updated']
    list_filter = ['completed', 'ending_type']
