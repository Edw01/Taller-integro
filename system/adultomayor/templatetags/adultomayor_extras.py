from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.filter
def has_profile(user):
    try:
        return hasattr(user, 'profile') and user.profile is not None
    except ObjectDoesNotExist:
        return False
