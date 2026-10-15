from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('signup/',             views.signup_view,   name='signup'),
    path('signin/',             views.signin_view,   name='signin'),
    path('signout/',            views.signout_view,  name='signout'),

    # Core pages
    path('',                    views.homepage,      name='homepage'),
    path('leaderboard/',        views.leaderboard,   name='leaderboard'),
    path('search/',             views.search_view,   name='search'),

    # Stories
    path('stories/<int:story_id>/',              views.story_detail,  name='story_detail'),
    path('stories/<int:story_id>/play/',         views.story_play,    name='story_play'),
    path('stories/<int:story_id>/choose/',       views.make_choice,   name='make_choice'),
    path('stories/<int:story_id>/rate/',         views.rate_story,    name='rate_story'),
    path('stories/<int:story_id>/delete/',       views.delete_story,  name='delete_story'),
    path('stories/create/',                      views.create_story,  name='create_story'),

    # Profiles
    path('profile/<str:username>/',              views.profile_view,  name='profile'),
    path('profile/edit/me/',                     views.edit_profile,  name='edit_profile'),

    # API
    path('api/node/<int:node_id>/',              views.api_node,      name='api_node'),
]
