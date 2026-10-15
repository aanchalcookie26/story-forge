from django import forms
from django.contrib.auth.models import User
from .models import UserAccount, Story, Rating, GENRE_CHOICES


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Choose a username', 'autocomplete': 'username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'autocomplete': 'email'})
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Min 6 characters', 'autocomplete': 'new-password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password', 'autocomplete': 'new-password'})
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('That username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class SignInForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'current-password'})
    )


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'genre', 'cover_emoji', 'description', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Your story title...'}),
            'cover_emoji': forms.TextInput(attrs={'placeholder': '🐉', 'maxlength': '4'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'A compelling teaser for your readers (2-3 sentences)...',
                'rows': 3
            }),
        }

    def clean_cover_emoji(self):
        emoji = self.cleaned_data.get('cover_emoji', '').strip()
        return emoji if emoji else '📖'


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars']
        widgets = {
            'stars': forms.HiddenInput(),
        }


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell readers about yourself...'}),
    )
    avatar_emoji = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '📖', 'maxlength': '4'}),
    )

    class Meta:
        model = UserAccount
        fields = ['bio', 'avatar_emoji']


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search stories, authors, genres...', 'autocomplete': 'off'})
    )
    genre = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genres')] + list(GENRE_CHOICES)
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('popular',  'Most Popular'),
            ('rating',   'Highest Rated'),
            ('newest',   'Newest First'),
            ('oldest',   'Oldest First'),
        ]
    )
