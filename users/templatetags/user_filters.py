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