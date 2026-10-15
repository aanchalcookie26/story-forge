# StoryForge — Interactive Branching Fiction Platform

## Quick Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Install Django
pip install django

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Seed all 8 stories
python manage.py seed_stories

# 5. Start the server
python manage.py runserver
```

Then open http://127.0.0.1:8000

**Admin panel:** http://127.0.0.1:8000/admin/
**Login:** Create a local administrator using Django's `createsuperuser` command.

---

## Project Structure

```
storyforge/
├── manage.py
├── README.md
├── db.sqlite3                  (created after migrate)
├── storyforge/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── stories/
│   ├── models.py               Story, Node, Choice, Rating, UserAccount, PlaySession
│   ├── views.py                All views
│   ├── forms.py                All forms
│   ├── urls.py                 URL routes
│   ├── admin.py                Admin panel
│   ├── apps.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           └── seed_stories.py 8 stories × 12-18 chapters each
├── templates/
│   ├── base.html               Master layout — navbar, particles, footer
│   └── stories/
│       ├── homepage.html       Hero, featured story, genre grid, top stories
│       ├── story_detail.html   Cover, stats, rating stars, reviews, sidebar
│       ├── story_play.html     Animated typewriter reader, progress bar, choices
│       ├── leaderboard.html    Ranked table with genre filter tabs
│       ├── search.html         Full-text search with genre + sort filters
│       ├── signin.html
│       ├── signup.html
│       ├── profile.html        Author bio, stories written, adventures completed
│       ├── edit_profile.html
│       ├── create_story.html
│       ├── confirm_delete.html
│       └── error.html          404 / 500
└── static/
    └── css/
        └── extra.css           Utility classes (shimmer, fade-in, spinner, tooltip)
```

---

## Key Features

| Feature | Detail |
|---------|--------|
| Animated Reader | Typewriter text reveal, ember particles, scene transitions |
| Progress Bar | Tracks chapter progress through the story |
| Branching Stories | 10–20 chapters, multiple endings (good / neutral / bad) |
| Session Resume | Readers can pause and resume any playthrough |
| Star Ratings | 5-star system, per-user, shown on detail + ending screen |
| Leaderboard | Ranked by plays, filterable by genre |
| Search | Full-text + genre + sort (plays, rating, date) |
| Profiles | Avatar emoji, bio, stories written, adventures completed |
| Admin Panel | Full CRUD for stories, nodes, choices, ratings |

---

## Seeded Stories (8 genres)

| Genre | Title | Chapters |
|-------|-------|---------|
| 🐉 Fantasy | The Dragon's Pact | 23 nodes |
| 🛸 Sci-Fi | Signal from Kepler-7 | 10 nodes |
| 🔍 Mystery | The Clockmaker's Last Hour | 12 nodes |
| 🏚️ Horror | The House on Morrow Lane | 13 nodes |
| 😂 Comedy | The Worst Wizard's Apprentice | 16 nodes |
| 🔐 Thriller | The Protocol | 9 nodes |
| 🗺️ Adventure | Lost City of the Sun Priests | 7 nodes |
| 🚂 Romance | Last Train to Somewhere | 11 nodes |

---

## URL Map

| URL | Name | View |
|-----|------|------|
| `/` | homepage | Homepage |
| `/leaderboard/` | leaderboard | Leaderboard |
| `/search/` | search | Browse/Search |
| `/signup/` | signup | Register |
| `/signin/` | signin | Login |
| `/signout/` | signout | Logout |
| `/stories/<id>/` | story_detail | Story detail page |
| `/stories/<id>/play/` | story_play | Animated reader |
| `/stories/<id>/choose/` | make_choice | POST: advance story |
| `/stories/<id>/rate/` | rate_story | POST: submit rating |
| `/stories/<id>/delete/` | delete_story | Delete (author only) |
| `/stories/create/` | create_story | New story form |
| `/profile/<username>/` | profile | User profile |
| `/profile/edit/me/` | edit_profile | Edit own profile |
| `/api/node/<id>/` | api_node | JSON node data |
| `/admin/` | — | Django admin |

