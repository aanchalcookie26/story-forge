from django import template

register = template.Library()


@register.filter
def round1(value):
    """Round a number to 1 decimal place. Returns '—' if None/falsy."""
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "—"


@register.filter
def stars_display(value):
    """Return a rating as a star string e.g. ★ 4.7"""
    try:
        return f"★ {float(value):.1f}"
    except (TypeError, ValueError):
        return "★ —"

