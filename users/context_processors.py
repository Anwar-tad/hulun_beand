from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        # ተጠቃሚው ተቀባይ የሆነባቸው እና is_read=False የሆኑ መልዕክቶችን መቁጠር
        count = Message.objects.filter(conversation__participants=request.user, is_read=False).exclude(sender=request.user).count()
        return {'unread_count': count}
    return {'unread_count': 0}