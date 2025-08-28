from django import template

register = template.Library()

@register.filter
def get_other_participant(participants, current_user):
    """
    Given a list of participants in a conversation,
    this filter returns the participant who is NOT the current user.
    """
    for participant in participants:
        if participant != current_user:
            return participant
    return None # Should not happen in a two-person conversation
  # users/templatetags/user_filters.py

@register.filter
def get_other_participant(participants, current_user):
    for participant in participants:
        if participant != current_user:
            return participant
    return None

# --- ADD THIS NEW FUNCTION ---
@register.filter
def get_model_field_verbose_name(instance, field_name):
    """
    Returns the verbose_name for a given model's field.
    Usage: {{ product|get_model_field_verbose_name:'category' }}
    """
    return instance._meta.get_field(field_name).verbose_name