from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def attendant_display_name(user):
    """Get formatted display name for attendant: 'Attendant X - First Last'"""
    if not user:
        return ""
    # Extract number from username (e.g., 'attendant1' -> 1)
    match = re.search(r'attendant(\d+)', user.username.lower())
    if match:
        number = match.group(1)
        name = user.get_full_name() or user.username
        return f"Attendant {number} - {name}"
    # Fallback if username doesn't match pattern
    return user.get_full_name() or user.username

